FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    libpq-dev \
    memcachedb \
    python3-dev \
    libmysqlclient-dev \
    python-psycopg2 \
    git-core \
    python3-pip\
    gettext \
    cron \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ADD . /code
WORKDIR /code

RUN pip3 install -r requirements.txt --upgrade

ENV DJANGO_SETTINGS_MODULE=settings.env
RUN python3 /code/Seeder/manage.py collectstatic --noinput
RUN unset DJANGO_SETTINGS_MODULE
