pipeline {
    agent any
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        stage('Deploy to Databricks') {
            steps {
                withCredentials([
                    string(credentialsId: 'DATABRICKS_HOST', variable: 'DATABRICKS_HOST'),
                    string(credentialsId: 'DATABRICKS_TOKEN', variable: 'DATABRICKS_TOKEN')
                ]) {
                    bat 'databricks workspace mkdirs /Shared/CI-CD'
                    bat 'databricks workspace import app.py /Shared/CI-CD/app.py --overwrite'
                    bat 'databricks workspace import requirements.txt /Shared/CI-CD/requirements.txt --overwrite'
                    echo 'Deployment Successful!'
                }
            }
        }
    }
}
