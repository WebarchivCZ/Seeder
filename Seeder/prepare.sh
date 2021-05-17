#!/usr/bin/env bash

pip3 install -r ../requirements.txt --upgrade
python3 ./manage.py migrate
# Make sure it runs at least once but every time also works
python3 ./manage.py match_cc_types
python3 ./manage.py collectstatic --noinput --clear
python3 ./manage.py crontab add
