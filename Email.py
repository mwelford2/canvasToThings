from main import send_email

with open('weekRuns.txt', 'r') as w:
    weekRuns = int(w.read())
with open('weekRuns.txt', 'w') as w:
    w.write(str(0));
times = "times"
if weekRuns == 1: times = "time"
send_email("Canvas to Things ran this week", f"Canvas to Things ran {weekRuns} times this week", "mwelford2@gmail.com")
