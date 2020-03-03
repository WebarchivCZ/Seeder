#!/usr/bin/env bash

pip3 install -r ../requirements.txt --upgrade
python3 ./manage.py migrate

python3 ./manage.py collectstatic --noinput --clear

python3 ./manage.py crontab add
