import yaml
import subprocess
import sys


def load_manifest():
    try:
        with open('manifest.yaml') as stream:
            data = yaml.load(stream, Loader=yaml.FullLoader)
            return data
    except IOError as error:
        print('File error: ' + str(error))


def run(manifests=load_manifest()):
    ENV = sys.argv[1]
    for project_env in manifests['pipelines']:
        environment, region = project_env.split('-')
        if environment == ENV:
            print('SYNCING {} DAGS'.format(manifests['pipelines'][project_env]['gcp_project']))
            # Login to gcloud and set the current project
            subprocess.check_call([
                '/usr/local/gcloud/google-cloud-sdk/bin/gcloud',
                'auth activate-service-account',
                '--key-file=/home/jenkins/credentials'

            ])
            subprocess.check_call([
                '/usr/local/gcloud/google-cloud-sdk/bin/gcloud',
                'config set project',
                manifests['pipelines'][project_env]['gcp_project']
            ])
            # import new python dag files
            subprocess.check_call([
                '/usr/local/gcloud/google-cloud-sdk/bin/gcloud',
                'composer',
                'environments',
                'storage',
                'dags',
                'import',
                '--environment',
                manifests['pipelines'][project_env]['composer_environment'],
                '--location',
                manifests['pipelines'][project_env]['composer_location'],
                '--source',
                '/dags'
            ])


run()
