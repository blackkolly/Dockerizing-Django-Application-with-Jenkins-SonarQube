pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }
    
    environment {
        DOCKER_IMAGE = 'blackkolly/sample-app'
        DOCKERHUB_CREDENTIALS = credentials('docker-hub-credentials')
        GIT_REPO = 'https://github.com/blackkolly/Dockerizing-Django-Application-with-Jenkins-SonarQube.git'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                url: env.GIT_REPO,
                credentialsId: 'github-credentials'
            }
        }
        
        stage('Setup Python') {
            steps {
                sh '''
                python -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }
        
        stage('Lint & Test') {
            steps {
                sh '''
                . venv/bin/activate
                flake8 . --count --show-source --statistics
                python manage.py test --noinput --parallel
                coverage run --source='.' manage.py test
                coverage xml
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${BUILD_NUMBER}")
                }
            }
        }
        
        stage('SonarQube Analysis') {
            when {
                branch 'main'
            }
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                    sonar-scanner \
                    -Dsonar.projectKey=django-sample-app \
                    -Dsonar.sources=. \
                    -Dsonar.python.coverage.reportPaths=coverage.xml
                    '''
                }
            }
        }
        
        stage('Push to Docker Hub') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-credentials') {
                        docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}").push()
                        docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}").push('latest')
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
            script {
                sh 'docker system prune -f || true'
            }
        }
    }
}
