import sqlite3


def get_db():
    conn = sqlite3.connect('database.db')
    # print("connected to database")
    return conn


def initialise():
    conn = get_db()

    f = open('schema.sql', 'r')
    schema = f.read()
    f.close()

    conn.executescript(schema)

def check_id(id, db):
    if db.execute('SELECT * FROM economy WHERE ID = ?', (id,)).fetchone() is None:
        db.execute('INSERT INTO economy (ID) VALUES (?)', (id,))

def check_pair(sender, recipient, db):
    pair_id = sender + recipient
    reverse = recipient + sender
    if db.execute('SELECT * FROM pairs WHERE ID = ?;', (pair_id,)).fetchone() is None:
        db.execute('INSERT INTO pairs (ID) VALUES (?);', (pair_id,))
        db.execute('INSERT INTO pairs (ID) VALUES (?);', (reverse,))

    return [pair_id, reverse]
