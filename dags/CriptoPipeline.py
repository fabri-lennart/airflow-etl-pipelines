# Import Modules for Airflow
# Import Modules for code
import json

import pendulum
import requests
from airflow.decorators import dag, task


# [START POINT]
@dag(
    start_date=pendulum.datetime(2025, 1, 12, tz="UTC"),
    catchup=False,
    tags=["BitcoinPipeline"],
)
def ETLCriptoPrint():
    """
    This pipeline request the data and returns a prints the info for btc.
    """

    @task()
    def extract(url):
        response = requests.get(url)
        data = response.json()
        return data

    @task()
    def transform(criptos_json: json):
        """
        A simple Transform task which takes the json data and only extracts the btc values.
        """
        data = criptos_json
        btc = next(item for item in data["data"] if item["id"] == "90")
        return btc

    @task()
    def load(transformed_json: json):
        print(transformed_json)

    # Define the main flow
    url = "https://api.coinlore.net/api/tickers/"
    all_data = extract(url)
    btc_data = transform(all_data)
    load(btc_data)


# Invocate the DAG
RunDag = ETLCriptoPrint()
