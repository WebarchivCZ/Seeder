#!/usr/bin/env bash

bash pull_locales.sh
python3 ./manage.py make_messages -a
