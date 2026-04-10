# Simple database manager
import json
import os

class Database:
    def __init__(self, filename):
        self.filename = filename
        self.data = {}
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.data = json.load(f)

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)

    def add_user(self, user_id, name, email):
        self.data[user_id] = {'name': name, 'email': email}
        self.save()

    def get_user(self, user_id):
        return self.data.get(user_id)

    def delete_user(self, user_id):
        if user_id in self.data:
            del self.data[user_id]
            self.save()

# Usage
db = Database('users.json')
db.add_user(1, 'John', 'john@example.com')
user = db.get_user(1)
print(f"User: {user['name']}")
