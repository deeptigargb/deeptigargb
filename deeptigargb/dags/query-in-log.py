from airflow import DAG
#from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime
import logging

default_args = {
    "start_date" : datetime(2020,1,1),
    "owner" : "deepti"
}

with DAG(dag_id='query-to-log', schedule_interval='@daily', default_args=default_args) as dag:
    first_subdag = BashOperator(task_id='first_sub_dag',  bash_command="date")

    logging.info('This is my first time run')