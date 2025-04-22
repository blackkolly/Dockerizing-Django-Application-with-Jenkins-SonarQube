pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }

    environment {
        DOCKER_IMAGE = 'blackkolly/sample-app'
        DOCKERHUB_CREDENTIALS = credentials('docker-hub-credentials')
        GITHUB_CREDENTIALS = credentials('github-credentials')
    }

    stages {
        stage('Checkout') {
            steps {
                git(
                    url: 'https://github.com/blackkolly/Dockerizing-Django-Application-with-Jenkins-SonarQube.git',
                    branch: 'main',
                    credentialsId: 'github-credentials'
                )
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                apt-get update && apt-get install -y --no-install-recommends docker.io
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh 'flake8 . --count --show-source --statistics --max-line-length=120'
            }
        }

        stage('Test') {
            steps {
                sh '''
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
                    -Dsonar.python.coverage.reportPaths=coverage.xml \
                    -Dsonar.exclusions=**/migrations/**,**/static/**,**/templates/**
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

        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sshagent(['staging-server-credentials']) {
                        sh """
                        ssh -o StrictHostKeyChecking=no user@staging-server "
                            docker pull ${DOCKER_IMAGE}:${BUILD_NUMBER} && \
                            docker stop sample-app || true && \
                            docker rm sample-app || true && \
                            docker run -d \
                                --name sample-app \
                                -p 8000:8000 \
                                -e DJANGO_SECRET_KEY=\${SECRET_KEY} \
                                -e DATABASE_URL=\${DATABASE_URL} \
                                -e DJANGO_DEBUG=False \
                                ${DOCKER_IMAGE}:${BUILD_NUMBER}
                        "
                        """
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
        success {
            slackSend(
                color: 'good',
                message: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n${env.BUILD_URL}"
            )
        }
        failure {
            slackSend(
                color: 'danger',
                message: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n${env.BUILD_URL}"
            )
        }
    }
}
