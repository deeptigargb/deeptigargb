"""
Sync Composer bucket dags, plugins and data folders with repo.
Import Airflow variables to environment.

This program is intended to be used by Jenkins only.

Takes 2 positional arguments:
    - 1. region: [uk, ca, us]
    - 2. deployment: [dev, prod]

Example usage:
python3 sync_composer_bucket.py uk dev

Expects a folder structure as follows:
pipelines/
    dags/
        uk/
        us/
        ca/
        sg/
        global1/
        shared/
    plugins/
        uk/
        us/
        ca/
        sg/
        global1/
        shared/
    data/
        uk/
        us/
        ca/
        sg/
        global1/
        shared/

Expects variable json files to be named as follows:
pipelines/data/{region}/variables/variables-{deployment}.json
e.g. pipelines/data/uk/variables/variables-dev.json
"""
import os
import json
import yaml
import subprocess
import sys


def load_manifest():
    try:
        with open('manifest.yml') as stream:
            data = yaml.load(stream, Loader=yaml.FullLoader)
            return data
    except IOError as error:
        print('File error: ' + str(error))


def get_composer_bucket(comp_env):
    print('FETCHING COMPOSER BUCKET FOR %s ENVIRONMENT' % comp_env['COMPOSER_ENV'])
    env_description = yaml.safe_load(
        subprocess.check_output(
            'gcloud composer environments describe $COMPOSER_ENV  \
                --project $GCP_PROJECT \
                --location $COMPOSER_LOCATION;',
            shell=True,
            env={**os.environ, **comp_env}
        )
    )
    return env_description['config']['dagGcsPrefix'].split('/dags')[0]


def get_cmd(airflow_vars):
    import_var_commands = '; '.join([
        f"gcloud composer environments run $COMPOSER_ENV "
        f"--location $COMPOSER_LOCATION "
        f"variables -- --set {k} '{v}'"
        for k, v in airflow_vars.items()
    ])
    return (
        f'echo SYNCING $REGION DAGS IN $GCP_PROJECT PROJECT; '
        # Authenticate and set project
        f'cd pipelines/; '
        # Import dags
        f'echo IMPORTING $REGION DAGS; '
        f'gsutil -m cp -r dags/$REGION $COMPOSER_BUCKET/dags/; '
        # Import plugins
        'echo IMPORTING $REGION PLUGINS; '
        f'gsutil -m cp -r plugins/$REGION $COMPOSER_BUCKET/plugins/; '
    ) + import_var_commands


def authenticate_service_account(comp_env):
    subprocess.check_call(
        'gcloud auth activate-service-account \
        --key-file=/home/jenkins/credentials; \
        gcloud config set project $GCP_PROJECT; ',
        shell=True,
        env={**os.environ, **comp_env}
    )


def get_var_file_path(region: str, deployment: str):
    return f'pipelines/data/{region}/variables/variables-{deployment}.json'


def get_airflow_vars(region: str, deployment: str):
    var_file_path = get_var_file_path(region, deployment)

    with open(var_file_path) as fd:
        airflow_vars = json.load(fd)

    return {
        k: (json.dumps(v) if isinstance(v, dict) else v)
        for k, v in airflow_vars.items()
    }


def run(manifests=load_manifest()):
    region = sys.argv[1]  # Options: uk, us, ca, sg
    deployment = sys.argv[2]  # Options: dev or prod

    try:
        dep_details = manifests['pipelines'][region][deployment]
    except KeyError:
        raise Exception(
            f'Region: "{region}" and/or deployment: "{deployment}" ' +
            'do not exist in manifest.yml'
        )

    airflow_vars = get_airflow_vars(region, deployment)

    for region_folder in [region, 'shared']:
        comp_env = {
            "REGION": region_folder,
            "DEPLOYMENT": deployment,
            "GCP_PROJECT": dep_details['gcp_project'],
            "COMPOSER_ENV": dep_details['composer_environment'],
            "COMPOSER_LOCATION": dep_details['composer_location'],
        }
        authenticate_service_account(comp_env)
        comp_env["COMPOSER_BUCKET"] = get_composer_bucket(comp_env)

        subprocess.check_call(
            get_cmd(airflow_vars),
            shell=True,
            env={**os.environ, **comp_env}
        )

    print("SYNCHRONISING ADDITIONAL PLUGINS")
    subprocess.check_call(
        'gsutil -m cp -r pipelines/plugins/control_plugin $COMPOSER_BUCKET/plugins/',
        shell=True,
        env={**os.environ, **comp_env}
    )
    subprocess.check_call(
        'gsutil -m cp -r pipelines/plugins/sentry_airflow $COMPOSER_BUCKET/plugins/',
        shell=True,
        env={**os.environ, **comp_env}
    )
    subprocess.check_call(
        'gsutil -m cp -r pipelines/plugins/shared/dag_utilities $COMPOSER_BUCKET/plugins/shared/',
        shell=True,
        env={**os.environ, **comp_env}
    )
    print("SYNCHRONISING TEST FOLDER")
    # Import Test folder
    subprocess.check_call(
        'gsutil -m cp -r pipelines/dags/test $COMPOSER_BUCKET/dags/',
        shell=True,
        env={**os.environ, **comp_env}
    )

if __name__ == '__main__':
    run()
