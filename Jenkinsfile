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
                    
                    // FIXED: Added '--format AUTO' so Databricks doesn't think it's a zip file
                    bat 'databricks workspace import /Shared/CI-CD/app.py --file app.py --format AUTO --overwrite'
                    bat 'databricks workspace import /Shared/CI-CD/requirements.txt --file requirements.txt --format AUTO --overwrite'
                    
                    echo 'Deployment Successful! Files are now in Databricks.'
                }
            }
        }
    }
}
