import smtplib
import requests
import json
from datetime import datetime
from datetime import timedelta
from email.message import EmailMessage

gmail_pass = 'mawfuqllybzcbfoc'
smtp_url = 'smtp.gmail.com'
smtp_port = 465
sender = "canvastothings@gmail.com"

CANVAS_API_TOKEN = "1016~PEAmwYr7G9WehY9T8NJmYYEC9UXw3r8TD9GLYceUwFzvcw7cYNxyuWATrF7Fr4NE"
CANVAS_DOMAIN = "ufl.instructure.com"
api_url = f"https://{CANVAS_DOMAIN}/api/v1/"

THINGS_EMAIL = "add-to-things-nelcms64mpl4syg7p44@things.email"

headers = {
    'Authorization': f'Bearer {CANVAS_API_TOKEN}',
    'Content-Type': 'application/json'
}

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


def id_to_name(class_id):
    # print(class_id)
    req = requests.get(api_url+f"courses/{class_id}", headers=headers)
    classes = json.loads(req.text)
    if classes['id'] == class_id:
        return classes['name']
    return None
    # return JSON['name']
    pass

def get_assignments():
    num_added = 0
    name_added = []
    
    with open("classIDs.txt", 'r') as c:
        classes = [int(line.strip()) for line in c]

    with open('assignments.txt', 'r') as f:
        content = f.read()
        f.close()

    for c in classes:
        req = requests.get(api_url+f"courses/{c}/assignments?bucket=future", headers=headers)
        req2 = requests.get(api_url+f"courses/{c}/assignments?bucket=upcoming", headers=headers)
        cur_ass = json.loads(req.text) + json.loads(req2.text) # join upcoming and future assignments in one dict
        for stick in cur_ass:
            # print(stick['name'], stick['due_at'], end='  UPDATED DATE: ')
            if not stick['due_at'] is None:
                due_at = datetime.strptime(str(stick['due_at']), '%Y-%m-%dT%H:%M:%SZ') - timedelta(hours=4)
            else: due_at = 'No due date'
            # print(due_at)
            class_name = id_to_name(c)
            # print(ass)
            # print(stick['id'])
            # print(content.find('6268132'))
            if content.find(str(stick['id'])) == -1: # make sure assignment hasn't been processed before
                print("adding assignment", stick['name'])
                if "Homework Board" in str(stick['name']) and c == 540816: # IMPORTANT: SPECIFIC FOR AEB2280, REMOVE FOR FUTURE CLASSES
                    add_reflection_post(class_name, due_at, stick['name'])
                with open('assignments.txt', 'a') as f:
                    f.write('\n')
                    f.write(str(stick['id']))
                    f.close()
                send_email(stick['name'], class_name + '\n' + str(due_at), THINGS_EMAIL)
                # send_email(f"Assignment: {stick['name']} added", class_name + "\n" + str(due_at) + "\n" + "Sent from mac", "canvastothings@gmail.com")
                name_added.append('' + stick['name'] + '|' + class_name + '|' + str(due_at))
                num_added+=1
    return num_added, name_added


def add_reflection_post(class_name, due_at, board_name):
    name = str(board_name).replace('Homework Board', 'Reflection Post')
    due_date = due_at + timedelta(days=7)
    send_email(name, class_name + '\n' + str(due_date), THINGS_EMAIL)
    return name

if __name__ == '__main__':
    num, names = get_assignments()
    n = str(names).strip("[]")
    send_email(f"Added {num} assignments", f"Added: {n}", "mwelford2@gmail.com")
    name_str = "{\n"
    for n in names:
        cur = n.split('|')
        name_str += f"    {cur[0]}: {cur[1]}|{cur[2]}\n"
    name_str+="}"
    with open('assignmentsAdded.txt','w') as a:
        a.write(name_str)
    with open('weekRuns.txt','r') as w, open('totalRuns.txt', 'w') as t:
        numRuns = int(w.read().strip())
        numRuns += 1
        t.write(str(numRuns)) # should replace file contents
    with open('weekRuns.txt', 'w') as w:
        w.write(str(numRuns))
    print("Canvas To Things ran ", datetime.now())
