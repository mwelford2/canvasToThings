# canvasToThings

Automatically syncs your upcoming Canvas assignments into [Things 3](https://culturedcode.com/things/) by sending them via email using Things' built-in Mail to Things feature.

Each time the script runs, it checks your Canvas courses for upcoming and future assignments, and for any that haven't been added before, it fires off an email to your Things inbox with the assignment name, course, and due date. Already-processed assignments are tracked locally so nothing gets added twice.

---

## Prerequisites

- Python 3.9+
- A Canvas account with API access
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

### 3. Set your Canvas domain

The script is currently set to `ufl.instructure.com`. If you're at a different school, open `main.py` and update this line:

```python
CANVAS_DOMAIN = "ufl.instructure.com"
```

Replace it with your institution's Canvas domain (e.g. `canvas.harvard.edu`).

### 4. Add your course IDs to `classIDs.txt`

Each line should contain one Canvas course ID (a number). You can find a course's ID in the URL when you visit it on Canvas — it looks like `canvas.youruniversity.edu/courses/12345678`.

```
12345678
87654321
```

### 5. Set environment variables

The script reads credentials from environment variables. Set the following:

| Variable | Description |
|---|---|
| `CANVAS_API_KEY` | Your Canvas API token ([how to generate one](https://community.canvaslms.com/t5/Student-Guide/How-do-I-manage-API-access-tokens-as-a-student/ta-p/273)) |
| `GMAIL_PASSWORD` | A Gmail [App Password](https://support.google.com/accounts/answer/185833) (not your regular Gmail password) |
| `SENDER_EMAIL` | The Gmail address you're sending from |
| `THINGS_EMAIL` | Your Things Mail to Things address (found in Things 3 → Settings → Mail to Things) |

On Mac/Linux you can export them in your shell:

```bash
export CANVAS_API_KEY="your_canvas_token"
export GMAIL_PASSWORD="your_app_password"
export SENDER_EMAIL="you@gmail.com"
export THINGS_EMAIL="your-things-address@things.email"
```

### 6. Initialize the tracking files

The script uses a few text files to track state. Make sure these exist (they can be empty):

```bash
touch assignments.txt assignmentsAdded.txt
echo "0" > totalRuns.txt
echo "0" > weekRuns.txt
```

---

## Running

```bash
python main.py
```

The script will:
1. Fetch upcoming and future assignments from each course in `classIDs.txt`
2. Skip any assignments already recorded in `assignments.txt`
3. Email each new assignment to your Things inbox with its course name and due date
4. Send you a summary email listing everything that was added

---

## Automating with GitHub Actions

The repo includes a GitHub Actions workflow, so you can run this on a schedule without keeping your computer on. To use it:

1. Fork the repository
2. Go to your fork's **Settings → Secrets and variables → Actions**
3. Add each of the four environment variables above as repository secrets
4. The workflow will run on its configured schedule automatically

---

## Files

| File | Purpose |
|---|---|
| `main.py` | Main script |
| `Email.py` | Email helper |
| `reqs.txt` | Python dependencies |
| `classIDs.txt` | Your Canvas course IDs (you edit this) |
| `assignments.txt` | Tracks which assignment IDs have been processed |
| `assignmentsAdded.txt` | JSON log of the most recent batch added |
| `output.log` / `backup.log` | Run logs |
| `weekRuns.txt` / `totalRuns.txt` | Run counters |
