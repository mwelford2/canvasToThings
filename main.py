import smtplib
import json
import os
from datetime import datetime
from datetime import timedelta
from email.message import EmailMessage
from zoneinfo import ZoneInfo

from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

gmail_pass = os.getenv("GMAIL_PASSWORD")
smtp_url = "smtp.gmail.com"
smtp_port = 465
sender = os.getenv("SENDER_EMAIL")

CANVAS_API_TOKEN = os.getenv("CANVAS_API_KEY")
CANVAS_DOMAIN = os.getenv("CANVAS_DOMAIN")

THINGS_EMAIL = os.getenv("THINGS_EMAIL")

canvas = Canvas(f"https://{CANVAS_DOMAIN}", CANVAS_API_TOKEN)


def send_email(subject, body, to):
    email = EmailMessage()
    email['Subject'] = subject
    email['To'] = to
    email['From'] = sender
    email.set_content(body)

    with smtplib.SMTP_SSL(smtp_url, smtp_port) as smtp:
        # smtp.starttls()
        smtp.login(sender, gmail_pass)
        smtp.send_message(email)
        # print("Sent successfully!")


UTC = ZoneInfo("UTC")
EASTERN_TZ = ZoneInfo("America/New_York")


def parse_due_at_eastern(due_at):
    if due_at is None:
        return 'No due date'
    due_at_utc = datetime.strptime(due_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    return due_at_utc.astimezone(EASTERN_TZ)


def remove_duplicates(all_ass):
    unique_assignments = []
    processed_assignment_ids = []
    for ass in all_ass:
        if ass.id not in processed_assignment_ids:
            unique_assignments.append(ass)
            processed_assignment_ids.append(ass.id)
    return unique_assignments


def get_assignments():
    num_added = 0
    name_added = []
    assignments_added = {}

    with open("classIDs.txt", 'r') as c:
        classes = [int(line.strip()) for line in c]

    with open('assignments.txt', 'r') as f:
        content = f.read()
        f.close()

    for c in classes:
        try:
            course = canvas.get_course(c)
            all_ass = list(course.get_assignments(bucket='future')) + list(course.get_assignments(bucket='upcoming')) # join upcoming and future assignments in one list
        except CanvasException as e:
            raise RuntimeError(f"Canvas API error while fetching course {c}: {e}") from e
        # all_ass = remove_duplicates(all_ass)
        class_name = course.name
        for cur_ass in all_ass:
            # print(cur_ass.name, cur_ass.due_at, end='  UPDATED DATE: ')
            due_at = parse_due_at_eastern(getattr(cur_ass, 'due_at', None))
            # print(due_at)
            # print(ass)
            # print(cur_ass.id)
            # print(content.find('6268132'))
            if str(cur_ass.id) not in content: # make sure assignment hasn't been processed before
                print("adding assignment", cur_ass.name)
                with open('assignments.txt', 'a') as f:
                    f.write('\n')
                    f.write(str(cur_ass.id))

                assignments_added[cur_ass.name] = f"{class_name}|{due_at}"
                send_email(cur_ass.name, class_name + '\n' + str(due_at), THINGS_EMAIL)
                # send_email(f"Assignment: {cur_ass.name} added", class_name + "\n" + str(due_at) + "\n" + "Sent from mac", "canvastothings@gmail.com")
                name_added.append('' + cur_ass.name + '|' + class_name + '|' + str(due_at))
                num_added+=1
    return num_added, name_added, assignments_added


def add_reflection_post(class_name, due_at, board_name):
    name = str(board_name).replace('Homework Board', 'Reflection Post')
    due_date = due_at + timedelta(days=7)
    send_email(name, class_name + '\n' + str(due_date), THINGS_EMAIL)
    return name

if __name__ == '__main__':
    num, names, assignments_added = get_assignments()
    with open('assignmentsAdded.txt','w') as a:
        a.write(json.dumps(assignments_added, indent=2, ensure_ascii=False))

    n = str(names).strip("[]")
    send_email(f"Added {num} assignments", f"Added: {n}", "mwelford2@gmail.com")
    name_str = "{"
    for n in names:
        cur = n.split('|')
        name_str += f"    \"{cur[0]}\": \"{cur[1]}|{cur[2]}\",\n"
    name_str = name_str[:-2]
    name_str+="\n}"
    # with open('assignmentsAdded.txt','w') as a:
    #     a.write(name_str)
    with open('weekRuns.txt','r') as w, open('totalRuns.txt', 'w') as t:
        numRuns = int(w.read().strip())
        numRuns += 1
        t.write(str(numRuns)) # should replace file contents
    with open('weekRuns.txt', 'w') as w:
        w.write(str(numRuns))
    print("Canvas To Things ran ", datetime.now())
