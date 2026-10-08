pipeline {
    agent any

    stages {

        stage('Install Dependencies') {
            steps {
                sh 'python3 -m venv jenkins-venv'
                sh './jenkins-venv/bin/pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh './jenkins-venv/bin/pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t hospital-appointment:jenkins .'
            }
        }
    }
}
