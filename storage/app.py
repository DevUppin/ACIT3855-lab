import connexion
from connexion import NoContent
import json
import datetime
import yaml
import logging
import logging.config
import uuid
import requests
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from create_database import UserRegistrationEvent, ImageUploadEvent, Base
import mysql.connector
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import time


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

db_user = app_config['datastore']['user']
db_password = app_config['datastore']['password']
db_hostname = app_config['datastore']['hostname']
db_port = app_config['datastore']['port']
db_name = app_config['datastore']['db']

# mysql_engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_hostname}:{db_port}/{db_name}')
DATABASE_URI = f'mysql+pymysql://{db_user}:{db_password}@{db_hostname}:{db_port}/{db_name}'

mysql_engine = create_engine(DATABASE_URI, pool_size=10,
                       pool_recycle=3000, pool_pre_ping=True)
MySQLSession = sessionmaker(bind=mysql_engine)

sqlite_engine = create_engine('sqlite:///storage.db', echo=True)
SQLiteSession = sessionmaker(bind=sqlite_engine)


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# Create logger
logger = logging.getLogger('basicLogger')

logger.info(f"Connected to MySQL database: {db_hostname}:{db_port}")

max_events = 5
event_file = 'events.json'

# Session = sessionmaker(bind=DB_ENGINE)

# ... (existing code)

# def registerUser(body):
#     session = Session()
#     user_registration_event = UserRegistrationEvent(**body)
#     session.add(user_registration_event)
#     session.commit()
#     session.close()
#     return NoContent, 201

# def uploadImage(body):
#     session = Session()
#     image_upload_event = ImageUploadEvent(**body)
#     session.add(image_upload_event)
#     session.commit()
#     session.close()
#     return NoContent, 201

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

# def registerUser(body):
#     """
#     Register a new user
#     """
#     trace_id = body['trace_id'] 
#     logger.info(f"Received event user_registration request with a trace id of {trace_id}")
#     body['trace_id'] = trace_id

#     db_conn = mysql.connector.connect(
#         host=db_hostname,
#         user=db_user,
#         password=db_password,
#         database=db_name
#     )
    
#     try:
#         db_cursor = db_conn.cursor()
#         db_cursor.execute('''
#             INSERT INTO users (name, email, password, age, trace_id)
#             VALUES (%(name)s, %(email)s, %(password)s, %(age)s, %(trace_id)s)
#         ''', body)
#         db_conn.commit()
#         logger.debug(f"User registration data added to the database (Id: {trace_id})")
#     except Exception as e:
#         logger.error(f"Error adding user registration data to the database: {e}")
#         db_conn.rollback()
#     finally:
#         db_conn.close()

#     logger.info(f"Returned event user_registration response (Id: {trace_id}) with status 201")
#     return NoContent, 201

# def uploadImage(body):
#     """
#     Upload an image
#     """
#     trace_id = body['trace_id'] 
#     logger.info(f"Received event image_upload request with a trace id of {trace_id}")
#     # body['trace_id'] = trace_id

#     db_conn = mysql.connector.connect(
#         host=db_hostname,
#         user=db_user,
#         password=db_password,  
#         database=db_name
#     )

#     try:
#         db_cursor = db_conn.cursor()
#         db_cursor.execute('''
#             INSERT INTO images (user_id, image_file_name, image_type, image_size, trace_id)
#             VALUES (%s, %s, %s, %s, %s)
#         ''', (body['user_id'], body['image_file_name'], body['image_type'], body['image_size'], body['trace_id']))
#         db_conn.commit()
#         logger.debug(f"Image upload data added to the database (Id: {trace_id})")
#     except Exception as e:
#         logger.error(f"Error adding image upload data to the database: {e}")
#         db_conn.rollback()
#     finally:
#         db_conn.close()

#     logger.info(f"Returned event image_upload response (Id: {trace_id}) with status 201")
#     return NoContent, 201



def get_user_registration_events(start_timestamp, end_timestamp):
    """Gets user registration events between the start and end timestamps"""
    session = MySQLSession()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")
    results = session.query(UserRegistrationEvent).filter(
        and_(UserRegistrationEvent.date_created >= start_timestamp_datetime,
             UserRegistrationEvent.date_created < end_timestamp_datetime))
    results_list = [event.to_dict() for event in results]
    session.close()
    logger.info("Query for User Registration events between %s and %s returns %d results" %
                (start_timestamp, end_timestamp, len(results_list)))
    return results_list, 200

def get_image_upload_events(start_timestamp, end_timestamp):
    """Gets image upload events between the start and end timestamps"""
    session = MySQLSession()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")
    results = session.query(ImageUploadEvent).filter(
        and_(ImageUploadEvent.date_created >= start_timestamp_datetime,
             ImageUploadEvent.date_created < end_timestamp_datetime))

    results_list = [event.to_dict() for event in results]
    session.close()
    logger.info("Query for Image Upload events between %s and %s returns %d results" %
                (start_timestamp, end_timestamp, len(results_list)))
    return results_list, 200

# def process_messages():
#     """ Process event messages """
#     hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
#     client = KafkaClient(hosts=hostname)
#     topic = client.topics[str.encode(app_config["events"]["topic"])]

#     # Create a consumer on a consumer group, that only reads new messages
#     # (uncommitted messages) when the service re-starts (i.e., it doesn't
#     # read all the old messages from the history in the message queue).
#     consumer = topic.get_simple_consumer(consumer_group=b'event_group',
#                                          reset_offset_on_start=False,
#                                          auto_offset_reset=OffsetType.LATEST)

#     # This is blocking - it will wait for a new message
#     for msg in consumer:
#         msg_str = msg.value.decode('utf-8')
#         msg = json.loads(msg_str)
#         logger.info("Message: %s" % msg)
#         payload = msg["payload"]

#         if msg["type"] == "user_registration":  # Change this to your event type
#             # Store the event1 (i.e., the payload) to the DB
#             store_user_registration(payload)
#             logger.info(f"{msg['type']} event has been added")
#         elif msg["type"] == "image_upload":  # Change this to your event type
#             # Store the event2 (i.e., the payload) to the DB
#             store_image_upload(payload)
#             logger.info(f"{msg['type']} event has been added")

#         # Commit the new message as being read
#         consumer.commit_offsets()



def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    
    # Define retry parameters
    max_retries = app_config["max_retries"]  # Maximum number of retries
    current_retry = 0
    
    while current_retry < max_retries:
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]

            # Create a consumer on a consumer group, that only reads new messages
            # (uncommitted messages) when the service re-starts (i.e., it doesn't
            # read all the old messages from the history in the message queue).
            consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                                 reset_offset_on_start=False,
                                                 auto_offset_reset=OffsetType.LATEST)

            # This is blocking - it will wait for a new message
            for msg in consumer:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
                logger.info("Message: %s" % msg)
                payload = msg["payload"]

                if msg["type"] == "user_registration":  # Change this to your event type
                    # Store the event1 (i.e., the payload) to the DB
                    store_user_registration(payload)
                    logger.info(f"{msg['type']} event has been added")
                elif msg["type"] == "image_upload":  # Change this to your event type
                    # Store the event2 (i.e., the payload) to the DB
                    store_image_upload(payload)
                    logger.info(f"{msg['type']} event has been added")

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


def store_user_registration(payload):
    session = MySQLSession()
    try:
        user_registration_event = UserRegistrationEvent(**payload)
        session.add(user_registration_event)
        session.commit()
        logger.info("User registration event stored in the database")
    except Exception as e:
        logger.error("Error storing user registration event: %s" % str(e))
        session.rollback()
    finally:
        session.close()


def store_image_upload(payload):
    session = MySQLSession()
    try:
        image_upload_event = ImageUploadEvent(**payload)
        session.add(image_upload_event)
        session.commit()
        logger.info("Image upload event stored in the database")
    except Exception as e:
        logger.error("Error storing image upload event: %s" % str(e))
        session.rollback()
    finally:
        session.close()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml")
strict_validation = True
validate_responses = True

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
