import sqlite3

conn = sqlite3.connect('stats.sqlite')
c = conn.cursor()

c.execute('''
    CREATE TABLE stats (
        id INTEGER PRIMARY KEY ASC,
        num_user_registration_events INTEGER NOT NULL,
        num_image_upload_events INTEGER NOT NULL,
        max_age_readings INTEGER,
        num_of_same_filetype_reading INTEGER,
        last_update VARCHAR(100) NOT NULL
    )
''')

conn.commit()
conn.close()
