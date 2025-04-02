from main import send_email

with open('weekRuns.txt', 'r+') as w:
    weekRuns = int(w.read())
    w.seek(0)
    w.write('0')
    w.truncate()
    w.close()
times = "times"
if weekRuns == 1: times = "time"
send_email("Canvas to Things ran this week", f"Canvas to Things ran {weekRuns} times this week", "mwelford2@gmail.com")