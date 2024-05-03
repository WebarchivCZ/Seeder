#!/usr/bin/env bash

bash prepare.sh
bash pull_locales.sh

# Export working environment to use in CRON later
printenv | sed 's/\(^[^=]*\)=\(.*\)/\1="\2"/' > /code/.cronenv

python3 ./manage.py runserver 0.0.0.0:8000