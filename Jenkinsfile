pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    stages {
        stage('Cloning from github..') {
            steps {
                script {
                    echo 'Cloning from github..'
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'github-token',
                            url: 'https://github.com/Reshendraraj/MLOPS-project-2-Recommndersystem.git'
                        ]]
                    )
                }
            }
        }

        stage('Making virtual environment..') {
            steps {
                script {
                    echo 'Making virtual environment..'
                    bat '''
                    python -m venv ${VENV_DIR}
                    ${VENV_DIR}\\Scripts\\activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install dvc
                    '''
                }
            }
        }

        stage('DVC Pull...') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'DVC Pull...'
                        bat '''
                        ${VENV_DIR}\\Scripts\\activate
                        dvc pull
                        '''
                    }
                }
            }
        }
    }
}
