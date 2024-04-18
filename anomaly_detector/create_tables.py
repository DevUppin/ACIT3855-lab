import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('anomaly.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE anomaly
                (id INTEGER PRIMARY KEY ASC, 
                event_id VARCHAR(250) NOT NULL,
                trace_id VARCHAR(250) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                anomaly_type VARCHAR(100) NOT NULL,
                description VARCHAR(250) NOT NULL,
                date_created VARCHAR(100) NOT NULL)
               ''')
conn.commit()

# Close connection
conn.close()
