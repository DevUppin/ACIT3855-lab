import json
import logging
import logging.config
import yaml
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import time
import sqlite3
import connexion
from connexion import NoContent
from flask import jsonify
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from stats import Stats, Base
import datetime
from sqlalchemy import Column, Integer, DateTime, func, String

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

# Create logger
logger = logging.getLogger('basicLogger')

# conn = sqlite3.connect('event_logs.db')
# cursor = conn.cursor()

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
        # Create a new session
        session = DB_SESSION()
        # Create new event log object
        event_log = Stats(message_text=msg['message'], message_code=msg['message_code'], timestamp=datetime.datetime.now())
        # Add to session and commit
        session.add(event_log)
        session.commit()
    except Exception as e:
        logger.error(f"Error processing message: {e}")
    finally:
        session.close()
    # try:
    #     insert_event_log(msg['message'], msg['message_code'])
    # except Exception as e:
    #     logger.error(f"Error processing message: {e}")


# Function to insert event log into SQLite database
# def insert_event_log(message, message_code):
#     session = DB_SESSION()
#     # conn = sqlite3.connect('event_logs.db')  # Create a new connection
#     cursor = conn.cursor()  # Create a new cursor
#     cursor.execute('''INSERT INTO event_logs (message, message_code) 
#                       VALUES (?, ?)''', (message, message_code))
#     conn.commit()


# Function to get event stats
def get_event_stats():
    try:
        session = DB_SESSION()
        event_stats = session.query(Stats.message_code, func.count(Stats.id)).group_by(Stats.message_code).all()
        return {code: count for code, count in event_stats}
    except Exception as e:
        logger.error(f"Error getting event stats: {e}")
        return {}
    finally:
        session.close()
    # conn = sqlite3.connect('event_logs.db')  # Create a new connection
    # cursor = conn.cursor()  # Create a new cursor
    # cursor.execute('''SELECT message_code, COUNT(*) FROM event_logs GROUP BY message_code''')
    # rows = cursor.fetchall()
    # event_stats = {row[0]: row[1] for row in rows}
    # return event_stats


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

