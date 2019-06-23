pipeline {
  agent any
    stages {
      stage('Build images and push them to Dockerhub') {
        steps {
          sh '''#!/usr/bin/env bash
            docker build -t webarchiv/seeder:develop -t webarchiv/seeder:$(git rev-parse --short HEAD) .
            docker push webarchiv/seeder:develop
            docker push webarchiv/seeder:$(git rev-parse --short HEAD)
          '''
        }
      }
      stage('Deploy to test') {
        steps {
          sh '''#!/usr/bin/env bash
            cd ci
            ansible-playbook -i test prepare-configuration.yml
            docker-compose -f docker-compose-test.yml -p seeder up -d
          '''
          }
      }
     }
}
