# app/core/security.py

import os
import hashlib


def generate_salt():
    """Generates a cryptographically secure random salt."""
    return os.urandom(32).hex()  # Returns a 64-character hex string


def hash_password(password, salt):
    """Hashes the password with the salt using SHA-256."""
    # We combine the password and salt, then hash the result
    salted_password = password.encode("utf-8") + salt.encode("utf-8")
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return hashed_password
