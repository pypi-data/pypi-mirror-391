"""
Example DAG demonstrating various Airflow features
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

# Default arguments
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def print_context(**context):
    """Example Python function"""
    print(f"Execution date: {context['ds']}")
    print(f"DAG run: {context['dag_run']}")
    return "Success!"


# Define DAG
with DAG(
    'example',
    default_args=default_args,
    description='Complete example DAG with various operators',
    schedule=timedelta(days=1),
    catchup=False,
    tags=['example', 'tutorial'],
) as dag:

    # Task: Bash operator
    start = BashOperator(
        task_id='start',
        bash_command='echo "🚀 Starting DAG execution..."',
    )

    # Task: Python operator
    process_data = PythonOperator(
        task_id='process_data',
        python_callable=print_context,
    )

    # Task: Parallel tasks
    parallel_tasks = []
    for i in range(3):
        task = BashOperator(
            task_id=f'parallel_task_{i}',
            bash_command=f'echo "Processing batch {i}..." && sleep 2',
        )
        parallel_tasks.append(task)

    # Task 6: Final task
    end = BashOperator(
        task_id='end',
        bash_command='echo "✅ DAG execution completed successfully!"',
    )

    # Define task dependencies
    start >> process_data
    parallel_tasks >> end


# Example of dynamic task generation
def generate_dynamic_tasks():
    """Example showing how to create tasks dynamically"""
    with DAG(
        'example_dynamic_tasks',
        default_args=default_args,
        description='Example with dynamically generated tasks',
        schedule_interval=None,
        catchup=False,
        tags=['example', 'dynamic'],
    ) as dynamic_dag:

        start = BashOperator(
            task_id='start',
            bash_command='echo "Starting dynamic DAG"',
        )

        # Generate tasks based on data
        data_sources = ['source_a', 'source_b', 'source_c']

        extract_tasks = []
        for source in data_sources:
            task = BashOperator(
                task_id=f'extract_{source}',
                bash_command=f'echo "Extracting from {source}"',
            )
            extract_tasks.append(task)
            start >> task

        # Transform task
        transform = BashOperator(
            task_id='transform',
            bash_command='echo "Transforming data"',
        )

        # Load task
        load = BashOperator(
            task_id='load',
            bash_command='echo "Loading to destination"',
        )

        extract_tasks >> transform >> load

    return dynamic_dag


# Uncomment to enable dynamic DAG
# dynamic_dag = generate_dynamic_tasks()
