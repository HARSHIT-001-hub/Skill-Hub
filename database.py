import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect("skillhub.db")
cursor = conn.cursor()

# Create a table for storing user profiles
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        address TEXT NOT NULL,
        interesting_language TEXT NOT NULL,
        known_language TEXT NOT NULL,
        level TEXT NOT NULL
    )
""")

# Commit and close the connection
conn.commit()
conn.close()

print("Database and table created successfully!")
