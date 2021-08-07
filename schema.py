import sqlite3 as sql
from sqlite3 import Error


try:
    conn = sql.connect("schema.db")

    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL, email TEXT NOT NULL)")

    cur.execute("CREATE TABLE IF NOT EXISTS texts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, user_id TEXT, FOREIGN KEY(user_id) REFERENCES users(id))")

    cur.execute("CREATE TABLE IF NOT EXISTS video (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, user_id TEXT, FOREIGN KEY(user_id) REFERENCES users(id))")

    cur.execute("CREATE TABLE IF NOT EXISTS audio (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, user_id TEXT, FOREIGN KEY(user_id) REFERENCES users(id))")

    cur.execute("""CREATE TABLE IF NOT EXISTS details (id INTEGER PRIMARY KEY AUTOINCREMENT, details BLOB, size INTEGER, upload_type TEXT, 
                user_id TEXT, FOREIGN KEY(user_id) REFERENCES users(id))""")

    print("Tables created successfully")
    cur.close()
    
except Error as e:
    print(e)