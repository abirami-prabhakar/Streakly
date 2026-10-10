// Job 1: build and push the app image to GHCR.
pipeline {
    agent { label 'built-in' }
    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    environment {
        IMAGE_NAME = 'ghcr.io/abirami-prabhakar/streakly'
        DOCKER_EXE = 'C:/Users/Abirami Prabhakar/AppData/Local/Programs/DockerDesktop/resources/bin/docker.exe'
        DOCKER_HOST = 'npipe:////./pipe/dockerDesktopLinuxEngine'
    }
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Check Docker') {
            steps {
                bat '"%DOCKER_EXE%" version'
                bat '"%DOCKER_EXE%" info'
            }
        }
        stage('Build Image') {
            steps { bat '"%DOCKER_EXE%" build --tag %IMAGE_NAME%:%BUILD_NUMBER% --tag %IMAGE_NAME%:latest .' }
        }
        stage('Push Image to GHCR') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'ghcr-token', usernameVariable: 'GHCR_USER', passwordVariable: 'GHCR_TOKEN')]) {
                    retry(3) {
                        sleep time: 5, unit: 'SECONDS'
                        powershell '''
                            $ErrorActionPreference = 'Stop'
                            $dockerConfigPath = Join-Path $env:WORKSPACE '.docker-ci'
                            New-Item -ItemType Directory -Path $dockerConfigPath -Force | Out-Null
                            try {
                                $env:GHCR_TOKEN | & $env:DOCKER_EXE --config $dockerConfigPath login ghcr.io --username $env:GHCR_USER --password-stdin
                                if ($LASTEXITCODE -ne 0) { throw 'GHCR login failed' }
                                & $env:DOCKER_EXE --config $dockerConfigPath push "${env:IMAGE_NAME}:${env:BUILD_NUMBER}"
                                if ($LASTEXITCODE -ne 0) { throw 'Versioned image push failed' }
                                & $env:DOCKER_EXE --config $dockerConfigPath push "${env:IMAGE_NAME}:latest"
                                if ($LASTEXITCODE -ne 0) { throw 'Latest image push failed' }
                            } finally {
                                Remove-Item -LiteralPath (Join-Path $dockerConfigPath 'config.json') -Force -ErrorAction SilentlyContinue
                            }
                        '''
                    }
                }
            }
        }
    }
    post {
        success { echo "Published ${env.IMAGE_NAME}:${env.BUILD_NUMBER} and :latest" }
        failure { echo 'Image job failed. Check Console Output.' }
    }
}
