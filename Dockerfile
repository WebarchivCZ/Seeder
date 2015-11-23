FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    libpq-dev \
    memcachedb \
    python-dev \
    python-pip \
    libmysqlclient-dev \
    python-psycopg2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ADD . /code
WORKDIR /code
