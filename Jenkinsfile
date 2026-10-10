// Job 1: build and push the app image to GHCR.
pipeline {
    agent { label 'built-in' }
    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    environment { IMAGE_NAME = 'ghcr.io/abirami-prabhakar/streakly' }
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Check Docker') {
            steps {
                bat 'docker version'
                bat 'docker info'
            }
        }
        stage('Build Image') {
            steps { bat 'docker build --tag %IMAGE_NAME%:%BUILD_NUMBER% --tag %IMAGE_NAME%:latest .' }
        }
        stage('Push Image to GHCR') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'ghcr-token', usernameVariable: 'GHCR_USER', passwordVariable: 'GHCR_TOKEN')]) {
                    powershell '''
                        $ErrorActionPreference = 'Stop'
                        $dockerConfigPath = Join-Path $env:WORKSPACE '.docker-ci'
                        New-Item -ItemType Directory -Path $dockerConfigPath -Force | Out-Null
                        try {
                            $env:GHCR_TOKEN | docker --config $dockerConfigPath login ghcr.io --username $env:GHCR_USER --password-stdin
                            if ($LASTEXITCODE -ne 0) { throw 'GHCR login failed' }
                            docker --config $dockerConfigPath push "${env:IMAGE_NAME}:${env:BUILD_NUMBER}"
                            if ($LASTEXITCODE -ne 0) { throw 'Versioned image push failed' }
                            docker --config $dockerConfigPath push "${env:IMAGE_NAME}:latest"
                            if ($LASTEXITCODE -ne 0) { throw 'Latest image push failed' }
                        } finally {
                            Remove-Item -LiteralPath (Join-Path $dockerConfigPath 'config.json') -Force -ErrorAction SilentlyContinue
                        }
                    '''
                }
            }
        }
    }
    post {
        success { echo "Published ${env.IMAGE_NAME}:${env.BUILD_NUMBER} and :latest" }
        failure { echo 'Image job failed. Check Console Output.' }
    }
}
