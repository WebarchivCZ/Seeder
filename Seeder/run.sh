#!/usr/bin/env bash

bash prepare.sh
bash pull_locales.sh

python3 ./manage.py runserver 0.0.0.0:8000