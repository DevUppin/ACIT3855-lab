import mysql.connector

db_conn = mysql.connector.connect(
    host="acit-3855-lab6-duppin.westus3.cloudapp.azure.com",
    user="user",
    password="password",
    database="events"
)

db_cursor = db_conn.cursor()

db_cursor.execute('''
DROP TABLE images
''')



db_cursor.execute('''
DROP TABLE users
''')

# Drop 'images' table first due to foreign key constraint


# Drop 'users' table


db_conn.commit()
db_conn.close()
