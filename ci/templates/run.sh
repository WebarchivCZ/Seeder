#!/usr/bin/env bash

# Make Bash Great Again
set -o errexit # exit when a command fails.
set -o nounset # exit when using undeclared variables
set -o pipefail # catch non-zero exit code in pipes
# set -o xtrace # uncomment for bug hunting

docker compose -f /home/ansible/seeder/docker-compose-{{ env }}.yml -p seeder pull
# We do not want to fail run script if there is no running web or static container, otherwise we would have to create run and update script separately.
docker compose -f /home/ansible/seeder/docker-compose-{{ env }}.yml -p seeder rm --stop --force web static 2>&1 || /bin/true
# Dtto for static volume
docker volume rm seeder_static 2>&1 || /bin/true
docker compose -f /home/ansible/seeder/docker-compose-{{ env }}.yml -p seeder up -d