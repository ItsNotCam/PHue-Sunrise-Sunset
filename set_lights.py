import requests
import json
import mysql.connector as conn
from datetime import datetime
import sys, os

config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'config.json')
with open(config_path) as file:
    js = json.loads(file.read())
    time_type = js['hue']['time_type']
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

state = requests.get(f"{hue_uri}/lights").json()
groups = requests.get(f"{hue_uri}/groups").json()
group_number, group_data = list(filter(
    lambda group : group[1]["name"].lower() == "home", 
    groups.items()
))[0]

time_state = time_type[args[1]]
time_state["on"] = True in group_data["state"].values()

body = json.dumps(time_type[args[1]])
uri = f"{hue_uri}/groups/{group_number}/action"
js = requests.put(uri,body).json()
