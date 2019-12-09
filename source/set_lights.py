import requests
import json
import mysql.connector as conn
from datetime import datetime
import sys, os

config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.json')
with open(config_path) as file:
    js = json.loads(file.read())
    time_type = js['hue']['time_type']
    host = js['db']['host']
    user = js['db']['user']
    password = js['db']['password']
    database = js['db']['database']
    table = js['db']['table']
    
    hue_ip = js['hue']['ip']
    hue_apik = js['hue']['apik']
    hue_uri = f"http://{hue_ip}/api/{hue_apik}"

    del js

args = sys.argv
if len(args) < 2:
    print("I require two arguments")
    exit()
if args[1] not in time_type.keys():
    print("Invalid parameter - I require \"night\" or \"day\"")
    exit()

try:
    # init db
    cnx = conn.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    if not cnx.is_connected():
        raise Exception

except Exception as e:
    print("Failed to connecto to database")
    print(e)

state = requests.get(f"{hue_uri}/lights").json()
groups = requests.get(f"{hue_uri}/groups").json()
group_number, group_data = list(filter(
    lambda group : group[1]["name"].lower() == "home", 
    groups.items()
))[0]

uri = f"{hue_uri}/groups/{group_number}/action"
body = json.dumps(time_type[args[1]])
js = requests.put(uri,body).json()

if cnx is not None or cnx.is_connected():
    success = 'error' not in js
    method = "PUT"

    cursor = cnx.cursor(dictionary=True)
    query = '''
        INSERT INTO {} (
          success, dt, method, uri, preset
        ) VALUES (
            {}, \"{}\", \"{}\", \"{}\", \"{}\"
        )
        '''.format(table, int(success), datetime.now(), method, uri, args[1])
    cursor.execute(query)
    
    cnx.commit()
    cursor.close()
    cnx.close()

    del cursor
    del cnx

