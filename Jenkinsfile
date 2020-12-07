pipeline {
  agent any
    stages {
      stage('Build images and push them to Dockerhub') {
        when {
          anyOf { branch 'master'; branch 'production'; branch 'feature/*' }
        }
        steps {
          sh '''#!/usr/bin/env bash
            # Make Bash Great Again
            set -o errexit # exit when a command fails.
            set -o nounset # exit when using undeclared variables
            set -o pipefail # catch non-zero exit code in pipes
            # set -o xtrace # uncomment for bug hunting

            docker build -t webarchiv/seeder:develop -t webarchiv/seeder:latest -t webarchiv/seeder:$(git rev-parse --short HEAD) .
            docker push webarchiv/seeder:develop
            docker push webarchiv/seeder:$(git rev-parse --short HEAD)
          '''
        }
      }
      stage('Deploy to test') {
        when {
          anyOf { branch 'master'; branch 'production'; branch 'feature/*' }
        }
        steps {
          sh '''#!/usr/bin/env bash
            # Make Bash Great Again
            set -o errexit # exit when a command fails.
            set -o nounset # exit when using undeclared variables
            set -o pipefail # catch non-zero exit code in pipes
            # set -o xtrace # uncomment for bug hunting

            cd ci
            ansible-playbook -i test prepare-configuration.yml
            docker-compose -f docker-compose-test.yml -p seeder pull
            docker-compose -f docker-compose-test.yml -p seeder rm --stop --force web static
            docker volume rm seeder_static
            docker-compose -f docker-compose-test.yml -p seeder up -d
          '''
        }
      }
      stage('Deploy to production') {
        when {
          anyOf { branch 'production'}
        }
        environment {
                SSH_CREDS = credentials('ansible')
        }
        steps {
          input "Přísáhám před krutým a přísným bohem, že https://app.webarchiv.cz je v perfektním stavu a stvrzuji, že může jít do produkce na https://webarchiv.cz."
          sh '''#!/usr/bin/env bash
            # Make Bash Great Again
            set -o errexit # exit when a command fails.
            set -o nounset # exit when using undeclared variables
            set -o pipefail # catch non-zero exit code in pipes
            # set -o xtrace # uncomment for bug hunting

            docker push webarchiv/seeder:latest
            cd ci
            ansible-playbook -i prod --private-key ${SSH_CREDS} -u ${SSH_CREDS_USR} prepare-configuration.yml
            # I had issues witch docker_compose module in ansible. Thus implmentation in ssh as workaround.
            ssh -o "StrictHostKeyChecking=no" -i ${SSH_CREDS} ${SSH_CREDS_USR}@10.3.0.50 docker-compose -f docker-compose-prod.yml -p seeder pull
            ssh -o "StrictHostKeyChecking=no" -i ${SSH_CREDS} ${SSH_CREDS_USR}@10.3.0.50 docker-compose -f docker-compose-prod.yml -p rm --stop --force web static
            ssh -o "StrictHostKeyChecking=no" -i ${SSH_CREDS} ${SSH_CREDS_USR}@10.3.0.50 docker volume rm seeder_static
            ssh -o "StrictHostKeyChecking=no" -i ${SSH_CREDS} ${SSH_CREDS_USR}@10.3.0.50 docker-compose -f docker-compose-prod.yml -p seeder up -d
          '''
        }
      }
    }
}
