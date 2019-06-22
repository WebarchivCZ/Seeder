pipeline {
     agent any
     stages {
          stage('Build images and push them to Dockerhub') {
               steps {
                    sh '''#!/usr/bin/env bash
                      docker build -t webarchiv/seeder:develop -t webarchiv/seeder:$(git rev-parse HEAD) .
                      docker push webarchiv/seeder:develop
                      docker push webarchiv/seeder:$(git rev-parse HEAD)
                    '''
               }
          }
          stage('Second Stage') {
               steps {
                    echo 'Step 2. Second time Hello'
                    echo 'Step 3. Third time Hello'
               }
          }
     }
}
