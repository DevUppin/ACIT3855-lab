import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('event_logs.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE event_logs (
                    id INTEGER PRIMARY KEY,
                    message TEXT NOT NULL,
                    message_code TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
conn.commit()

# Close connection
conn.close()

