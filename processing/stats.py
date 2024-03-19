from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stats(Base):
    """ Processing Statistics """
    __tablename__ = "stats"
    
    id = Column(Integer, primary_key=True)
    num_user_registration_events = Column(Integer, nullable=False, default=0)
    num_image_upload_events = Column(Integer, nullable=False, default=0)
    max_age_readings = Column(Integer, nullable=False, default=0)
    num_of_same_filetype_reading = Column(Integer, nullable=False, default=0)
    last_update = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, num_user_registration_events, num_image_upload_events, max_age_readings,
                 num_of_same_filetype_reading, last_update):
        """ Initializes a processing statistics object """
        self.num_user_registration_events = num_user_registration_events
        self.num_image_upload_events = num_image_upload_events
        self.max_age_readings = max_age_readings
        self.num_of_same_filetype_reading = num_of_same_filetype_reading
        self.last_update = last_update

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        stats_dict = {
            'num_user_registration_events': self.num_user_registration_events,
            'num_image_upload_events': self.num_image_upload_events,
            'max_age_readings': self.max_age_readings,
            'num_of_same_filetype_reading': self.num_of_same_filetype_reading,
            'last_update': self.last_update.strftime("%Y-%m-%dT%H:%M:%S")
        }
        return stats_dict
