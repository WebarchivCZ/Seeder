from fabric.api import local, cd, run, env, prefix, task


@task(alias='rns')
def runserver():
    local('./manage.py runserver')


@task(alias='sdb')
def syncdb():
    local('./manage.py syncdb --noinput')
    local('./manage.py migrate')


@task(alias='sm')
def schemamigration():
    local('./manage.py schemamigration core --auto')
    local('git add core/migrations/')
    local('./manage.py migrate')


@task(alias='cs')
def collect_static():
    run('../manage.py collectstatic --noinput')


@task(alias='s')
def shell():
    run('./manage.py shell')