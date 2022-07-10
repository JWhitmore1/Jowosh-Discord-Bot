import sqlite3


def get_db():
    conn = sqlite3.connect('database.db')
    print("connected to database")
    return conn


def initialise():
    conn = get_db()

    f = open('schema.sql', 'r')
    schema = f.read()
    f.close()

    conn.execute(schema)
