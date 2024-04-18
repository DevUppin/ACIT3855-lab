# import connexion
# from connexion import NoContent
# import json
# import datetime
# import yaml
# import logging
# import logging.config
# import uuid
# import requests
# from sqlalchemy import create_engine, and_
# from sqlalchemy.orm import sessionmaker
# import mysql.connector
# from apscheduler.schedulers.background import BackgroundScheduler
# from stats import Stats, Base
# from flask import jsonify
# # from dateutil import parser
# # from datetime import datetime
# import pytz
# # from sqlalchemy.orm import scoped_session

# with open('app_conf.yml', 'r') as f:
#     app_config = yaml.safe_load(f.read())

# # user_registration_url = app_config['eventstore1']['url']
# # image_upload_url = app_config['eventstore2']['url']

# DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
# Base.metadata.bind = DB_ENGINE
# DB_SESSION = sessionmaker(bind=DB_ENGINE)
# # session = DB_SESSION()


# with open('log_conf.yml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# logger = logging.getLogger('basicLogger')


# def populate_stats():
#     """ Periodically update stats """
#     logger.info("Start Periodic Processing")

#     try:
#         session = DB_SESSION()
#         current_stats = session.query(Stats).order_by(Stats.last_update.desc()).first()
#     except Exception as e:
#         logger.error(f"Error reading current statistics from the database: {e}")
#         current_stats = None  
#     finally:
#         if session:
#             session.close()

#     if not current_stats:
#         current_stats = Stats(
#         num_user_registration_events=0,
#         num_image_upload_events=0,
#         max_age_readings=0,
#         num_of_same_filetype_reading=0,
#         last_update=datetime.datetime.now(pytz.utc)
#     )
#         session = DB_SESSION()
#         session.add(current_stats)
#         session.commit()
#         session.close()

#     last_updated_time = current_stats.last_update
#     if isinstance(last_updated_time, datetime.datetime):
#         formatted_last_update = last_updated_time.strftime("%Y-%m-%dT%H:%M:%S")
#         print(formatted_last_update)
#     else:
#         print("last_update is not a datetime object")
#     current_datetime_obj = datetime.datetime.now(pytz.utc)
#     current_datetime = current_datetime_obj.strftime("%Y-%m-%dT%H:%M:%S")
#     print(type(current_datetime))
#     try:
#         # response1 = requests.get(f'http://127.0.0.1:8090/user-registration?start_timestamp={formatted_last_update}&end_timestamp={current_datetime}')
#         # response2 = requests.get(f'http://127.0.0.1:8090/image-upload?start_timestamp=2016-08-30T09:12:33&end_timestamp={current_datetime}')
#         user_registration_url = app_config['eventstore1']['url'].format(formatted_last_update=formatted_last_update, current_datetime=current_datetime)
#         image_upload_url = app_config['eventstore2']['url'].format(formatted_last_update=formatted_last_update, current_datetime=current_datetime)
#         response1 = requests.get(user_registration_url)
#         response2 = requests.get(image_upload_url)

#         if response1.status_code == 200 and response2.status_code == 200:
#             total_events = len(response1.json()) + len(response2.json())
#             logger.info(f"Received {total_events} events")

#             num_events1 = len(response1.json()) + current_stats.num_user_registration_events
#             num_events2 = len(response2.json()) + current_stats.num_image_upload_events
#             logger.info(f"Received {num_events1} events from User Registration Event")
#             logger.info(f"Received {num_events2} events from Image Upload Event")
                    
#             response2 = response2.json()
#             response1 = response1.json()

#             total_num_same_file_type = 0
#             max_age_reading_values = []

#             for event in response2:
#                 trace_id = event.get('trace_id', 'Unknown')
#                 logger.debug(f"Processing num_same_file_type ('.jpg') event with trace_id: {trace_id}")

#                 image_type = event.get('image_type', '')
#                 if image_type == '.jpg': 
#                     total_num_same_file_type += 1

#             for event in response1:
#                 trace_id = event.get('trace_id', 'Unknown')
#                 logger.debug(f"Processing max_age_reading event with trace_id: {trace_id}")
#                 age = event.get('age', 0)
#                 max_age_reading_values.append(age)

#             max_age_reading = max(max_age_reading_values) if max_age_reading_values else 0

#             logger.debug(f"Calculated statistics: "
#                 f"total_num_same_file_type={total_num_same_file_type}, "
#                 f"max_age_reading={max_age_reading}")

#             # current_datetime = parser.parse(current_datetime)

#             new_stats = Stats(
#             num_user_registration_events=num_events1,
#             num_image_upload_events=num_events2,
#             max_age_readings=max_age_reading,
#             num_of_same_filetype_reading=total_num_same_file_type,
#             last_update=current_datetime_obj
#             )
#             session = DB_SESSION()
#             session.add(new_stats)
#             session.commit()
#             session.closee()

#             logger.debug(f"Updated statistics: {current_stats.to_dict()}")
#         else:
#             logger.error(f"Failed to get events. Status codes: {response1.status_code}, {response2.status_code}")
#     except Exception as e:
#         logger.error(f"Error querying Data Store Service: {e}")

#     logger.info("Periodic Processing has ended")



# def get_stats():
#     """ GET endpoint for /events/stats resource """
#     logger.info("Request for statistics has started")

#     try:
#         session = DB_SESSION()
#         current_stats = session.query(Stats).order_by(Stats.last_update.desc()).first()
#         session.commit()
#         session.close()
        
#         if not current_stats:
#             logger.error("Statistics do not exist")
#             return jsonify({"message": "Statistics do not exist"}), 404

#         stats_dict = current_stats.to_dict()

#         logger.debug(f"Statistics retrieved: {stats_dict}")

#         logger.info("Request for statistics has completed")

#         return jsonify(stats_dict), 200
#     except Exception as e:
#         logger.error(f"Error processing request for statistics: {e}")
#         return jsonify({"message": "Internal Server Error"}), 500

# def init_scheduler():
#     sched = BackgroundScheduler(daemon=True)
#     sched.add_job(populate_stats,
#         'interval',
#         seconds=app_config['scheduler']['period_sec'])
#     sched.start()


# app = connexion.FlaskApp(__name__, specification_dir='')
# app.add_api("openapi.yml")
# strict_validation = True
# validate_responses = True

# if __name__ == "__main__":
# # run our standalone gevent server
#     init_scheduler()
#     app.run(port=8100)


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
import mysql.connector
from apscheduler.schedulers.background import BackgroundScheduler
from stats import Stats, Base
from flask import jsonify
from flask_cors import CORS
from pykafka import KafkaClient
import time
# from dateutil import parser
# from datetime import datetime
import pytz
# from connexion.middleware import MiddlewarePosition
# from starlette.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import scoped_session

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

kafka_server = app_config['events']['hostname']
kafka_port = app_config['events']['port']
topic_events = app_config['events']['topic1']
topic_event_log = app_config['events']['topic2']

# user_registration_url = app_config['eventstore1']['url']
# image_upload_url = app_config['eventstore2']['url']

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
# session = DB_SESSION()


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

client = None
producer_event_log = None

def connect_to_kafka():
    """Connect to Kafka"""
    global client, producer_event_log
    max_retries = app_config['max_retries']
    current_retry = 0
    while current_retry < max_retries:
        try:
            client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
            topic_two = client.topics[str.encode(topic_event_log)]
            producer_event_log = topic_two.get_sync_producer()
            logger.info("Connected to Kafka")
            msg = {
                "type": "event_log",
                "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "payload": {
                    "message": "Proccessor service connected to Kafka and is ready to proccess messages from events topic",
                    "message_code": "0003"
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

def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")
    session = None
    try:
        session = DB_SESSION()
        current_stats = session.query(Stats).order_by(Stats.last_update.desc()).first()
    # except Exception as e:
    #     logger.error(f"Error reading current statistics from the database: {e}")
    #     current_stats = None  
        if not current_stats:
            current_stats = Stats(
            num_user_registration_events=0,
            num_image_upload_events=0,
            max_age_readings=0,
            num_of_same_filetype_reading=0,
            last_update=datetime.datetime.now()
            )

        session.add(current_stats)
        session.commit()

        last_updated_time = current_stats.last_update
        if isinstance(last_updated_time, datetime.datetime):
            formatted_last_update = last_updated_time.strftime("%Y-%m-%dT%H:%M:%S")
            print(formatted_last_update)
        else:
            print("last_update is not a datetime object")
        current_datetime_obj = datetime.datetime.now()
        current_datetime = current_datetime_obj.strftime("%Y-%m-%dT%H:%M:%S")
        print(type(current_datetime))
        total_events = None
        try:
        # response1 = requests.get(f'http://127.0.0.1:8090/user-registration?start_timestamp={formatted_last_update}&end_timestamp={current_datetime}')
        # response2 = requests.get(f'http://127.0.0.1:8090/image-upload?start_timestamp=2016-08-30T09:12:33&end_timestamp={current_datetime}')
            user_registration_url = app_config['eventstore1']['url'].format(formatted_last_update=formatted_last_update, current_datetime=current_datetime)
            image_upload_url = app_config['eventstore2']['url'].format(formatted_last_update=formatted_last_update, current_datetime=current_datetime)
            response1 = requests.get(user_registration_url)
            response2 = requests.get(image_upload_url)

            if response1.status_code == 200 and response2.status_code == 200:
                total_events = len(response1.json()) + len(response2.json())
                logger.info(f"Received {total_events} events")

                num_events1 = len(response1.json()) + current_stats.num_user_registration_events
                num_events2 = len(response2.json()) + current_stats.num_image_upload_events
                logger.info(f"Received {num_events1} events from User Registration Event")
                logger.info(f"Received {num_events2} events from Image Upload Event")
                    
                response2 = response2.json()
                response1 = response1.json()

                total_num_same_file_type = 0
                max_age_reading_values = []

                for event in response2:
                    trace_id = event.get('trace_id', 'Unknown')
                    logger.debug(f"Processing num_same_file_type ('.jpg') event with trace_id: {trace_id}")

                    image_type = event.get('image_type', '')
                    if image_type == '.jpg': 
                        total_num_same_file_type += 1

                for event in response1:
                    trace_id = event.get('trace_id', 'Unknown')
                    logger.debug(f"Processing max_age_reading event with trace_id: {trace_id}")
                    age = event.get('age', 0)
                    max_age_reading_values.append(age)

                max_age_reading = max(max_age_reading_values) if max_age_reading_values else 0

                logger.debug(f"Calculated statistics: "
                    f"total_num_same_file_type={total_num_same_file_type}, "
                    f"max_age_reading={max_age_reading}")

            # current_datetime = parser.parse(current_datetime)

                new_stats = Stats(
                num_user_registration_events=num_events1,
                num_image_upload_events=num_events2,
                max_age_readings=max_age_reading,
                num_of_same_filetype_reading=total_num_same_file_type,
                last_update=current_datetime_obj
                )

                session.add(new_stats)
                session.commit()

                logger.debug(f"Updated statistics: {current_stats.to_dict()}")
            else:
                logger.error(f"Failed to get events. Status codes: {response1.status_code}, {response2.status_code}")

            if total_events > app_config['threshold']:
                msg = {
                    "type": "event_log",
                    "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "payload": {
                        "message": "Threshold of configurable number of events exceeded during periodic processing",
                        "message_code": "0004"
                    }
                }
                msg_str = json.dumps(msg)
                producer_event_log.produce(msg_str.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error querying Data Store Service: {e}")

        logger.info("Periodic Processing has ended")
        
    except Exception as e:
        logger.error(f"Error in periodic processing: {e}")
    finally:
        if session:
            session.close()



def get_stats():
    """ GET endpoint for /events/stats resource """
    logger.info("Request for statistics has started")
    session = None
    try:
        session = DB_SESSION()
        current_stats = session.query(Stats).order_by(Stats.last_update.desc()).first()

        
        if not current_stats:
            logger.error("Statistics do not exist")
            return jsonify({"message": "Statistics do not exist"}), 404

        stats_dict = current_stats.to_dict()

        logger.debug(f"Statistics retrieved: {stats_dict}")

        logger.info("Request for statistics has completed")

        return jsonify(stats_dict), 200
    except Exception as e:
        logger.error(f"Error processing request for statistics: {e}")
        return jsonify({"message": "Internal Server Error"}), 500
    finally:
        session.close()

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
        'interval',
        seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
    

# app.add_middleware(
#     CORSMiddleware,
#     position=MiddlewarePosition.BEFORE_EXCEPTION,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )
app.add_api("openapi.yml")
strict_validation = True
validate_responses = True

if __name__ == "__main__":
# run our standalone gevent server
    init_scheduler()
    app.run(port=8100)


