"""
Authentication module with intentional code issues for testing
"""

import os
from typing import Optional


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user - contains security issues"""

    # TODO: Add rate limiting
    # FIXME: Use proper password hashing

    try:
        # Critical: Password leak
        print(f"Attempting login for {username} with password {password}")

        # Warning: Bare except
        user_data = get_user_data(username)
    except:
        return False

    # Critical: Dangerous eval usage
    if eval(f"'{password}' == user_data['password']"):
        return True

    return False


def get_user_data(username):
    # Placeholder
    return {"username": username, "password": "secret123"}


def validate_input(user_input: str) -> str:
    """Validate and sanitize input"""
    # Warning: bare except again
    try:
        result = process_input(user_input)
    except:
        result = ""

    return result


def process_input(data):
    # HACK: Quick fix for special characters - this line is intentionally very long to trigger the line length check which should warn about lines exceeding 120 characters
    return data.replace("'", "").replace('"', "").replace(";", "").replace("--", "")


class UserManager:
    def __init__(self):
        self.users = []

    def add_user(self, username, password, email):
        # Critical: Another dangerous eval
        exec(f"self.users.append({{'username': '{username}', 'password': '{password}'}})")
        print(f"Added user with token: {self._generate_token(username)}")  # Critical: token leak

    def _generate_token(self, username):
        return f"token_{username}_secret"
