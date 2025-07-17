pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'flask-s3-app:${BUILD_NUMBER}'
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        S3_BUCKET_NAME = 'myflaskbucket2025'
        S3_REGION = 'ap-northeast-1'
    }

    stages {
        stage('Clone source') {
            steps {
                git branch: 'main', url: 'https://github.com/1sGu7/LAB9DTDM.git'
            }
        }
        stage('Build Docker image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}")
                }
            }
        }
        stage('Run/Restart container') {
            steps {
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
