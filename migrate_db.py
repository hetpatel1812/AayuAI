import sqlite3
import os

db_path = os.path.join('instance', 'aayu.db')
if not os.path.exists(db_path):
    db_path = 'aayu.db'

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("ALTER TABLE users ADD COLUMN sms_notifications BOOLEAN DEFAULT 1")
    cur.execute("ALTER TABLE users ADD COLUMN email_notifications BOOLEAN DEFAULT 1")
    conn.commit()
    print("Columns added successfully.")
except Exception as e:
    print("Error or columns already exist:", e)
finally:
    conn.close()
