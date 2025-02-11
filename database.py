import sqlite3
from passlib.hash import pbkdf2_sha256
import os

class Database:
    def __init__(self):
        self.db_file = "user_data.db"
        self.initialize_database()

    def initialize_database(self):
        if not os.path.exists(self.db_file):
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    score INTEGER,
                    total_questions INTEGER,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            conn.commit()
            conn.close()

    def register_user(self, username, password, email):
        try:
            hashed_password = pbkdf2_sha256.hash(password)
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                         (username, hashed_password, email))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username, password):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()

        if result and pbkdf2_sha256.verify(password, result[1]):
            return result[0]  # Return user_id
        return None

    def save_score(self, user_id, score, total_questions):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO scores (user_id, score, total_questions) VALUES (?, ?, ?)',
                      (user_id, score, total_questions))
        conn.commit()
        conn.close()

    def get_user_scores(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT score, total_questions, date
            FROM scores
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 5
        ''', (user_id,))
        results = cursor.fetchall()
        conn.close()
        return results
