# canvasToThings

Automatically syncs upcoming Canvas assignments into [Things 3](https://culturedcode.com/things/) by sending them via email using Things' built-in Mail to Things feature.

This version uses Canvas' private **Calendar Feed (ICS)** instead of the Canvas REST API. That avoids expiring student API tokens and does not require course IDs.

Each time the script runs, it downloads your Canvas calendar feed, finds future assignment events, and emails any assignment that has not been processed before to your Things inbox. Processed assignment IDs are stored locally so nothing gets added twice.

---

## Prerequisites

- Python 3.9+
- A Canvas account with access to the Calendar Feed
- Things 3 (Mac/iPhone/iPad) with [Mail to Things](https://culturedcode.com/things/support/articles/2908262/) enabled
- A Gmail account to send emails from (with an [App Password](https://support.google.com/accounts/answer/185833) set up)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/mwelford2/canvasToThings.git
cd canvasToThings
```

### 2. Install dependencies

```bash
pip install -r reqs.txt
```

### 3. Copy your Canvas Calendar Feed URL

In Canvas:

1. Open **Calendar**
2. Click **Calendar Feed**
3. Copy the private ICS URL

Treat this URL like a password. Anyone with the URL may be able to read your Canvas calendar feed.

### 4. Set environment variables

The script reads these environment variables:

| Variable | Description |
|---|---|
| `CANVAS_CALENDAR_FEED` | Your private Canvas Calendar Feed / ICS URL |
| `GMAIL_PASSWORD` | A Gmail [App Password](https://support.google.com/accounts/answer/185833) (not your normal Gmail password) |
| `SENDER_EMAIL` | The Gmail address you're sending from |
| `THINGS_EMAIL` | Your Things Mail to Things address |

On Mac/Linux:

```bash
export CANVAS_CALENDAR_FEED="https://your-canvas-instance/feeds/calendars/...ics"
export GMAIL_PASSWORD="your_app_password"
export SENDER_EMAIL="you@gmail.com"
export THINGS_EMAIL="your-things-address@things.email"
```

You no longer need `CANVAS_API_KEY`, `CANVAS_DOMAIN`, or `classIDs.txt` for the main sync.

### 5. Initialize the tracking files

```bash
touch assignments.txt assignmentsAdded.txt
echo "0" > totalRuns.txt
echo "0" > weekRuns.txt
```

The calendar-feed version keeps using Canvas assignment IDs when possible, so an existing `assignments.txt` from the old REST API version remains compatible and should prevent previously processed assignments from being re-added.

---

## Running

```bash
python main.py
```

The script will:

1. Download your Canvas Calendar Feed
2. Ignore ordinary calendar events and keep assignment events
3. Ignore assignments whose due date is already in the past
4. Skip assignments already recorded in `assignments.txt`
5. Email each new assignment to your Things inbox with its course code and due date
6. Send a summary email listing everything that was added

Canvas includes the course code in calendar summaries, for example:

```text
Homework 4 [EEL3701C]
```

The script sends `Homework 4` as the Things task title and `EEL3701C` in the task body.

---

## Automating with GitHub Actions

The repo includes a daily GitHub Actions workflow.

Go to:

**Repository → Settings → Secrets and variables → Actions**

and add these repository secrets:

- `CANVAS_CALENDAR_FEED`
- `GMAIL_PASSWORD`
- `SENDER_EMAIL`
- `THINGS_EMAIL`

The old `CANVAS_API_KEY` secret is not used by the calendar-feed workflow.

The workflow runs automatically once per day and can also be triggered manually from the **Actions** tab.

---

## Files

| File | Purpose |
|---|---|
| `main.py` | Downloads/parses the Canvas ICS feed and sends new assignments to Things |
| `reqs.txt` | Python dependencies (`requests`, `icalendar`) |
| `assignments.txt` | Tracks processed Canvas assignment IDs |
| `assignmentsAdded.txt` | JSON log of the most recent batch added |
| `weekRuns.txt` / `totalRuns.txt` | Run counters |
| `.github/workflows/main.yml` | Scheduled GitHub Actions sync |

`classIDs.txt` is left in the repository for compatibility/history but is no longer used by `main.py`.
