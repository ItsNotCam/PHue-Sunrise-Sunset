#!/bin/bash

echo "\e[36mSetting up virtual environment ... "
python3 -m venv venv
echo "\e[36mDone\n"

echo "\e[32mInstalling python3 requirements ... "
. venv/bin/activate
pip3 install -r source/requirements.txt
echo "\e[32mDone\n"

echo "\e[35mSetting up crontab ..."
venv/bin/python3 source/sunrise_sunset.py
echo "\e[35mDone\n"

echo "\e[34mSetting up docker mysql instance ...\e[0m"
cd docker
docker-compose up -d
echo "\e[34mDone\n"
