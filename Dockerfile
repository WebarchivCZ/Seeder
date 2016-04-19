FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    libpq-dev \
    memcachedb \
    python-dev \
    python-pip \
    libmysqlclient-dev \
    python-psycopg2 \
    git-core \
    python3-pip\
    gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ADD . /code
WORKDIR /code

RUN pip3 install -r requirements.txt --upgrade
RUN pip3 install -r requirements_dev.txt --upgrade
RUN python3 /code/Seeder/manage.py collectstatic --noinput