FROM python:3.8.19

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
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatspi2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ADD . /code
WORKDIR /code

# Create default log file for cron
RUN touch /var/log/cron.log

RUN pip3 install -r requirements.txt --upgrade

# Install Playwright browsers
RUN playwright install chromium

# Export working environment to use in CRON later
RUN export DJANGO_SETTINGS_MODULE=settings.env \
    && printenv | sed 's/\(^[^=]*\)=\(.*\)/\1="\2"/' > /code/.cronenv \
    && python3 /code/Seeder/manage.py collectstatic --noinput --clear \
    && unset DJANGO_SETTINGS_MODULE

EXPOSE 8000
