from __future__ import annotations

from pendulum import datetime
from airflow.decorators import dag
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'Automation Team',
    'retries': 3
}
@dag(
    schedule='@daily',
    tags=['daily', 'automation', 'email'],
    start_date=datetime(2023, 1, 1),
    catchup=False,
    default_args=default_args,
    description="This dag runs daily email automations.",
)
def daily_dag():
    """
    ### Daily DAG Documentation
    This is the main function for the daily DAG.
    """
    run_individual = BashOperator(
        task_id="run_individual_colab",
        bash_command="PYTHONPATH=/usr/local/airflow/ python /usr/local/airflow/automations/daily/d1_individual_contributor.py"
    )

    run_anniversary = BashOperator(
        task_id="run_anniversary_colab",
        bash_command="PYTHONPATH=/usr/local/airflow/ python /usr/local/airflow/automations/daily/d4_work_anniversary.py"
    )

daily_dag()