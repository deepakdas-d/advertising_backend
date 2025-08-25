import sqlite3

# Replace 'db.sqlite3' with your database file if different
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(tables)  # should include 'Admin_carousel'

conn.close()
