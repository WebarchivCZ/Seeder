#!/usr/bin/env bash

# Make Bash Great Again
set -o errexit # exit when a command fails.
set -o nounset # exit when using undeclared variables
set -o pipefail # catch non-zero exit code in pipes
# set -o xtrace # uncomment for bug hunting

# Pull latest published image
docker-compose -f /home/ansible/seeder/docker-compose-{{ env }}.yml -p seeder pull vyvoj
# Update vyvoj service
docker-compose -f /home/ansible/seeder/docker-compose-{{ env }}.yml -p seeder up -d vyvoj