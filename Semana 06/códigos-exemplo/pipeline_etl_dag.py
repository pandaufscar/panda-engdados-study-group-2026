import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator


SCRIPTS_DIR = Path("/opt/airflow/scripts")
sys.path.append(str(SCRIPTS_DIR))

from pipeline_etl import extract, load, transform


with DAG(
    dag_id="pipeline_etl",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(seconds=10),
    },
) as dag:
    extrair = PythonOperator(
        task_id="extrair",
        python_callable=extract,
    )

    transformar = PythonOperator(
        task_id="transformar",
        python_callable=transform,
    )

    carregar = PythonOperator(
        task_id="carregar",
        python_callable=load,
    )

    extrair >> transformar >> carregar
