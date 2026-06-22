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
                    
                    // FIXED: Naye CLI version ke hisaab se commands update kar diye
                    bat 'databricks workspace import /Shared/CI-CD/app.py --file app.py --overwrite'
                    bat 'databricks workspace import /Shared/CI-CD/requirements.txt --file requirements.txt --overwrite'
                    
                    echo 'Deployment Successful! Files are now in Databricks.'
                }
            }
        }
    }
}
