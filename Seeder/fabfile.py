from fabric.api import local, task, run


commands = {
    'runserver': ['./manage.py runserver'],
    'syncdb': [
        './manage.py migrate auth',
        './manage.py syncdb --noinput',
        './manage.py migrate'],
    'static': [
        './<manage.py bower_install>',
        './manage.py collectstatic --noinput'],
    'pull': ['git pull --rebase']
}


@task(alias='rns')
def runserver():
    map(local, commands['runserver'])


@task(alias='sdb')
def syncdb():
    map(local, commands['syncdb'])


@task(alias='sm')
def schemamigration():
    local('./manage.py makemigrations core')
    local('git add core/migrations/')
    local('./manage.py migrate')


@task(alias='cs')
def collect_static():
    map(local, commands['static'])


@task(alias='s')
def shell():
    local('./manage.py shell')


@task(alias='dl')
def deploy_locally():
    map(local, commands['pull'] + commands['syncdb'] + commands['static'])


@task(alias='d')
def deploy():
    map(run, commands['pull'] + commands['syncdb'] + commands['static'])
