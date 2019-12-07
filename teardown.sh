#!/bin/bash
echo "\n\e[35mRemoving crontabs relating to this app ... "
script='
from crontab import CronTab
import sys

user = sys.argv[1]
cron = CronTab(user=user)
for comment in ["sunrise","sunset","update_sun"]:
	for tab in cron.find_comment(comment):
		print("Removing:",tab)
		cron.remove(tab)
cron.write()
'
venv/bin/python3 -c "$script" "$USER"
echo "\e[35mDone\n"

echo "\e[32mRemoving virtual environment ..."
rm -rf venv
echo "\e[32mDone\n"

echo "\e[36mDeleting docker instance ...\e[0m"
cd docker
docker-compose down
echo "\e[36mDone\n"

echo "\e[36mRemoving docker image ..."
docker image rm mysql:8.0.18
echo "\n\e[36mPruning docker volumes ..."
docker volume prune -f
docker volume rm docker_huesql -f
echo "\e[36mDone\n"

