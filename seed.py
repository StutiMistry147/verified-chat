import sqlite3
import bcrypt

def initialize_database(db_path: str = "chat.db"):
    """Initialize SQLite database with schema and seed three users"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    """)
    
    # Create messages table (optional - we're stateless but keeping for completeness)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            username TEXT NOT NULL,
            channel_name TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    # Seed three users with bcrypt hashed passwords
    users = [
        (1, "alice", bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')),
        (2, "bob", bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')),
        (3, "charlie", bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
    ]
    
    for user in users:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO users (id, username, hashed_password) VALUES (?, ?, ?)",
                user
            )
        except sqlite3.IntegrityError:
            pass  # User already exists
    
    conn.commit()
    
    # Verify users were created
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"Database initialized with {count} users")
    
    conn.close()

if __name__ == "__main__":
    # Allow running directly for testing
    initialize_database()
    print("Seed complete. Users: alice, bob, charlie (password: password123)")
