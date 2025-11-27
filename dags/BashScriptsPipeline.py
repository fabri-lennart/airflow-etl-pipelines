import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="my_bash_dag",
    start_date=pendulum.datetime(2025, 1, 12, tz="UTC"),
    catchup=False,
    tags=["BashScripts"],
) as dag:
    # Task to execute a simple bash command
    run_hello_command = BashOperator(
        task_id="hello_bash",
        bash_command='echo "Hello from BashOperator!"',
    )

    # Task to execute a multi-line bash command
    run_multi_line_command = BashOperator(
        task_id="multi_line_bash",
        bash_command="""
            echo "This is the first line."
            sleep 2
            echo "This is the second line after a delay."
        """,
    )

    # Define task dependencies
    run_hello_command >> run_multi_line_command
