import sqlite3

conn = sqlite3.connect("attendance.db")
cur = conn.cursor()

cur.execute("PRAGMA table_info(students);")
for col in cur.fetchall():
    print(col)

cur.execute("PRAGMA table_info(attendance);")
for col in cur.fetchall():
    print(col)

conn.close()
