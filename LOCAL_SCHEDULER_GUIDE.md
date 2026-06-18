# Local Scheduler Guide — Exact 21:00 IST Email Reminders

GitHub Actions scheduled runs are **best-effort** and can be delayed. If you want your reminder email to arrive at exactly 21:00 IST every day, run the same script on your own computer using the free built-in scheduler.

This guide uses **Windows Task Scheduler** (built into Windows, no 3rd-party tool required).

---

## What You Need

- A Windows PC that is turned on around 21:00 IST
- Python installed (`python --version` should work)
- Your `.env` file filled in with:
  - `RESEND_API_KEY`
  - `EMAIL_TO`
  - `COURSES_JSON`

If you have not created `.env` yet, copy `.env.example` to `.env` and fill in the values.

---

## Quick Setup (Automated)

1. Open **PowerShell as Administrator**.
2. Navigate to this project folder.
3. Run:
   ```powershell
   .\scripts\setup_windows_scheduler.ps1
   ```
4. The script creates a scheduled task named `Term4DailyReminder` that runs every day at 21:00 IST.

To verify, open **Task Scheduler** → search for `Term4DailyReminder`.

---

## Manual Setup

If you prefer to set it up yourself:

1. Open **Task Scheduler** (search in Start menu).
2. Click **Create Task**.
3. **General** tab:
   - Name: `Term4DailyReminder`
   - Select **Run whether user is logged on or not**
   - Check **Run with highest privileges** (optional)
4. **Triggers** tab:
   - Click **New**
   - Begin the task: **On a schedule**
   - Settings: **Daily**
   - Start time: `21:00:00`
   - Make sure the date/time is set to IST
5. **Actions** tab:
   - Click **New**
   - Action: **Start a program**
   - Program/script: `powershell.exe`
   - Add arguments: `-ExecutionPolicy Bypass -File "C:\full\path\to\scripts\run_reminder_local.ps1"`
6. **Conditions** tab:
   - Uncheck **Start the task only if the computer is on AC power** (optional, for laptops)
7. Click **OK** and enter your Windows password if prompted.

---

## Test the Local Run

Before waiting for 21:00 IST, test it once:

```powershell
.\scripts\run_reminder_local.ps1
```

You should receive an email within a few seconds.

---

## Disable or Remove the Scheduled Task

To stop local emails:

```powershell
schtasks /Delete /TN "Term4DailyReminder" /F
```

Or open Task Scheduler, right-click the task, and choose **Disable** or **Delete**.

---

## FAQ

**Q: Do I need to leave my computer on?**  
A: Yes. Windows Task Scheduler can only run when the PC is on.

**Q: What if my Windows timezone is not IST?**  
A: Set the trigger time to the equivalent of 21:00 IST in your local timezone, or change your system timezone to IST.

**Q: Will this conflict with GitHub Actions emails?**  
A: If you use both, you will get two emails. To avoid duplicates, disable the GitHub Actions workflow:
   1. Go to **Actions → Daily Course Reminder**
   2. Click the **...** menu → **Disable workflow**

**Q: Is my data safe?**  
A: Yes. The `.env` file stays on your computer. The script only sends an email through Resend using your own API key.
