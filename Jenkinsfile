pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Deploy Full Project to Databricks') {
            steps {
                withCredentials([
                    string(credentialsId: 'DATABRICKS_HOST', variable: 'DATABRICKS_HOST'),
                    string(credentialsId: 'DATABRICKS_TOKEN', variable: 'DATABRICKS_TOKEN')
                ]) {
                    
                    // 1. Create a new main folder for the whole project
                    bat 'databricks workspace mkdirs /Shared/banklens-platform2'
                    
                    // 2. Sync the ENTIRE repository (.) into that Databricks folder
                    // Note: We add /Workspace at the front because the 'sync' command requires it
                    bat 'databricks sync . /Workspace/Shared/banklens-platform2'
                    
                    echo 'Full Banklens Platform Deployment Successful!'
                }
            }
        }
    }
}
