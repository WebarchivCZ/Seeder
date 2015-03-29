from fabric.api import local, cd, run, env, prefix, task


@task(alias='rns')
def runserver():
    local('./manage.py runserver')


@task(alias='sdb')
def syncdb():
    """
    There is some weird bug in 1.8 that requires auth module to be migrated
    before anything else...
    """
    local('./manage.py migrate auth')
    local('./manage.py migrate core')
    local('./manage.py migrate')


@task(alias='sm')
def schemamigration():
    local('./manage.py schemamigration core --auto')
    local('git add core/migrations/')
    local('./manage.py migrate')


@task(alias='cs')
def collect_static():
    local('./manage.py bower_install')
    local('./manage.py collectstatic --noinput')


@task(alias='s')
def shell():
    local('./manage.py shell')