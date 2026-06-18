# Term-IV Course Dashboard + Email Reminders

Dark-themed personal dashboard + automated nightly email reminders for your Term-IV schedule. Now with **clash resolution suggestions** and **customizable course bundles** for you and your friends.

---

## What's Included

| Component | Description |
|---|---|
| `index.html` | Dark-themed web dashboard with calendar, course cards, clash report, course picker |
| `courses.json` | Your extracted timetable data (9 courses, 95 sessions) with sister section data |
| `all_courses.json` | Full timetable data for ALL 105 course-sections (for course picker) |
| `scripts/send_reminder.py` | Sends nightly HTML email with tomorrow's schedule + clash suggestions |
| `.github/workflows/daily-reminder.yml` | GitHub Actions cron — runs daily around 21:00 IST (see timing note below) |

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

**Clashes:** 1 total — 1 rigid (CCR × M&A)

---

## Features

### Dashboard
- **Live clock & date**
- **Term progress bar** — visual % of term complete
- **Today's / Tomorrow's schedule** — with clash detection and sister section suggestions
- **Course cards** — progress bars, faculty, credits, sister section status, attendance %
- **Clash resolution** — when clashes detected, dashboard suggests attending sister section (e.g., "Attend TSB-B instead")
- **Weekly calendar** — visual grid with color-coded blocks + attendance dots + clash warnings
- **Full timetable** — sortable table of all sessions with attendance toggle buttons
- **Attendance tracker** — mark any session as Present ✓ / Absent ✗. Persisted in browser localStorage
- **Export attendance** — download your attendance data as JSON
- **CFA countdown** — days left until Aug 19 exam
- **Mobile responsive** — works on phone browsers

### Customizable Bundle (For Friends)
- Click **⚙️ Bundle** in the navbar
- Select any courses from the full Term-IV catalog
- Dashboard instantly updates to your selected courses
- Attendance data is separate per bundle (no overwriting)
- **Reset to Default** anytime

### Email Reminders
- Daily at 21:00 IST, get an email with tomorrow's schedule
- **Clash warnings** with sister section suggestions
- **Rigid clash alerts** when no workaround exists

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
4. Your dashboard will be live at `https://yourusername.github.io/repo-name/`

### 3. Configure GitHub Secrets (for Email)

In your GitHub repo:
1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add `RESEND_API_KEY` = your Resend API key
4. Add `EMAIL_TO` = your email address
5. Add `COURSES_JSON` = your personal course bundle JSON (see below)

Done! The GitHub Actions workflow will run every day around 21:00 IST and email you tomorrow's schedule.

**Why `COURSES_JSON` is required:**  
The email script needs YOUR personal course bundle, not the shared `courses.json` file in the repo. Storing it as a GitHub Secret keeps it private and ensures that if a friend forks your repo, they only receive emails for their own courses (once they add their own `COURSES_JSON` secret).

**How to get your `COURSES_JSON`:**
1. Open your live dashboard and pick your courses in the bundle picker
2. Open browser DevTools → Console and run:
   ```js
   copy(localStorage.getItem('term4_bundle'))
   ```
3. Paste the copied JSON into the `COURSES_JSON` secret value field

---

## Friend Setup Guide

Want a friend to use this dashboard for their own courses? Here's how:

### Option A: Share the Live Dashboard (No Email)

1. Share your GitHub Pages URL with them
2. They click **⚙️ Bundle** and select their own courses
3. Their selections are saved in their browser only
4. They get their own timetable, attendance tracking, etc.

> **Note:** The course picker needs the dashboard to be hosted (not opened via `file://`). If running locally, use `python -m http.server` and open `localhost:8000`.

### Option B: Full Setup With Email Reminders

1. **Friend forks this repo** on GitHub
2. They go to the live dashboard (their fork's GitHub Pages URL)
3. They click **⚙️ Bundle** → select their courses → **Save Bundle**
4. They export their bundle: open browser DevTools → Console → run:
   ```js
   copy(localStorage.getItem('term4_bundle'))
   ```
5. They add their own GitHub Secrets:
   - `COURSES_JSON` — paste the copied JSON from step 4
   - `RESEND_API_KEY` — their Resend API key
   - `EMAIL_TO` — their email address
6. They enable GitHub Actions in their fork
7. Daily emails now work for their bundle!

> **Important:** The email script reads from the `COURSES_JSON` secret, not from `courses.json`. If `COURSES_JSON` is missing, the workflow will fail with instructions instead of accidentally sending the original owner's timetable.

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

## Tech Stack

- **Frontend:** Vanilla HTML + Tailwind CSS CDN (no build step)
- **Data:** Static JSON extracted from official Excel timetable
- **Email:** Resend API (free tier: 100 emails/day)
- **Scheduler:** GitHub Actions cron (free, approximate timing)
- **Hosting:** GitHub Pages (free)

## Email Timing Note

GitHub Actions scheduled runs are **best-effort** and can be delayed by minutes or even hours during busy periods. The workflow is scheduled for an off-peak minute to reduce this, but it may still arrive at 23:00, 23:40, or later.

For **exact 21:00 IST delivery**, use the free local scheduler guide in [`LOCAL_SCHEDULER_GUIDE.md`](LOCAL_SCHEDULER_GUIDE.md). This runs the same script on your own computer at exactly the right time, with no 3rd-party service needed.

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

> All attendance data is stored in your browser's `localStorage` — it stays private and persists between visits. Each course bundle gets its own storage key, so friends using the same computer won't overwrite each other's data.

---

*Built for PGP 2025-27 Term-IV*

---

## Privacy Note

This repo is public. If you prefer to hide your git author email from commit history, go to **Settings → Change visibility → Private**.
