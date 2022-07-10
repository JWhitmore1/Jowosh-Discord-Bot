import sqlite3

def connect():
    conn = sqlite3.connect('database.db')
    print("connected to database")
    return conn

def initialise():
    conn = connect()
    # conn.execute()
    # RUN SCHEMA

