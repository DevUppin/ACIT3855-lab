import connexion
from connexion import NoContent
import yaml
import json
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# Set up logging

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# Create logger
logger = logging.getLogger('basicLogger')

# Kafka configuration
# kafka_config = app_config['kafka']
# kafka_host = f"{kafka_config['hostname']}:{kafka_config['port']}"
# kafka_topic = kafka_config['topic']



def get_user_registration_reading(index):
    """ Get User Registration Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving user registration reading at index %d" % index)

    try:
        count = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # Assuming the event type is 'user_registration' and contains necessary fields
            if msg['type'] == 'user_registration':
                if count == index:
                    return msg, 200
                count += 1
                if count > index:
                    raise ValueError("Index out of range")
        logger.error("Could not find user registration reading at index %d" % index)
        return {"message": "Not Found"}, 404
    except:
        logger.error("No more messages found")
        logger.error("Could not find user registration reading at index %d" % index)
        return {"message": "Not Found"}, 404
    
def get_image_upload_reading(index):
    """ Get Image Upload Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving image upload reading at index %d" % index)

    try:
        count = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # Assuming the event type is 'image_upload' and contains necessary fields
            if msg['type'] == 'image_upload':
                if count == index:
                    return msg, 200
                count += 1
                if count > index:
                    raise ValueError("Index out of range")
        logger.error("Could not find image upload reading at index %d" % index)
        return {"message": "Not Found"}, 404
    except:
        logger.error("No more messages found")
        logger.error("Could not find image upload reading at index %d" % index)
        return {"message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml")

if __name__ == "__main__":
    app.run(port=8110)
