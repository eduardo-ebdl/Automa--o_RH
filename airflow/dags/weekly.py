from __future__ import annotations

from pendulum import datetime
from airflow.decorators import dag
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'Automation Team',
    'retries': 3
}
@dag(
    schedule='@weekly',
    tags=['weekly', 'automation', 'email'],
    start_date=datetime(2023, 1, 1),
    catchup=False,
    default_args=default_args,
    description="This dag runs weekly email automations.",
)
def weekly_dag():
    """
    ### Weekly DAG Documentation
    This is the main function for the weekly DAG.
    """
    run_individual = BashOperator(
        task_id="run_consolidated_manager",
        bash_command="PYTHONPATH=/usr/local/airflow/ python /usr/local/airflow/automations/weekly/w1_consolidated_manager.py"
    )

    run_anniversary = BashOperator(
        task_id="run_consolidated_coordinator",
        bash_command="PYTHONPATH=/usr/local/airflow/ python /usr/local/airflow/automations/weekly/w2_consolidated_coordinator.py"
    )

weekly_dag()
