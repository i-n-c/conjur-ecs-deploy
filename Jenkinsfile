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
  }

    post {
    always {
      cleanupAndNotify(currentBuild.currentResult)
    }
  }
}
