Docker Compose
==============

For developing purposes you can use ``docker-compose`` which creates
various dockers and networks them together. This setup in not secure and
database might get deleted on accident.

Running up the containers ::

    $ docker-compose up

this will run the runserver on localhost port 8000.

You will need to create your super user in order to log in: ::

    $ docker-compose run web ./manage.py createsuperuser

If you need to import data from legacy system put the raw sql file in
``legacy_dumps`` folder and run following command: ::

    $ docker-compose run web ./manage.py legacy_sync

If you add some new requirements you will need to rebuild the images with
``docker-compose build`` command. Even though the command for running the server
will try to install latest requirements it won't affect other dockers so you
will have trouble accessing any manage command.