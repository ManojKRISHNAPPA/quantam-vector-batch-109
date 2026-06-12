pipeline {
  agent any

  stages{
    stage('hostanme'){
      steps{
        sh '''
          echo "this to get the hostname"
          hostname
        '''
      }
    }
    stage('date'){
      steps{
        sh '''
          echo "this to get the current date"
          date
        '''
      }
    }
    stage('memory'){
      steps{
        sh '''
          echo "this to get the memory"
          free -h
        '''
      }
    }
    stage('active process -running '){
      steps{
        sh '''
          echo "this to get the active process"
          ps -aux | head -10
        '''
      }
    }    
  }
}