import os
import sqlite3

# ========================================

DB_NAME = "cn2020final.db"

# ========================================

if os.path.exists(DB_NAME):
    os.remove(DB_NAME)

conn = sqlite3.connect(DB_NAME)

c = conn.cursor()

c.execute('''CREATE TABLE accounts
    (id integer primary key autoincrement, username text, password text)
''')

c.execute('''CREATE TABLE sessions
    (id text, username text)
''')

c.execute('''CREATE TABLE messages
    (id integer primary key autoincrement,
     user_from text,
     user_to text,
     message text)
''')

conn.commit()
conn.close()
