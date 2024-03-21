# create_database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

db_user = app_config['datastore']['user']
db_password = app_config['datastore']['password']
db_hostname = app_config['datastore']['hostname']
db_port = app_config['datastore']['port']
db_name = app_config['datastore']['db']

mysql_engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_hostname}:{db_port}/{db_name}')

# engine = create_engine('sqlite:///storage.db', echo=True)
Base = declarative_base()

class UserRegistrationEvent(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(length=250))
    email = Column(String(length=250))
    password = Column(String(length=250))
    age = Column(Integer)
    # date_created = Column(DateTime, default=datetime.datetime.utcnow)
    trace_id = Column(String(length=100))
    date_created = Column(DateTime, default=datetime.datetime.now, nullable=False)

    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'age': self.age,
            'date_created': self.date_created.strftime('%Y-%m-%dT%H:%M:%S'),
            'trace_id': self.trace_id
        }

class ImageUploadEvent(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(length=36))  # Corrected attribute name from 'userId' to 'user_id'
    image_file_name = Column(String(length=250))
    image_type = Column(String(length=10))
    image_size = Column(String(length=10))
    # date_created = Column(DateTime, default=datetime.datetime.utcnow)
    trace_id = Column(String(length=100))
    date_created = Column(DateTime, default=datetime.datetime.now, nullable=False)


    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_file_name': self.image_file_name,
            'image_type': self.image_type,
            'image_size': self.image_size,
            'date_created': self.date_created.strftime('%Y-%m-%dT%H:%M:%S'),
            'trace_id': self.trace_id
        }

Base.metadata.create_all(mysql_engine)

