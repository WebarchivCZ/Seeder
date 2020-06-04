#!/usr/bin/env bash

bash pull_locales.sh
python3 ./manage.py makemessages -a
