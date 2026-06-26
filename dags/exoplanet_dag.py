from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 1, 1),
    'retries': 1
}

with DAG(
    'exoplanet_pipeline',
    default_args=default_args,
    description='NASA Exoplanet Discovery Pipeline',
    schedule_interval=None,
    catchup=False
) as dag:

    ingest = BashOperator(
        task_id='ingest',
        bash_command='python /opt/airflow/src/ingestion/ingest.py'
    )

    stage = BashOperator(
        task_id='stage',
        bash_command='python /opt/airflow/src/staging/stage_planets.py'
    )

    build_mart = BashOperator(
        task_id='build_mart',
        bash_command='python /opt/airflow/src/mart/build_mart.py'
    )

    ingest >> stage >> build_mart