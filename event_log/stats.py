from sqlalchemy import Column, Integer, DateTime, func, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stats(Base):
    """ Processing Statistics """
    __tablename__ = "stats"
    
    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    message_code = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, message_text, message_code, timestamp):
        """ Initializes a processing statistics object """
        self.message_text = message_text
        self.message_code = message_code
        self.timestamp = timestamp

    # def to_dict(self):
    #     """ Dictionary Representation of a statistics """
    #     stats_dict = {
    #         '': self.num_user_registration_events,
    #         'num_image_upload_events': self.num_image_upload_events,
    #         'max_age_readings': self.max_age_readings,
    #         'num_of_same_filetype_reading': self.num_of_same_filetype_reading,
    #         'last_update': self.last_update.strftime("%Y-%m-%dT%H:%M:%S")
    #     }
    #     return stats_dict
