from datetime import datetime, timedelta
from crontab import CronTab
import requests, json, time, sqlite3, os, sys

user = sys.argv[1]

basedir = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(basedir, 'config.json')
with open(config_path) as file:
    js = json.loads(file.read())
    city_name = js['location']['city_name']
    state_id = js['location']['state_id']

    path = js['path']

    del js

db = sqlite3.connect(os.path.join(basedir,"cities.db"))
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

found = cron.find_comment('sunrise')
for job in found:
    cron.remove(job)

sunrise = cron.new(
    command=f"{path}/venv/bin/python3 {path}/source/set_lights.py day", 
    comment="sunrise"
)
sunrise.day.every(1)
sunrise.hour.on(sunrise_time.hour)
sunrise.minute.on(sunrise_time.minute)
print("Creating:",repr(sunrise))

found = cron.find_comment('sunset')
for job in found:
    cron.remove(job)

sunset = cron.new(
    command=f"{path}/venv/bin/python3 {path}/source/set_lights.py night",
    comment="sunset"
)
sunset.day.every(1)
sunset.hour.on(sunset_time.hour)
sunset.minute.on(sunset_time.minute)
print("Creating:",repr(sunset))

cron.write()
