import sqlite3



# Database connection
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    disabled BOOLEAN NOT NULL
)''')


# Data to insert
users = {
    "asmith": {
        "username": "asmith",
        "full_name": "Alice Smith",
        "email": "alice.smith@example.com",
        "hashed_password": "$2b$12$lQ4UIZdDshcksPHFmlaRfOhcrgpYciIyuKN/woVEdHfhB5zHQ75K2",
        "disabled": False
    },
    "bjohnson": {
        "username": "bjohnson",
        "full_name": "Bob Johnson",
        "email": "bob.johnson@example.com",
        "hashed_password": "$2b$12$lQ4UIZdDshcksPHFmlaRfOhcrgpYciIyuKN/woVEdHfhB5zHQ75K2",
        "disabled": False
    },
    "cbrown": {
        "username": "cbrown",
        "full_name": "Charlie Brown",
        "email": "charlie.brown@example.com",
        "hashed_password": "$2b$12$lQ4UIZdDshcksPHFmlaRfOhcrgpYciIyuKN/woVEdHfhB5zHQ75K2",
        "disabled": False
    },
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test.user@example.com",
        "hashed_password": "$2b$12$lQ4UIZdDshcksPHFmlaRfOhcrgpYciIyuKN/woVEdHfhB5zHQ75K2",
        "disabled": False
    }
}

# Insert data
for user in users.values():
    c.execute("SELECT 1 FROM users WHERE username = ?", (user['username'],))
    if not c.fetchone():
        c.execute("INSERT INTO users (username, full_name, email, hashed_password, disabled) VALUES (?, ?, ?, ?, ?)",
                  (user['username'], user['full_name'], user['email'], user['hashed_password'], user['disabled']))

# Commit the changes and close the connection
conn.commit()
conn.close()
