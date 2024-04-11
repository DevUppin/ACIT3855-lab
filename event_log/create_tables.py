import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('event_logs.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE event_logs (
                    id INTEGER PRIMARY KEY,
                    message VARCHAR(500) NOT NULL,
                    message_code VARCHAR(200) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
conn.commit()

# Close connection
conn.close()

