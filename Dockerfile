FROM python:3.7.3

# Debian Stretch is no longer supported, so need to use archive sources
RUN echo "deb http://archive.debian.org/debian/ stretch main\n\
deb-src http://archive.debian.org/debian/ stretch main" > /etc/apt/sources.list

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

# Create default log file for cron
RUN touch /var/log/cron.log

RUN pip3 install -r requirements.txt --upgrade

RUN export DJANGO_SETTINGS_MODULE=settings.env \
    && python3 /code/Seeder/manage.py collectstatic --noinput --clear \
    && unset DJANGO_SETTINGS_MODULE

EXPOSE 8000
