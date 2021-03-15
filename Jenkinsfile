pipeline {
  agent { label 'executor-v2' }

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '30'))
  }

  triggers {
    cron(getDailyCronString())
  }

  stages {
    stage('Lint'){
      steps {
        sh 'scripts/lint'
      }
    }
    stage('Smoke Test'){
      environment {
        STACK_NAME = "ecsdeployci${BRANCH_NAME.replaceAll("[^A-Za-z0-9]", "").take(6)}${BUILD_NUMBER}"
      }
      steps {
        sh 'summon -f scripts/secrets.yml scripts/prepare'
        sh 'summon -f scripts/secrets.yml scripts/deploy'
        // Summon not needed for exercise as it only uses the conjur api
        // not the AWS api
        sh 'scripts/exercise'
      }
      post {
        always {
          archiveArtifacts(artifacts: 'params.json')
          archiveArtifacts(artifacts: 'admin_password_meta.json', allowEmptyArchive: true)
          archiveArtifacts(artifacts: 'stack_*.json')
          archiveArtifacts(artifacts: '*.log', allowEmptyArchive: true)
          sh 'summon -f scripts/secrets.yml scripts/cleanup'
        }
      }
    }
  }

    post {
    always {
      cleanupAndNotify(currentBuild.currentResult)
    }
  }
}
