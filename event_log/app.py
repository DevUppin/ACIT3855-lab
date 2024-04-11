# from flask import Flask, jsonify
# from pykafka import KafkaClient
# from pykafka.common import OffsetType
# import logging
# import sqlite3
# import json

# app = Flask(__name__)

# # Configure logging
# logging.basicConfig(filename='event_logger.log', level=logging.INFO)

# # Connect to SQLite database
# conn = sqlite3.connect('event_logs.db')
# cursor = conn.cursor()

# # Kafka consumer setup
# consumer = KafkaConsumer('event_log',
#                          bootstrap_servers=['localhost:9092'],
#                          auto_offset_reset='earliest',
#                          group_id='event_logger_group')

# # Function to insert event log into SQLite database
# def insert_event_log(message, message_code):
#     cursor.execute('''INSERT INTO event_logs (message, message_code) 
#                       VALUES (?, ?)''', (message, message_code))
#     conn.commit()

# # Function to get event stats
# def get_event_stats():
#     cursor.execute('''SELECT message_code, COUNT(*) FROM event_logs GROUP BY message_code''')
#     rows = cursor.fetchall()
#     event_stats = {row[0]: row[1] for row in rows}
#     return event_stats

# # Route to get event stats
# @app.route('/events_stats')
# def events_stats():
#     event_stats = get_event_stats()
#     return jsonify(event_stats)

# # Function to consume messages from Kafka and process them
# def consume_messages():
#     for message in consumer:
#         try:
#             msg_data = json.loads(message.value.decode('utf-8'))
#             logging.info(f"Received message: {msg_data}")
#             insert_event_log(msg_data['message'], msg_data['message_code'])
#         except Exception as e:
#             logging.error(f"Error processing message: {e}")

# if __name__ == '__main__':
#     consume_messages()


import json
import logging
import yaml
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import time
import sqlite3
import connexion
from connexion import NoContent
from flask import jsonify

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# Create logger
logger = logging.getLogger('basicLogger')

conn = sqlite3.connect('event_logs.db')
cursor = conn.cursor()

def connect_to_kafka():
    hostname = "%s:%d" % (app_config["kafka"]["hostname"], app_config["kafka"]["port"])

    # Define retry parameters
    max_retries = app_config["max_retries"]  # Maximum number of retries
    current_retry = 0
    
    while current_retry < max_retries:
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["kafka"]["topic"])]

            # Create a consumer on a consumer group, that only reads new messages
            # (uncommitted messages) when the service re-starts (i.e., it doesn't
            # read all the old messages from the history in the message queue).
            consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                                 reset_offset_on_start=False,
                                                 auto_offset_reset=OffsetType.LATEST)

            # This is blocking - it will wait for a new message
            logger.info(f"Connected to Kafka")
            for msg in consumer:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
                logger.info("Message: %s" % msg)
                # Process the message as needed
                process_message(msg)
                # Commit the new message as being read
                consumer.commit_offsets()
                
        except Exception as e:
            # Handle exception and retry
            logger.error(f"Error connecting to Kafka: {e}")
            current_retry += 1
            logger.info(f"Retrying connection to Kafka. Retry count: {current_retry}")
            time.sleep(5)  # Sleep for 5 seconds before retrying
        else:
            # No exception occurred, break out of the loop
            break

    # If reached here, maximum retries exhausted without successful connection
    logger.error("Unable to connect to Kafka after maximum retries. Exiting.")


def process_message(msg):
    try:
        insert_event_log(msg['message'], msg['message_code'])
    except Exception as e:
        logger.error(f"Error processing message: {e}")


# Function to insert event log into SQLite database
def insert_event_log(message, message_code):
    cursor.execute('''INSERT INTO event_logs (message, message_code) 
                      VALUES (?, ?)''', (message, message_code))
    conn.commit()


# Function to get event stats
def get_event_stats():
    cursor.execute('''SELECT message_code, COUNT(*) FROM event_logs GROUP BY message_code''')
    rows = cursor.fetchall()
    event_stats = {row[0]: row[1] for row in rows}
    return event_stats


# Route to get event stats
def events_stats():
    event_stats = get_event_stats()
    return jsonify(event_stats)



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml")
strict_validation = True
validate_responses = True


# if __name__ == "__main__":
#     # Start Kafka connection in a separate thread
#     t1 = Thread(target=connect_to_kafka)
#     t1.setDaemon(True)
#     t1.start()

#     # Continue with the rest of your application logic
#     # ...

if __name__ == "__main__":
    t1 = Thread(target=connect_to_kafka)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8120)

