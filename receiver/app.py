import connexion
from connexion import NoContent
import json
import datetime
import yaml
import logging
import logging.config
import uuid
import requests
from sqlalchemy import create_engine
from pykafka import KafkaClient
import time

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


user_Registration = app_config['userRegistration']['url']
image_Upload = app_config['imageUpload']['url']
kafka_server = app_config['events']['hostname']
kafka_port = app_config['events']['port']
topic_events = app_config['events']['topic1']
topic_event_log = app_config['events']['topic2']

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
# topic = client.topics[str.encode(topic)]
# producer = topic.get_sync_producer()

# max_events = 5
# event_file = 'events.json'

# def update_event_data(event_type, msg_data):
#     # Read existing event data from file
#     try:
#         with open(event_file, 'r') as file:
#             event_data = json.load(file)
#     except FileNotFoundError:
#         event_data = {
#             'user_registration': {'count': 0, 'events': []},
#             'image_upload': {'count': 0, 'events': []}
#         }

#     event_data[event_type]['count'] += 1
#     event_data[event_type]['events'].insert(0, {
#         'received_timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
#         'msg_data': msg_data
#     })

#     event_data[event_type]['events'] = event_data[event_type]['events'][:max_events]

#     with open(event_file, 'w') as file:
#         json.dump(event_data, file, indent=2)

client = None
producer = None

def connect_to_kafka():
    """Connect to Kafka"""
    global client, producer
    max_retries = app_config['max_retries']
    current_retry = 0
    while current_retry < max_retries:
        try:
            client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
            topic = client.topics[str.encode(topic_events)]
            producer = topic.get_sync_producer()
            topic_two = client.topics[str.encode(topic_event_log)]
            producer_event_log = topic_two.get_sync_producer()
            logger.info("Connected to Kafka")
            msg = {
                "type": "event_log",
                "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "payload": {
                    "message": "Receiver service connected to Kafka and is ready to receive messages on its RESTful API",
                    "message_code": "0001"
                }
            }
            msg_str = json.dumps(msg)
            producer_event_log.produce(msg_str.encode('utf-8'))
            break  # Exit loop if connection successful
        except Exception as e:
            logger.error(f"Error connecting to Kafka: {e}")
            current_retry += 1
            logger.info(f"Retrying connection to Kafka. Retry count: {current_retry}")
            time.sleep(5)  # Wait for 5 seconds before retrying

    if current_retry == max_retries:
        logger.error("Failed to connect to Kafka after maximum retries. Exiting.")
        exit(1)

connect_to_kafka()


def registerUser(body):
    """
    Register a new user
    """
    # client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    # topic = client.topics[str.encode(topic_events)]
    # producer = topic.get_sync_producer()
    trace_id = str(uuid.uuid4())  # Generate a unique trace_id
    logger.info(f"Received event user_registration request with a trace id of {trace_id}")
    body['trace_id'] = trace_id
    # update_event_data('user_registration', body)
    # response = requests.post(user_Registration, json=body, headers={'Content-Type': 'application/json'})
    msg = {
        "type": "user_registration",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info(f"Returned event user_registration response (Id: {trace_id}) with status 201")
    return NoContent, 201


def uploadImage(body):
    """
    Upload an image
    # """
    # client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    # topic = client.topics[str.encode(topic_events)]
    # producer = topic.get_sync_producer()
    trace_id = str(uuid.uuid4())  # Generate a unique trace_id
    logger.info(f"Received event image_upload request with a trace id of {trace_id}")
    body['trace_id'] = trace_id 
    # update_event_data('image_upload', body)
    # response = requests.post(image_Upload, json=body, headers={'Content-Type': 'application/json'})
    msg = {
        "type": "image_upload",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info(f"Returned event image_upload response (Id: {trace_id}) with status 201")
    return NoContent, 201



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml")
strict_validation = True
validate_responses = True

if __name__ == "__main__":
    app.run(port=8080)
