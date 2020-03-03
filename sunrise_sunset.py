from datetime import datetime, timedelta
from crontab import CronTab
import requests, json, time, sqlite3, os, sys

user = sys.argv[1]
path = os.path.abspath(os.path.dirname(__file__))

config_path = os.path.join(path, 'data', 'config.json')
with open(config_path) as file:
    js = json.loads(file.read())
city_name = js['location']['city_name']
state_id = js['location']['state_id']

db = sqlite3.connect(os.path.join(path,'data', "cities.db"))
latitude,longitude,offset = db.execute('''
    SELECT latitude, longitude, utc_offset
    FROM cities 
    WHERE state_id=\"{}\" AND city=\"{}\"
'''.format(state_id,city_name)
).fetchone()
db.close()

params = { "lat": latitude, "lng": longitude, "date": "today" } 
results = requests.get(
    url="https://api.sunrise-sunset.org/json", 
    params=params
).json()['results']


sunrise_time = (
    datetime.strptime(results['sunrise'],"%I:%M:%S %p") + \
    timedelta(hours=offset)
).time() 

sunset_time = (
    datetime.strptime(results['sunset'],"%I:%M:%S %p") + \
    timedelta(hours=offset)
).time()


cron = CronTab(user=user)
command = f"{path}/venv/bin/python3 {path}/set_lights.py night"

for job in cron.find_comment('sunset'):
    cron.remove(job)

sunset = cron.new(command=command, comment="sunset")
sunset.day.every(1)
sunset.hour.on(sunset_time.hour)
sunset.minute.on(sunset_time.minute)
cron.write()
