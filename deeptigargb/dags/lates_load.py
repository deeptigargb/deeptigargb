from typing import Optional
from google.cloud import bigquery
from datetime import datetime, timedelta
import time
import os
import pathlib
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.file_to_gcs import FileToGoogleCloudStorageOperator

project = 'data-dev-239410'
bq_conn_id='bigquery_primary'


def get_bigquery_client(
        bq_conn_id: str,
        bq_location: str,
        bq_project: Optional[str] = None,
) -> bigquery.Client:
    return bigquery.Client(
        project=bq_project
    )


def list_of_datasets(client, project):
    union_query = ''
    client = get_bigquery_client(
        bq_project=project,
        bq_conn_id='bigquery_primary',
        bq_location='europe-west2',
    )
    print("inside list_of_datasets")
    print("here is the list of datasets ", list(client.list_datasets()))
    for dataset in list(client.list_datasets()):
        print("dataset ",dataset.dataset_id)
        if 'insights_domain' in dataset.dataset_id:
            single_query = f'SELECT * FROM `{project}.{dataset.dataset_id}.__TABLES__` union all '
            union_query = union_query + single_query
    return union_query


def build_html_report(path_file):
    client = get_bigquery_client(
        bq_project=project,
        bq_conn_id='bigquery_primary',
        bq_location='europe-west2',
    )
    print("inside task")
    union_query = list_of_datasets(client, project)
    print("union_query ",union_query)
    final_query = 'with all_tables as ( ' + union_query.rstrip(
        "union all") + ') select project_id, dataset_id, table_id,' \
                       'last_modified_time, timestamp_millis(last_modified_time ) as ' \
                       'last_modified from all_tables order by last_modified'
    print("final_query ", final_query)
    df = client.query(final_query).to_dataframe()
    print("here is the head ",path_file )
    print("here is the path ", pathlib.Path(__file__))
    time_diff = ((time.time() * 1000) - df['last_modified_time'])
    days = (time_diff / (1000 * 60 * 60 * 24)).astype('int64')
    hours = ((time_diff / (1000 * 60 * 60)) % 24).astype('int64')
    df['Time Difference in days'] = days.astype(str) + ' days, ' + hours.astype(str) + 'hours'
    print("creating html")
    final_path = os.path.join(path_file, 'latest_domain_tables_load.html')
    print("final ",final_path)

    with open(final_path, 'w') as f:
        f.write(df.to_html())


head, tail = os.path.split(pathlib.Path(__file__))

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 9, 1),
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

with DAG(dag_id='latest_domain_load_report', schedule_interval='*/1 * * * *', default_args=default_args) as dag:
    build_html = PythonOperator(
        task_id='build_html_report',
        python_callable=build_html_report,
        op_kwargs={
            'path_file': head
        },
        dag=dag,
    )

    gcp_operator = FileToGoogleCloudStorageOperator(
        task_id='gcp_task',
        src=os.path.join(head, 'latest_domain_tables_load.html'),
        dst='dap/latest_domain_tables_load.html',
        bucket='data-dev-239410',
        google_cloud_storage_conn_id=bq_conn_id,
        mime_type='Folder',
        dag=dag
    )
    build_html >> gcp_operator
