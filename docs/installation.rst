Installation
============

Prerequisites:
--------------

 - python 2.7
 - PostgreSQL
 - `PIP <https://pip.pypa.io/en/latest/installing.html>`_
 - nginx
 - virtualenv
 - supervisor
 - uwsgi
 - python psycopg2 driver


Virtualenv
----------

Virtualenv is something like chroot for python libraries.
Installation instructions: https://virtualenv.pypa.io/en/latest/installation.html .
Then create virtualenv seeder: ``$virtualenv seeder``
You have to activate it every time before using python:
``source seeder/bin/activate``.


Configuration
-------------

Firstly create `Seeder/settings/local_settings.py` according to template
`Seeder/settings/local_settings.template.py`.

Then:

 - set secret key, that should be something long and random
 - set debugs to ``False`` for security reasons
 - set allowed host variable - put there your domain name
 - finally set the database username and password

Read more about settings at: https://docs.djangoproject.com/en/1.8/ref/settings/


nginx
-----

After installing and configuring nginx create config file similar to `template.nginx.conf` in
``/etc/nginx/sites-available/`` and make a link to it in ``/etc/nginx/sites-enabled``.


uwsgi
-----
Put something like `template.uwsgi.conf` to ``/etc/uwsgi/apps-available/``.
and link to it from ``/etc/uwsgi/apps-enabled/``.


supervisor
----------
Put something like `template.supervisor.conf` to ``/etc/supervisor/conf.d/``.


Cron
----

You need to run ``python manage.py runcrons`` periodically, this commands runs periodical tasks that takes care of various thins - screenshots,
postponed voting rounds, expiring contracts...

So put something like ::

    0 * * * * source <virtualenv>/bin/activate && python <seeder>Seeder/manage.py runcrons > <log_path>/django_cron.log



Final restart
-------------

After configuring all of the above lets restart servers ::

    $ sudo service supervisor restart
    $ sudo service nginx restart

The proceed with deploying.