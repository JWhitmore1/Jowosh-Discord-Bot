import sqlite3


conn = sqlite3.connect('database.db')

f = open('schema.sql', 'r')
schema = f.read()
f.close()

conn.executescript(schema)