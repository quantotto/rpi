node {
    def GIT_REV

    def VERSION = '2.11.0'

    stage('Clone repository') {
        /* Let's make sure we have the repository cloned to our workspace */

        checkout([$class: 'GitSCM',
                  branches: [[name: '*/master']],
                  doGenerateSubmoduleConfigurations: false,
                  extensions: [[$class: 'SubmoduleOption',
                                disableSubmodules: false,
                                parentCredentials: true,
                                recursiveSubmodules: true,
                                reference: '',
                                trackingSubmodules: false]],
                  submoduleCfg: [],
                  userRemoteConfigs: [[url: 'git@github.com:quantotto/rpi.git']]])
    }

    stage('RPI Image build') {
        sh """export VIRTUAL_ENV=/var/lib/jenkins/.venv
        export PATH="${VIRTUAL_ENV}/bin:${PATH}"
        python build.py --base-image-file /var/lib/jenkins/2020-11-11-Raspbian-lite.img
        chmod ugo+r out"""
    }
}
