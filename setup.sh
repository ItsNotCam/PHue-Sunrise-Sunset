#!/bin/bash

echo "\e[32mInstalling dependencies ..."
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install docker.io docker-compose python3 python3-pip -y
sudo python3 -m pip3 install --upgrade pip3
sudo apt-get install python3-venv -y
echo "\e[32mDone\n"

echo "\e[33mSetting up docker permission for $USER ..."
sudo groupadd docker >> /dev/null
sudo usermod -aG docker "$USER" >> /dev/null
echo "\e[33mDone\n"

echo "\e[33mStarting docker service ... "
sudo systemctl start docker
echo "\e[33mDone\n"

echo "\e[36mSetting up virtual environment ... "
python3 -m venv venv
echo "\e[36mDone\n"

echo "\e[32mInstalling python3 requirements ... "
. venv/bin/activate
pip3 install -r source/requirements.txt
echo "\e[32mDone\n"

echo "\e[35mSetting up crontab ..."
CRONSTR="* 3 * * * $PWD/venv/bin/python3 $PWD/source/sunrise_sunset.py # update_sun"
echo "Creating: <CronItem '$CRONSTR'>"
(crontab -l ; echo "$CRONSTR") | crontab -
venv/bin/python3 source/sunrise_sunset.py
echo "\e[35mDone\n"

echo "\e[34mSetting up docker mysql instance ..."
cd docker
docker-compose up -d
echo "\e[34mDone\n"
