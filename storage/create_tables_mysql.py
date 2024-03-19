import mysql.connector

db_conn = mysql.connector.connect(
    host="acit-3855-lab6-duppin.westus3.cloudapp.azure.com",
    user="user",
    password="password",
    database="events"
)

db_cursor = db_conn.cursor()

# Create 'users' table
db_cursor.execute('''
CREATE TABLE users
(
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(250) NOT NULL,
    email VARCHAR(250) NOT NULL,
    password VARCHAR(250) NOT NULL,
    age INTEGER NOT NULL,
    trace_id VARCHAR(100) NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
)
''')

# Create 'images' table
db_cursor.execute('''
CREATE TABLE images
(
    id INT NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(36) NOT NULL,
    image_file_name VARCHAR(250) NOT NULL,
    image_type VARCHAR(10) NOT NULL,
    image_size VARCHAR(10) NOT NULL,
    trace_id VARCHAR(100) NOT NULL,    
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
)
''')

db_conn.commit()
db_conn.close()

