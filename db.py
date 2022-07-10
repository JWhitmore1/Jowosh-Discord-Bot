import sqlite3

def connect():
    conn = sqlite3.connect('database.db')
    print("connected to database")
    return conn

def initialise():
    conn = connect()
    conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                ID INT PRIMARY KEY NOTNULL, 
                995309463571542126 INT, 
                427290604007849984 INT);
                ''')
    