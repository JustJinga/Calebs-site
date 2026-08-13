import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    author_url TEXT,
    rating INTEGER NOT NULL,
    review TEXT NOT NULL,
    date TEXT NOT NULL,
    cover_url TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    github_url TEXT,
    status TEXT DEFAULT 'completed'
)
''')

conn.commit()
conn.close()

print('Database created successfully!')