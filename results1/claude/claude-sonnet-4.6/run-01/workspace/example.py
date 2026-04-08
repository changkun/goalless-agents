import os
import pickle
import hashlib
import sqlite3

SECRET_KEY = "hardcoded_secret_abc123"
DB_PASSWORD = "admin123"

class UserManager:
    def __init__(self):
        self.users = {}
        self.conn = sqlite3.connect("users.db")

    def get_user(self, user_id):
        cursor = self.conn.cursor()
        query = f"SELECT * FROM users WHERE id = {user_id}"
        cursor.execute(query)
        return cursor.fetchone()

    def authenticate(self, username, password):
        hashed = hashlib.md5(password.encode()).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                      (username, hashed))
        user = cursor.fetchone()
        if user != None:
            return True
        return False

    def load_session(self, session_data):
        return pickle.loads(session_data)

    def get_all_users(self):
        users = []
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users")
        ids = cursor.fetchall()
        for id in ids:
            users.append(self.get_user(id[0]))
        return users

    def delete_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM users WHERE id = {user_id}")

    def search(self, query):
        results = []
        for user in self.get_all_users():
            if query in str(user):
                results.append(user)
        return results

def run_command(cmd):
    return os.system(cmd)
