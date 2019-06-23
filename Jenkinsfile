pipeline {
  agent any
    stages {
      stage('Build images and push them to Dockerhub') {
        anyOf { branch 'master'; branch 'production'; branch 'jenkins'}
        steps {
          sh '''#!/usr/bin/env bash
            docker build -t webarchiv/seeder:develop -t webarchiv/seeder:latest -t webarchiv/seeder:$(git rev-parse --short HEAD) .
            docker push webarchiv/seeder:develop
            docker push webarchiv/seeder:$(git rev-parse --short HEAD)
          '''
        }
      }
      stage('Deploy to test') {
        when {
          anyOf { branch 'master'; branch 'jenkins'}
        }
        steps {
          sh '''#!/usr/bin/env bash
            cd ci
            ansible-playbook -i test prepare-configuration.yml
            docker-compose -f docker-compose-test.yml -p seeder up -d
          '''
        }
      }
      stage('Deploy to production') {
        when {
          anyOf { branch 'production'}
        }
        steps {
          input "Přísáhám před krutým a přísným bohem, že https://app.webarchiv.cz je v perfektním stavu a stvrzuji, že může jít do produkce na https://webarchiv.cz."
          sh '''#!/usr/bin/env bash
            docker push webarchiv/seeder:latest
            cd ci
            ansible-playbook -i prod prepare-configuration.yml
            echo SSH into machine and run compose there.
          '''
        }
      }
    }
}
