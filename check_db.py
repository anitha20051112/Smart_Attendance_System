import sqlite3

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("📌 Tables:", cursor.fetchall())

# Show schema for each table
cursor.execute("PRAGMA table_info(students);")
print("\n📌 Students table:")
for col in cursor.fetchall():
    print(col)

cursor.execute("PRAGMA table_info(attendance);")
print("\n📌 Attendance table:")
for col in cursor.fetchall():
    print(col)

conn.close()
