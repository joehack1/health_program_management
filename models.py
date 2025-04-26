# models.py
import sqlite3

# Create database connection
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute('''
CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS enrollments (
    client_id INTEGER,
    program_id INTEGER,
    FOREIGN KEY(client_id) REFERENCES clients(id),
    FOREIGN KEY(program_id) REFERENCES programs(id)
)
''')

conn.commit()

# ADD THIS LINE at the bottom of models.py
__all__ = ['conn']
