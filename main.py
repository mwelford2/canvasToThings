import json
import os
import re
import smtplib
from datetime import date, datetime
from email.message import EmailMessage
from urllib.parse import unquote, urlparse
from zoneinfo import ZoneInfo

import requests
from icalendar import Calendar


gmail_pass = os.getenv("GMAIL_PASSWORD")
smtp_url = "smtp.gmail.com"
smtp_port = 465
sender = os.getenv("SENDER_EMAIL")
THINGS_EMAIL = os.getenv("THINGS_EMAIL")
CANVAS_CALENDAR_FEED = os.getenv("CANVAS_CALENDAR_FEED")

UTC = ZoneInfo("UTC")
EASTERN_TZ = ZoneInfo("America/New_York")
COURSE_SUFFIX = re.compile(r"^(?P<title>.*) \[(?P<course>[^\[\]]+)\]$")
ASSIGNMENT_FRAGMENT = re.compile(r"^assignment_(\d+)$")


def require_environment_variables():
    required = {
        "GMAIL_PASSWORD": gmail_pass,
        "SENDER_EMAIL": sender,
        "THINGS_EMAIL": THINGS_EMAIL,
        "CANVAS_CALENDAR_FEED": CANVAS_CALENDAR_FEED,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )


def send_email(subject, body, to):
    email = EmailMessage()
    email["Subject"] = subject
    email["To"] = to
    email["From"] = sender
    email.set_content(body)

    with smtplib.SMTP_SSL(smtp_url, smtp_port) as smtp:
        smtp.login(sender, gmail_pass)
        smtp.send_message(email)


def fetch_canvas_calendar():
    response = requests.get(CANVAS_CALENDAR_FEED, timeout=30)
    response.raise_for_status()
    return Calendar.from_ical(response.content)


def split_canvas_summary(summary):
    """Return (assignment title, course code) from Canvas' ICS summary."""
    match = COURSE_SUFFIX.match(summary.strip())
    if match:
        return match.group("title").strip(), match.group("course").strip()
    return summary.strip(), "Canvas"


def assignment_id_from_url(url):
    """
    Canvas assignment calendar URLs end in #assignment_<id>.

    Using that ID keeps assignments.txt compatible with the old REST API version,
    so switching to the calendar feed does not re-add every existing assignment.
    """
    if not url:
        return None

    fragment = unquote(urlparse(url).fragment)
    match = ASSIGNMENT_FRAGMENT.match(fragment)
    return match.group(1) if match else None


def event_key(event):
    """Return a stable key for an assignment VEVENT, or None for non-assignments."""
    url = str(event.get("URL", "")).strip()
    assignment_id = assignment_id_from_url(url)
    if assignment_id:
        return assignment_id

    # Fallback for feeds that omit URL but retain Canvas' assignment UID.
    uid = str(event.get("UID", "")).strip()
    if uid.startswith("event-assignment-") or uid.startswith("event-sub-assignment-"):
        return f"uid:{uid}"

    return None


def parse_due_at_eastern(event):
    if "DTSTART" not in event:
        return None

    due_at = event.decoded("DTSTART")
    if isinstance(due_at, datetime):
        if due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=UTC)
        return due_at.astimezone(EASTERN_TZ)

    # Canvas can represent all-day events as DATE rather than DATE-TIME.
    if isinstance(due_at, date):
        return due_at

    return None


def is_future(due_at):
    if due_at is None:
        return False
    if isinstance(due_at, datetime):
        return due_at >= datetime.now(EASTERN_TZ)
    return due_at >= datetime.now(EASTERN_TZ).date()


def load_processed_assignments():
    try:
        with open("assignments.txt", "r") as file:
            return {line.strip() for line in file if line.strip()}
    except FileNotFoundError:
        return set()


def mark_assignment_processed(key):
    with open("assignments.txt", "a") as file:
        if file.tell() > 0:
            file.write("\n")
        file.write(key)


def get_assignments():
    calendar = fetch_canvas_calendar()
    processed = load_processed_assignments()

    num_added = 0
    names_added = []
    assignments_added = {}

    for event in calendar.walk("VEVENT"):
        key = event_key(event)
        if key is None or key in processed:
            continue

        due_at = parse_due_at_eastern(event)
        if not is_future(due_at):
            continue

        raw_summary = str(event.get("SUMMARY", "Untitled assignment"))
        assignment_name, class_name = split_canvas_summary(raw_summary)

        print("adding assignment", assignment_name)
        mark_assignment_processed(key)
        processed.add(key)

        due_text = str(due_at)
        assignments_added[assignment_name] = f"{class_name}|{due_text}"
        send_email(assignment_name, class_name + "\n" + due_text, THINGS_EMAIL)
        names_added.append(f"{assignment_name}|{class_name}|{due_text}")
        num_added += 1

    return num_added, names_added, assignments_added


def increment_run_counter():
    try:
        with open("weekRuns.txt", "r") as file:
            num_runs = int(file.read().strip() or "0")
    except (FileNotFoundError, ValueError):
        num_runs = 0

    num_runs += 1

    with open("weekRuns.txt", "w") as file:
        file.write(str(num_runs))

    with open("totalRuns.txt", "w") as file:
        file.write(str(num_runs))


if __name__ == "__main__":
    require_environment_variables()

    num, names, assignments_added = get_assignments()

    with open("assignmentsAdded.txt", "w") as file:
        file.write(json.dumps(assignments_added, indent=2, ensure_ascii=False))

    summary = ", ".join(names) if names else "None"
    send_email(
        f"Added {num} assignments",
        f"Added: {summary}",
        "mwelford2@gmail.com",
    )

    increment_run_counter()
    print("Canvas To Things ran", datetime.now(EASTERN_TZ))
