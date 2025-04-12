import smtplib
import requests
import json
from datetime import datetime
from datetime import timedelta
from email.message import EmailMessage

api_key = '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'
api_password = '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'
smtp_url = 'smtp.sendgrid.net'
smtp_port = 465
fromEmail = "canvastothings@gmail.com"

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
    email['From'] = fromEmail
    email.set_content(body)

    with smtplib.SMTP_SSL(smtp_url, smtp_port) as smtp:
        # smtp.starttls()
        smtp.login("apikey", api_key)
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

def getAssignments():

    classes = {524214, 525732, 525172, 525138, 526338, 513638, 528781} # Physics 1 + Lab, Anime, Econ food & you, First year engineering, data structures, eng design society

    with open('assignments.txt', 'r') as f:
        content = f.read()
        f.close()

    for c in classes:
        req = requests.get(api_url+f"courses/{c}/assignments?bucket=future", headers=headers)
        cur_ass = json.loads(req.text)
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
            if content.find(str(stick['id'])) == -1:
                print("adding assignment", stick['name'])
                with open('assignments.txt', 'a') as f:
                    f.write('\n')
                    f.write(str(stick['id']))
                    f.close()
                send_email(stick['name'], class_name + '\n' + str(due_at) + '\n' + 'Sent from git', THINGS_EMAIL)
                send_email(f'Assignment: {stick['name']} added', class_name + '\n' + str(due_at) + '\n' + 'Sent from mac', "canvastothings@gmail.com")
if __name__ == '__main__':
    getAssignments()
    with open('weekRuns.txt','r+') as w, open('totalRuns.txt', 'w') as t:
        numRuns = int(w.read().strip())
        numRuns += 1
        w.truncate() # clear weekRuns file
        w.write(str(numRuns))
        t.write(str(numRuns)) # should replace file contents
    print("Canvas To Things ran ", datetime.now())
