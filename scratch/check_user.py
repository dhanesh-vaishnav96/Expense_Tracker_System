import sqlite3
import sys

db_path = 'd:/Expense Tracker/expense_tracker.db'
email = 'dhaneshvaishnav123@gmail.com'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, name, password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if user:
        print(f"User found: ID={user[0]}, Email={user[1]}, Name={user[2]}")
        print(f"Hashed Password: {user[3]}")
    else:
        print("User not found.")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
