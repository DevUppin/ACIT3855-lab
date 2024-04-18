# anomaly_detector.py
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import connexion
from connexion import NoContent
import json
import datetime
import yaml
import logging
import logging.config
from sqlalchemy import create_engine, and_
from anomaly import Anomaly, Base
from flask import jsonify
from flask_cors import CORS
from pykafka import KafkaClient
import time
from pykafka.common import OffsetType
from threading import Thread

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

kafka_server = app_config['events']['hostname']
kafka_port = app_config['events']['port']
topic_events = app_config['events']['topic1']
threshold_anomaly1 = app_config['threshold_a1']
threshold_anomaly2 = app_config['threshold_a2']

# Connect to SQLite database
DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')



def add_anomaly(event_id, trace_id, event_type, anomaly_type, description):
    session = DB_SESSION()

    anomaly = Anomaly(event_id=event_id, trace_id=trace_id, event_type=event_type,
                      anomaly_type=anomaly_type, description=description, )
    session.add(anomaly)
    session.commit()
    session.close()
    logger.info("Anomaly added to the database: %s", anomaly.to_dict())

# Function to handle anomaly detection
def detect_anomaly(message):
    event = json.loads(message.value.decode('utf-8'))
    event_type = event.get("type")

    if event_type == "user_registration":
        age = event.get("age")
        if age is not None and age > threshold_anomaly1:
            add_anomaly(event_id=event.get("id"),
                        trace_id=event.get("trace_id"),
                        event_type=type,
                        anomaly_type="age_anomaly",
                        description=f"User registration with age over 35: {age}"
                        )

    elif event_type == "image_upload":
        file_size = event.get("image_size")
        if file_size == threshold_anomaly2:
            add_anomaly(event_id=event.get("id"),
                        trace_id=event.get("trace_id"),
                        event_type=type,
                        anomaly_type="file_size_anomaly",
                        description="File upload with size of 500kb")




consumer = None
# Function to consume events from Kafka
def consume_events():
    """ making connection to kafka and consume messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    
    # Define retry parameters
    max_retries = app_config["max_retries"]  
    current_retry = 0
    
    while current_retry < max_retries:
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(topic_events)]
            logger.info(f"Topic created")

            # Create a consumer on a consumer group, that only reads new messages
            # (uncommitted messages) when the service re-starts (i.e., it doesn't
            # read all the old messages from the history in the message queue).
            consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                                 reset_offset_on_start=False,
                                                 auto_offset_reset=OffsetType.LATEST)
            
            logger.info(f"Connected to kafka")
            for msg in consumer:
                if msg is not None:
                    logger.info("Received message: %s", msg)
                    detect_anomaly(msg)

        except Exception as e:
            # Handle exception and retry
            logger.error(f"Error connecting to Kafka: {e}")
            current_retry += 1
            logger.info(f"Retrying connection to Kafka. Retry count: {current_retry}")
            time.sleep(5)  # Sleep for 5 seconds before retrying
        else:
            # No exception occurred, break out of the loop
            break


def get_anomalies():
    session = DB_SESSION()
    anomalies = session.query(Anomaly).order_by(Anomaly.date_created.desc()).all()
    session.close()
    return jsonify([anomaly.to_dict() for anomaly in anomalies]), 201
                                                                                  
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml")
# Configuring CORS
CORS(app.app)


if __name__ == "__main__":
    t1 = Thread(target=consume_events)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8130)




















