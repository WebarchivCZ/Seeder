FROM python:3.7.3

RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    libpq-dev \
    memcachedb \
    python3-dev \
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

RUN export DJANGO_SETTINGS_MODULE=settings.env \
    && python3 /code/Seeder/manage.py collectstatic --noinput --clear \
    && unset DJANGO_SETTINGS_MODULE

EXPOSE 8000
