#!/usr/bin/env groovy

pipeline {
  agent {
    label 'CENM_RHEL7_GE_e2e_33'
  }
  environment {
    imagerepo = 'armdocker.rnd.ericsson.se/proj-eric-enm-resource-configuration-data'
    server_image = 'server'
    server_internal_image = 'server_internal'
    generator_image = 'generator'
    gerrit_username = 'RCDEICUSR1'
    gerrit_password_encrypted = 'gAAAAABkt8SVuBzERs-UEYSH5064aphU4bQfbiFFEI0sRm1wuA8ScyQQz9WZfTnNi9ghmVEufSvQhM-sGxyTtJX0VAg-gx-ZgSajVQJBJeWParjONFYAjeo='
    fe_versiontag = sh (
      script: 'sed -n -r "s/\\s*version: \'([^\\\']*)\'.*/\\1/p" web/src/model/versionHistory.js | tail -1',
      returnStdout: true
    ).trim()
    gen_versiontag = sh (
      script: 'python gen/_version.py',
      returnStdout: true
    ).trim()
  }
  stages {
    stage('Inject Credential Files') {
      steps {
        withCredentials([file(credentialsId: 'lciadm100-docker-auth', variable: 'dockerConfig')]) {
          sh "install -m 600 ${dockerConfig} ${HOME}/.docker/config.json"
        }
      }
    }
    stage('Checkout RCD Repository') {
      steps {
        git branch: 'master',
            url: 'ssh://gerrit-gamma.gic.ericsson.se:29418/OSS/ENM-Parent/SQ-Gate/com.ericsson.oss.containerisation/eric-enm-resource-configuration-data'
      }
    }
    stage('Check for changes in front end and generator.') {
      steps {
        script {
          env.fe_changes=sh (
            script: "/proj/ciexadm200/tools/git/2.20.0/bin/git diff origin/master fe_release --stat -- web/src/",
            returnStdout: true
          ).trim()
        }
        script{
          env.generator_changes=sh (
            script: "/proj/ciexadm200/tools/git/2.20.0/bin/git diff origin/master generator_release --stat -- gen/ ':(exclude)gen/test/*' ':(exclude)gen/container/*' ':(exclude)gen/test_resources/*'",
            returnStdout: true
          ).trim()
        }
      }
    }
    stage('Build RCD front end Docker image') {
      when {
        expression { env.fe_changes }
      }
      steps {
        dir ('web') {
          sh 'docker build -f container/runtime.Dockerfile -t ${imagerepo}/${server_image}:$fe_versiontag .'
          sh 'echo  VITE_APP_ENV_TYPE=pdu >> .env'
          sh 'docker build -f container/runtime.Dockerfile -t ${imagerepo}/${server_internal_image}:$fe_versiontag .'
          sh 'rm -f .env'
        }
      }
    }
    stage('Build RCD generator Docker image') {
      when {
        expression { env.generator_changes }
      }
      steps {
        sh 'docker build -f gen/container/Dockerfile --build-arg GERRIT_USERNAME=${gerrit_username} --build-arg GERRIT_PASSWORD_ENCRYPTED=${gerrit_password_encrypted} -t ${imagerepo}/${generator_image}:$gen_versiontag .'
      }
    }
    stage('Trivy Scan report'){
      steps {
        script{
          // added || true to make sure pipeline passes eventhought trivy throws error "/entrypoint.sh: line 10: trivy_metadata.properties: Permission denied"
          sh 'docker run --user $(id -u):$(id -g)   $(for x in $(id -G); do printf " --group-add %s" "$x"; done)   -v /var/run/docker.sock:/var/run/docker.sock   -v ${WORKSPACE}/:/mnt --rm armdocker.rnd.ericsson.se/proj-adp-cicd-drop/trivy-inline-scan:latest  ${imagerepo}/${generator_image}:$gen_versiontag || true'
          sh 'docker run --user $(id -u):$(id -g)   $(for x in $(id -G); do printf " --group-add %s" "$x"; done)   -v /var/run/docker.sock:/var/run/docker.sock   -v ${WORKSPACE}/:/mnt --rm armdocker.rnd.ericsson.se/proj-adp-cicd-drop/trivy-inline-scan:latest  ${imagerepo}/${server_image}:$fe_versiontag || true'
        }
      }
    }
    stage('Push RCD front end Docker image to Artifactory') {
      when {
        expression { env.fe_changes }
      }
      steps {
        sh '''
          docker push ${imagerepo}/${server_image}:$fe_versiontag
          docker push ${imagerepo}/${server_internal_image}:$fe_versiontag
          git tag --annotate --message 'Release front end ${fe_versiontag}' --force fe_release HEAD
          git push --force origin fe_release
        '''
      }
    }
    stage('Push RCD generator Docker image to Artifactory') {
      when {
        expression { env.generator_changes }
      }
      steps {
        sh '''
          docker push ${imagerepo}/${generator_image}:$gen_versiontag
          git tag --annotate --message 'Release front end ${gen_versiontag}' --force generator_release HEAD
          git push --force origin generator_release
        '''
      }
    }
    stage('Publish changes to RCD VM') {
      steps{
        script{
          withCredentials([usernamePassword(credentialsId: 'rcduser1', passwordVariable: 'pass', usernameVariable: 'user')]) {
            def remote = [:]
            remote.name = 'seliius20096'
            remote.host = 'seliius20096.seli.gic.ericsson.se'
            remote.user = user
            remote.password = pass
            remote.allowAnyHosts = true
            stage('Run rcd_update.sh on RCD VM') {
              sshPut remote: remote, from: 'rcd_update.sh', into: '/rcd/'
              sshCommand remote: remote, sudo: true, command: "bash -c '/rcd/rcd_update.sh -g ${gen_versiontag} -f ${fe_versiontag}'"
            }
          }
        }
      }
    }
  }
}
