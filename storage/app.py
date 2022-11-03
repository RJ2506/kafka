from platform import python_branch
from sqlite3 import connect
import requests
import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from search import SearchProducts
from buy import BuyingProducts
import pymysql
import mysql.connector
import yaml, logging, logging.config
import datetime
from pykafka import KafkaClient

with open("app_conf.yaml", "r") as f:
    app_config = yaml.safe_load(f.read())


with open("log_conf.yaml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basicLogger")

logger.info(f'Connecting to DB, Hostname:{app_config["datastore"]["hostname"]}, Port:{app_config["datastore"]["port"]}')

DB_ENGINE = create_engine(
    f'mysql+pymysql://{app_config["datastore"]["user"]}:{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}'
)
# DB_ENGINE = create_engine(
#     f'mysql+pymysql://rj:Rodolfjohn25!@localhost:3306/mydb'
# )

# DB_ENGINE = create_engine("sqlite:///book.sqlite")

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def purchase_item(body):
    """purchase the item you selected"""
    session = DB_SESSION()
    
    bp = BuyingProducts(
        body["customer_id"],
        body["credit_card"],
        body["price"],
        body["purchased_date"],
        body["transaction_number"],
        body["trace_id"],
    )
    logger.info(f"stored event buy request with a trace id of {body['trace_id']}")

    session.add(bp)
    session.commit()
    session.close()

    return NoContent, 201


def get_purchase_item(timestamp):
    """get the  timestamp of the purchase tiem"""
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    readings = session.query(BuyingProducts).filter(BuyingProducts.date_created >= timestamp_datetime)

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    
    
    session.close()
    logger.info(
        "Query for purchase item after %s returns %d results"
        % (timestamp, len(results_list))
    )

    return results_list, 200


def search_item(body):
    """search for the product"""
    session = DB_SESSION()

    sp = SearchProducts(
        body["brand_name"],
        body["item_description"],
        body["price"],
        body["product_name"],
        body["quantity_left"],
        body["sales_price"],
        body["trace_id"],
    )

    logger.info(f"stored event buy request with a trace id of {body['trace_id']}")

    session.add(sp)
    session.commit()
    session.close()
    return NoContent, 201


def get_search_item(timestamp):
    """get the  timestamp of the purchase tiem"""
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    readings = session.query(SearchProducts).filter(
        SearchProducts.date_created >= timestamp_datetime
    )

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info(
        "Query for Search Items after %s returns %d results"
        % (timestamp, len(results_list))
    )

    return results_list, 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8090)
