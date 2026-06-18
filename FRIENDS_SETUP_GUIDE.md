# Friend Setup Guide — Term-IV Dashboard

> **TL;DR:** Fork this repo → Enable GitHub Pages → Pick your courses → Add your Resend API key + course bundle → Done. Takes 5 minutes.

---

## What You Get

Your own personal Term-IV dashboard with:
- **Timetable** for your course bundle
- **Clash detection** + resolution tracker (record which class you plan to attend)
- **Attendance tracking** with export
- **CFA countdown** (optional)
- **Daily email reminders** with clash alerts

---

## Step 1: Fork This Repo

1. Go to the GitHub repo: `https://github.com/DeepIIM/term4-dashboard`
2. Click **Fork** (top-right corner)
3. Choose your personal account
4. Wait ~10 seconds for the fork to complete

---

## Step 2: Enable GitHub Pages

1. In your forked repo, go to **Settings** → **Pages** (left sidebar)
2. Under "Build and deployment":
   - **Source:** Deploy from a branch
   - **Branch:** `main` → `/ (root)`
3. Click **Save**
4. Wait 1–2 minutes, then visit: `https://YOUR_USERNAME.github.io/term4-dashboard/`
   (replace `YOUR_USERNAME` with your actual GitHub username)

---

## Step 3: Set Up Your Bundle

1. Open your dashboard URL
2. On first load, a **setup wizard** appears:
   - Choose if you're giving CFA (and your CFA date if yes)
   - Click **"Pick Courses"** to open the bundle picker
   - Search and select your 9 courses + sections
   - Click **Save Bundle**
3. Your dashboard is now personalized!

> **To change your bundle later:** Click the **⚙️ Bundle** button in the top-right.

---

## Step 4: Daily Email Reminders (Optional but Recommended)

### 4a. Get a Resend API Key (Free)

1. Go to [resend.com](https://resend.com) and sign up
2. Verify your email address
3. Go to **API Keys** → click **Create API Key**
4. Name it "Term-IV Dashboard", choose **Sending access**
5. Copy the key (starts with `re_`)

### 4b. Add Secrets to Your GitHub Repo

1. In your forked repo, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add three secrets:

| Name | Value |
|---|---|
| `COURSES_JSON` | Your personal course bundle JSON (see step 3 above) |
| `RESEND_API_KEY` | Your Resend API key (e.g. `re_xxxxxx`) |
| `EMAIL_TO` | Your email address (where reminders go) |

4. The GitHub Actions workflow will run automatically every day **around 9:00 PM IST**

### 4c. Test It Now

1. Go to **Actions** tab in your repo
2. Click **"Daily Email Reminder"** on the left
3. Click **"Run workflow"** → **Run workflow**
4. Check your inbox in ~30 seconds

---

## How to Use the Dashboard

### Home Page
- **Stats rings:** Term progress, CFA countdown (if set), next free day, attendance rate
- **Today / Tomorrow:** Your classes with attendance buttons
- **Upcoming Clashes:** Shows clashes in the next 3 weeks. Click **"Resolve"** to record your plan:
  - Attend Course A as planned
  - Attend Course B as planned
  - Attend sister section (if available)
  - Skip one / Decide later
- **Course Progress:** Visual progress bars for all your courses

### My Courses Tab
- Click any course card to see all sessions
- Mark attendance with ✓ / ✗ buttons
- See clash suggestions per session
- View your **Clash Decisions** history at the top of the modal

### Session Calendar Tab
- Monthly calendar with all your sessions
- Clash days highlighted
- Click any session dot to open the course modal

### Attendance Data
- Everything is saved in your **browser's localStorage**
- **Export:** Click "Export" to download a JSON backup
- **Reset:** Click "Reset" to clear all attendance data

---

## Customizing Your CFA Date

1. Click **"Edit Profile"** in the Upcoming Clashes section
2. Toggle CFA yes/no
3. Pick your CFA exam date
4. The home page countdown will update automatically

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Dashboard shows old/broken data | Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac) |
| Emails not arriving | Check spam folder. Verify `RESEND_API_KEY`, `EMAIL_TO`, and `COURSES_JSON` secrets are correct. |
| Emails show someone else's classes | You forgot to add the `COURSES_JSON` secret with your own bundle. See Step 3. |
| Bundle picker won't open | The page needs to be served over HTTP (not `file://`). Use GitHub Pages or run `python -m http.server` locally. |
| Clash decisions disappear | Decisions are stored per-browser. If you switch devices, they won't sync. Use the same browser/profile. |
| Want to change my email | Go to repo Settings → Secrets → edit `EMAIL_TO` |

---

## Data Privacy

- **Your attendance** and **clash decisions** stay in your browser only
- **Your email**, **Resend API key**, and **course bundle** stay in your GitHub secrets only
- No data is sent to any server except Resend (for your own email reminders)

## Exact Email Timing (Optional)

GitHub Actions scheduled runs can be delayed. If you want your email at exactly 9:00 PM IST, follow the free local scheduler guide in [`LOCAL_SCHEDULER_GUIDE.md`](LOCAL_SCHEDULER_GUIDE.md).

---

## Need Help?

DM the person who shared this with you. They can help debug.
