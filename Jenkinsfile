pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'yourdockerhubuser/flask-s3-app:${BUILD_NUMBER}'  // đổi thành Docker Hub của bạn
        AWS_ACCESS_KEY_ID = credentials('AKIA2ELEWHODST3YCRSU')             // cấu hình trong Jenkins Credentials
        AWS_SECRET_ACCESS_KEY = credentials('KyPmNYjusY94DAGlL58Ho7dFgDxTFTZD4b19QBBI')
        S3_BUCKET_NAME = 'myflaskbucket2025'
        S3_REGION = 'ap-northeast-1'
    }

    stages {
        stage('Clone source') {
            steps { git 'https://github.com/yourrepo/your-flask-app.git' }
        }
        stage('Build Docker image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}")
                }
            }
        }
        stage('Push Docker image') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                        docker.image("${DOCKER_IMAGE}").push()
                    }
                }
            }
        }
        stage('Deploy/Restart container') {
            steps {
                // Stop & remove old container, run container mới từ image vừa build
                sh '''
                docker stop flask-s3-app || true
                docker rm flask-s3-app || true
                docker run -d \
                  --name flask-s3-app \
                  -p 5000:5000 \
                  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
                  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
                  -e S3_BUCKET_NAME=$S3_BUCKET_NAME \
                  -e S3_REGION=$S3_REGION \
                  ${DOCKER_IMAGE}
                '''
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
