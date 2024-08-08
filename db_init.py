import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Create user_log table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    user_name text,
    chat_id INTEGER,
    chat_type TEXT,
    message_id INTEGER,  
    message_content TEXT,
    date_time TEXT,
    first_name TEXT,
    last_name TEXT,
    country TEXT,
    city TEXT,
    FOREIGN KEY (user_id) REFERENCES user_information(user_id)
)
''')

# Create user_information table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_information (
    user_id INTEGER PRIMARY KEY,
    longitude REAL,
    latitude REAL,
    schedule_var INTEGER,
    phone_number INTEGER,
    preferred_language INTEGER
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()
