from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime
import logging

# from deeptigargb.dags.slack_hook import task_fail_slack_alert
from airflow.hooks.base_hook import BaseHook
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator
from functools import partial

SLACK_CONN_ID = 'domain_slack'


def task_fail_slack_alert(context):
    slack_webhook_token = BaseHook.get_connection(SLACK_CONN_ID).password
    slack_msg = """
            :red_circle: Task Failed again. 
            *Task_id*: {task}  
            *Dag*: {dag} 
            *Execution Time*: {exec_date}  
            *Log Url*: {log_url} 
            """.format(
        task=context.get('task_instance').task_id,
        dag=context.get('task_instance').dag_id,
        ti=context.get('task_instance'),
        exec_date=context.get('execution_date'),
        log_url=context.get('task_instance').log_url,
    )
    failed_alert = SlackWebhookOperator(
        task_id='slack_test',
        http_conn_id='domain_slack',
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username='airflow')
    return failed_alert.execute(context=context)


default_args = {
    "start_date": datetime(2020, 1, 1),
    "owner": "airflow",
    'retries': 0
}

with DAG(dag_id='slack_integrate', schedule_interval='@daily', default_args=default_args) as dag:
    second_subdag = BashOperator(task_id='second_sub_dag', bash_command="date1",
                                 on_failure_callback=partial(task_fail_slack_alert))
    #raise Exception('hello there, this is just a funny error')


    logging.info('This is my first time run')
