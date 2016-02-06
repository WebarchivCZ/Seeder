Deploying
=========

Deploying takes care of installing PIP packages, installing js packages and
static files collecting.

Manual
------

You need to run following commands: ::

    $ git pull
    $ pip install -R requirements.txt -U
    $ ./manage.py migrate
    $ tx pull -a
    $ ./manage.py compilemessages
    $ ./manage.py collectstatic


Using Fabric
------------
Local deploying can be executed server-side from seeder directory.
To do this simply type (with active ``seeder`` virtualenv!) ::

    seeder/Seeder $ fab deploy_locally

