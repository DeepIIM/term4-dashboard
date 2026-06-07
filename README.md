# Term-IV Course Dashboard + Email Reminders

Dark-themed personal dashboard + automated nightly email reminders for your Term-IV schedule.

---

## What's Included

| Component | Description |
|---|---|
| `dashboard/index.html` | Dark-themed web dashboard with calendar, course cards, clash report |
| `dashboard/courses.json` | Your extracted timetable data (9 courses, 95 sessions) |
| `scripts/send_reminder.py` | Sends nightly HTML email with tomorrow's classes |
| `.github/workflows/daily-reminder.yml` | GitHub Actions cron — runs daily at 21:00 IST |

---

## Your Courses (20 Credits)

| # | Course | Cr | Ends |
|---|--------|:---:|---|
| CCR-A | Communicating Corporate Reputation | 2 | Aug 5 |
| ACEL-A | Advanced Corporate & Economic Laws | 2 | Jul 30 |
| GAIB | Generative AI in Business | 2 | Jul 17 |
| TSB-A | Technology Strategy for Business | 2 | Jul 8 |
| GAFW-A | Gen AI and Future of Work | 1 | Jul 9 |
| MSN | Managing Social Networks | 2 | Jul 24 |
| CEDA-A | Corporate Entrepreneurship | 3 | Aug 8 |
| M&A | Mergers and Acquisitions | 3 | Aug 7 |
| SS-G | Strategy Simulation | 3 | Jul 20 |

**Clashes:** 5 total — 4 manageable, 1 rigid (MSN × SS-G)

---

## Quick Start

### 1. Resend Setup (for Email)

1. Go to [resend.com](https://resend.com) and create a free account
2. Verify your domain OR use the default `onboarding@resend.dev` sender
3. Go to **API Keys** → Create an API key
4. Copy the key — you'll need it in step 3

### 2. Deploy Dashboard to GitHub Pages

1. Push this repo to GitHub
2. Go to **Settings → Pages**
3. Source: **Deploy from a branch** → Select `main` → Folder `/ (root)`
4. Your dashboard will be live at `https://yourusername.github.io/repo-name/dashboard/`

### 3. Configure GitHub Secrets (for Email)

In your GitHub repo:
1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add `RESEND_API_KEY` = your Resend API key
4. Add `EMAIL_TO` = your email address

Done! The GitHub Actions workflow will run every day at 21:00 IST and email you tomorrow's schedule.

---

## Manual Testing

Want to test the email before waiting for the cron?

```bash
# Set env vars temporarily
export RESEND_API_KEY="re_your_key"
export EMAIL_TO="you@example.com"

# Run the script
python scripts/send_reminder.py
```

Or trigger the workflow manually:
1. Go to **Actions → Daily Course Reminder**
2. Click **Run workflow**

---

## Dashboard Features

- **Live clock & date**
- **Term progress bar** — visual % of term complete
- **Today's schedule** — card view of today's classes with attendance buttons
- **Course cards** — progress bars, faculty, credits, sister section status, **attendance % per course**
- **Clash report** — rigid clashes in red, manageable in yellow
- **Weekly calendar** — visual grid with color-coded blocks + attendance dots
- **Full timetable** — sortable table of all 95 sessions with **attendance toggle buttons**
- **Attendance tracker** — mark any session as Present ✓ / Absent ✗. Persisted in browser localStorage
- **Export attendance** — download your attendance data as JSON
- **CFA countdown** — days left until Aug 19 exam
- **Mobile responsive** — works on phone browsers

---

## Tech Stack

- **Frontend:** Vanilla HTML + Tailwind CSS CDN (no build step)
- **Data:** Static JSON extracted from official Excel timetable
- **Email:** Resend API (free tier: 100 emails/day)
- **Scheduler:** GitHub Actions cron (free)
- **Hosting:** GitHub Pages (free)

---

## Attendance Tracker

The dashboard includes a built-in attendance tracker:

1. **Mark attendance** for any session via the timetable or today's schedule
2. **Present** = green ✓ | **Absent** = red ✗ | **Not marked** = gray
3. **Course cards** show real-time attendance % for each course
4. **Hero stat** shows overall attendance rate across all courses
5. **Calendar blocks** show a small dot indicating attendance status
6. **Export** your attendance data as JSON anytime
7. **Reset** clears all attendance history

> All attendance data is stored in your browser's `localStorage` — it stays private and persists between visits.

---

*Built for PGP 2025-27 Term-IV*
