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

# IMPORTANT: THIS CODE ONLY WORKS PROPERLY ASSUMING ALL ASSIGNMENTS ARE DUE AT 11:59 PM.
# IMPORTANT: SHOULD THAT NOT BE THE CASE THIS FUNCTION MUST BE CHANGED.
def get_time_subtraction(assignments):
    due_date_str = ""
    for assignment in assignments:
        if assignment['due_at'] is None:
            continue
        due_date_str = assignment['due_at']
        break
    due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%SZ")
    total_hours = 0
    while due_date.hour != 23:
        due_date = due_date - timedelta(hours=1)
        total_hours += 1
    return total_hours


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
        all_ass = json.loads(req.text) + json.loads(req2.text) # join upcoming and future assignments in one dict
        time_diff = get_time_subtraction(all_ass)
        for cur_ass in all_ass:
            # print(cur_ass['name'], cur_ass['due_at'], end='  UPDATED DATE: ')
            if not cur_ass['due_at'] is None:
                due_at = datetime.strptime(cur_ass['due_at'], "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=time_diff)
            else: due_at = 'No due date'
            # print(due_at)
            class_name = id_to_name(c)
            # print(ass)
            # print(cur_ass['id'])
            # print(content.find('6268132'))
            if content.find(str(cur_ass['id'])) == -1: # make sure assignment hasn't been processed before
                print("adding assignment", cur_ass['name'])
                if "Homework Board" in str(cur_ass['name']) and c == 540816: # IMPORTANT: SPECIFIC FOR AEB2280, REMOVE FOR FUTURE CLASSES
                    add_reflection_post(class_name, due_at, cur_ass['name'])
                with open('assignments.txt', 'a') as f:
                    f.write('\n')
                    f.write(str(cur_ass['id']))
                    f.close()
                send_email(cur_ass['name'], class_name + '\n' + str(due_at), THINGS_EMAIL)
                # send_email(f"Assignment: {cur_ass['name']} added", class_name + "\n" + str(due_at) + "\n" + "Sent from mac", "canvastothings@gmail.com")
                name_added.append('' + cur_ass['name'] + '|' + class_name + '|' + str(due_at))
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
        name_str += f"    \"{cur[0]}\": \"{cur[1]}|{cur[2]}\",\n"
    name_str = name_str[:-2]
    name_str+="\n}"
    with open('assignmentsAdded.txt','w') as a:
        a.write(name_str)
    with open('weekRuns.txt','r') as w, open('totalRuns.txt', 'w') as t:
        numRuns = int(w.read().strip())
        numRuns += 1
        t.write(str(numRuns)) # should replace file contents
    with open('weekRuns.txt', 'w') as w:
        w.write(str(numRuns))
    print("Canvas To Things ran ", datetime.now())
