pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'py -3.11 -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'py -3.11 -m pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t streakly:latest .'
            }
        }
    }

    post {
        success {
            echo 'Streakly pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}