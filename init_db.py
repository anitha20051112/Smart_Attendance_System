import sqlite3
import os

# Delete old database if it exists
db_path = "attendance.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"🗑️ Old database '{db_path}' deleted.")

# Connect and create a new database
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create tables with TEXT IDs
cur.executescript("""
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS attendance;

CREATE TABLE students (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE attendance (
    id TEXT,
    date TEXT,
    time TEXT,
    FOREIGN KEY (id) REFERENCES students(id)
);
""")

conn.commit()
conn.close()
print("✅ Database initialized successfully with TEXT IDs")
