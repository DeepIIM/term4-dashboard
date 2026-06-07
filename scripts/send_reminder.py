"""
Daily Course Reminder Email Sender
Reads courses.json and sends an HTML email with tomorrow's schedule.
Designed to run via GitHub Actions cron or locally.

Environment variables:
  RESEND_API_KEY  - Your Resend API key
  EMAIL_TO        - Your email address
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Try to import resend, fallback to requests
try:
    import resend
    HAS_RESEND_SDK = True
except ImportError:
    HAS_RESEND_SDK = False
    import requests


def load_courses():
    script_dir = Path(__file__).parent.resolve()
    json_path = script_dir.parent / "courses.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_tomorrow_sessions(data):
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    sessions = []
    for course in data["courses"]:
        for s in course["sessions"]:
            if s["date"] == tomorrow:
                sessions.append({**s, "course": course})
    sessions.sort(key=lambda x: x["slot"])
    return tomorrow, sessions


def find_clashes(sessions):
    """Find slot overlaps among tomorrow's sessions and suggest sister sections."""
    clashes = []
    for i in range(len(sessions)):
        for j in range(i + 1, j_limit := len(sessions)):
            if sessions[i]["slot"] == sessions[j]["slot"]:
                a = sessions[i]["course"]
                b = sessions[j]["course"]
                has_sister_a = a.get("sisterAllowed") and a.get("sisterSection")
                has_sister_b = b.get("sisterAllowed") and b.get("sisterSection")
                
                # Check known clash metadata
                known = None
                if "clashes" in sessions[i].get("__data", {}).get("clashes", []):
                    pass  # handled below
                
                clashes.append({
                    "sessionA": sessions[i],
                    "sessionB": sessions[j],
                    "hasSisterA": has_sister_a,
                    "hasSisterB": has_sister_b,
                    "rigid": not (has_sister_a or has_sister_b),
                })
    return clashes


def get_sister_suggestion(clash):
    """Return human-readable clash suggestion."""
    session_a = clash["sessionA"]
    session_b = clash["sessionB"]
    has_sister_a = clash["hasSisterA"]
    has_sister_b = clash["hasSisterB"]
    rigid = clash["rigid"]

    if rigid:
        return f"<strong style='color:#f87171'>&#9888; Rigid clash:</strong> No sister section available. You must miss one class."

    suggestions = []
    if has_sister_a:
        sister = session_a["course"]["sisterSection"]
        sister_sess = next(
            (s for s in sister["sessions"] if s["sessionNum"] == session_a["sessionNum"]),
            None,
        )
        if sister_sess:
            suggestions.append(
                f"Attend <strong>{sister['code']}</strong> instead of {session_a['course']['code']} "
                f"({sister_sess['time']}, {sister_sess['classroom']})"
            )
    if has_sister_b:
        sister = session_b["course"]["sisterSection"]
        sister_sess = next(
            (s for s in sister["sessions"] if s["sessionNum"] == session_b["sessionNum"]),
            None,
        )
        if sister_sess:
            suggestions.append(
                f"Attend <strong>{sister['code']}</strong> instead of {session_b['course']['code']} "
                f"({sister_sess['time']}, {sister_sess['classroom']})"
            )

    if not suggestions:
        return f"<strong style='color:#fbbf24'>&#9888; Clash:</strong> Sister section allowed but schedule data unavailable."

    return (
        f"<strong style='color:#fbbf24'>&#128161; Suggestion:</strong> "
        f"<span style='color:#fde68a'>{' OR '.join(suggestions)}</span>"
    )


def format_date(date_str):
    d = datetime.fromisoformat(date_str)
    return d.strftime("%A, %B %d, %Y")


def build_email_html(tomorrow_str, sessions, data):
    date_display = format_date(tomorrow_str)

    if not sessions:
        body_content = """
        <div style="text-align:center; padding: 40px 0;">
          <div style="font-size: 48px; margin-bottom: 16px;">&#127881;</div>
          <h2 style="color: #e2e8f0; margin: 0;">No classes tomorrow!</h2>
          <p style="color: #94a3b8; margin-top: 8px;">Enjoy your day off. Maybe catch up on CFA prep?</p>
        </div>
        """
    else:
        # Detect clashes
        clashes = find_clashes(sessions)
        clash_session_keys = set()
        for c in clashes:
            clash_session_keys.add((c["sessionA"]["course"]["code"], c["sessionA"]["slot"]))
            clash_session_keys.add((c["sessionB"]["course"]["code"], c["sessionB"]["slot"]))

        rows = []
        for s in sessions:
            c = s["course"]
            is_clash = (c["code"], s["slot"]) in clash_session_keys
            clash_html = ""

            if is_clash:
                my_clash = next(
                    cl
                    for cl in clashes
                    if (cl["sessionA"]["course"]["code"] == c["code"] and cl["sessionA"]["slot"] == s["slot"])
                    or (cl["sessionB"]["course"]["code"] == c["code"] and cl["sessionB"]["slot"] == s["slot"])
                )
                suggestion = get_sister_suggestion(my_clash)
                clash_html = f'<div style="margin-top: 8px; padding: 8px 10px; border-radius: 8px; background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.2); font-size: 12px; line-height: 1.5;">{suggestion}</div>'

            rows.append(f"""
            <tr>
              <td style="padding: 14px 16px; border-bottom: 1px solid #1e293b; vertical-align: top;">
                <div style="font-size: 18px; font-weight: 700; color: #e2e8f0;">{s["time"]}</div>
                <div style="font-size: 12px; color: #64748b;">{s["day"]} &#8226; {s["classroom"]}</div>
              </td>
              <td style="padding: 14px 16px; border-bottom: 1px solid #1e293b; vertical-align: top;">
                <div style="font-size: 15px; font-weight: 600; color: #e2e8f0;">{c["name"]}</div>
                <div style="font-size: 13px; color: #94a3b8;">{c["faculty"]}</div>
                {clash_html}
              </td>
            </tr>
            """)

        body_content = f"""
        <p style="color: #94a3b8; margin-bottom: 24px;">You have <strong style="color: #e2e8f0;">{len(sessions)}</strong> class session(s) scheduled.</p>
        <table style="width: 100%; border-collapse: collapse;">
          <tbody>
            {"" .join(rows)}
          </tbody>
        </table>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #0f172a; font-family: 'Segoe UI', system-ui, sans-serif;">
      <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
          <td align="center" style="padding: 40px 20px;">
            <table role="presentation" style="max-width: 600px; width: 100%; background: #1e293b; border-radius: 16px; border: 1px solid #334155; overflow: hidden;">

              <!-- Header -->
              <tr>
                <td style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 32px 24px; text-align: center;">
                  <div style="font-size: 32px; margin-bottom: 8px;">&#128197;</div>
                  <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700;">Tomorrow's Classes</h1>
                  <p style="color: rgba(255,255,255,0.8); margin: 6px 0 0; font-size: 15px;">{date_display}</p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="padding: 24px;">
                  {body_content}
                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="padding: 20px 24px; border-top: 1px solid #1e293b; text-align: center;">
                  <p style="color: #475569; font-size: 12px; margin: 0;">
                    Term-IV Dashboard &#8226; PGP 2025-27
                  </p>
                  <p style="color: #334155; font-size: 11px; margin: 4px 0 0;">
                    Sent automatically at 9:00 PM IST
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
    return html


def send_email(subject, html_body, to_email, api_key):
    sender = "onboarding@resend.dev"  # Resend default sender for unverified domains

    if HAS_RESEND_SDK:
        resend.api_key = api_key
        params = {
            "from": sender,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }
        try:
            response = resend.Emails.send(params)
            print(f"Email sent! ID: {response.get('id', 'unknown')}")
            return True
        except Exception as e:
            print(f"Failed to send email via Resend SDK: {e}")
            return False
    else:
        # Fallback to direct API call
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": sender,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            print(f"Email sent! ID: {response.json().get('id', 'unknown')}")
            return True
        except Exception as e:
            print(f"Failed to send email via API: {e}")
            return False


def main():
    api_key = os.environ.get("RESEND_API_KEY")
    to_email = os.environ.get("EMAIL_TO")

    if not api_key:
        print("ERROR: RESEND_API_KEY environment variable not set.")
        print("Get your API key from https://resend.com/api-keys")
        sys.exit(1)

    if not to_email:
        print("ERROR: EMAIL_TO environment variable not set.")
        sys.exit(1)

    data = load_courses()
    tomorrow_str, sessions = get_tomorrow_sessions(data)

    # Log clash info
    clashes = find_clashes(sessions)
    if clashes:
        print(f"\nDetected {len(clashes)} clash(es) tomorrow:")
        for c in clashes:
            a = c["sessionA"]["course"]["code"]
            b = c["sessionB"]["course"]["code"]
            print(f"  {a} x {b} (slot {c['sessionA']['slot']}) - {'RIGID' if c['rigid'] else 'Manageable'}")

    print(f"\nTomorrow ({tomorrow_str}): {len(sessions)} session(s)")
    for s in sessions:
        print(f"  {s['time']} - {s['course']['code']} - {s['course']['name']}")

    html_body = build_email_html(tomorrow_str, sessions, data)
    subject = f"📅 Tomorrow's Classes — {format_date(tomorrow_str)}"

    success = send_email(subject, html_body, to_email, api_key)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
