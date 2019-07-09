#!/usr/bin/env bash

# Make Bash Great Again
set -o errexit # exit when a command fails.
set -o nounset # exit when using undeclared variables
set -o pipefail # catch non-zero exit code in pipes
# set -o xtrace # uncomment for bug hunting

ansible-playbook -i test prepare-configuration.yml
docker-compose -f docker-compose-test.yml -f docker-compose.override.yml -p seeder up --remove-orphans
