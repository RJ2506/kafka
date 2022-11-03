from time import strftime
import uuid
import connexion
from connexion import NoContent
import datetime
import requests
import json
import yaml
import logging, logging.config
from pykafka import KafkaClient

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yaml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basicLogger")


def purchase_item(body):
    """purchase the item you selected"""
    trace = str(uuid.uuid4())
    body["trace_id"] = trace

    logging.info(f"Returned event buy response {trace}")
    res = requests.post(
        "http://localhost:8090/buy",
        json.dumps(body),
        headers={"Content-type": "application/json"},
    )

    logging.info(f"Returned event buy status {res.status_code}")
    return res.text, res.status_code


def search_item(body):
    """search for the product"""
    trace = str(uuid.uuid4())
    body["trace_id"] = trace

    logging.info(f"Returned event search response {trace}")
    res = requests.post(
        "http://localhost:8090/search",
        json.dumps(body),
        headers={"Content-type": "application/json"},
    )
    logging.info(f"Returned event search status {res.status_code}")
    return res.text, res.status_code


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    app.run(port=8080)
