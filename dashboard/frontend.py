
from flask import Flask
from flask import render_template, request, url_for
import datetime


app = Flask(__name__)
app.secret_key = 'some secret key'

dashdata = {'traffic': '15m', 'fuel': '1.35', 'temperature': '18 C'}
dashdata['tel'] = ['Telefon A', 'Telefon B',
                   'Telefon C', 'Telefon D', 'Telefon E']
dashdata['news'] = ['News1', 'News2', 'News C', 'News D', 'News E']
dashdata['calendar'] = ['Cal 1', 'Cal 2', 'Cal C', 'Cal  D', 'Cal E']
temptime = datetime.datetime.utcnow()
dashdata['lastupdated'] = temptime.strftime('%H:%M')
dashdata['motd'] = ["Eine Nachricht des Tages"]
dashdata['corona'] = ["00"]


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard(messages=None):
    print("show dashboard..." + str(request.data))
    global dashdata
    if request.method == 'POST':
        dashjsoncontent = request.json
        dashdata = dashjsoncontent  # test?
        temptime = datetime.datetime.utcnow()
        dashdata['lastupdated'] = temptime.strftime('%H:%M')
        print("Last update: " + dashdata['lastupdated'])
        return 'Done update'

    return render_template('dashboard.html', dashdata=dashdata)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
