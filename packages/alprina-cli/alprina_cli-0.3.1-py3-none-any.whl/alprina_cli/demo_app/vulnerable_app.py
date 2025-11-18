"""
Demo vulnerable application for Alprina tutorial.
Contains intentional security issues for educational purposes.

⚠️ WARNING: This code contains INTENTIONAL vulnerabilities!
DO NOT use any patterns from this file in production code.

NOTE: The "secrets" in this file are fake examples for teaching.
They are not real credentials and are safe to commit.
"""

# droid-shield:disable-file  # This file intentionally contains fake vulnerabilities for education

# Issue 1: SQL Injection (CRITICAL)
def login_user(username, password):
    """
    VULNERABLE: String concatenation in SQL query.
    An attacker can inject SQL code to bypass authentication.
    """
    # BAD: Using f-string with user input
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    return cursor.fetchone()

# Issue 2: Hardcoded Secret (CRITICAL)
JWT_SECRET = "super_secret_key_12345"  # VULNERABLE: Hardcoded secret in source code

# Issue 3: XSS Vulnerability (CRITICAL)
from flask import Flask, request
app = Flask(__name__)

@app.route('/comment', methods=['POST'])
def post_comment():
    """
    VULNERABLE: Unsanitized user input rendered in HTML.
    Allows attackers to inject malicious JavaScript.
    """
    comment = request.form['comment']
    # BAD: Direct HTML rendering without sanitization
    return f"<div class='comment'>{comment}</div>"

# Issue 4: Command Injection (HIGH)
import os
def ping_server(host):
    """
    VULNERABLE: Shell injection via unsanitized input.
    Attacker can execute arbitrary system commands.
    """
    # BAD: Using shell=True with user input
    os.system(f"ping -c 1 {host}")

# Issue 5: Path Traversal (HIGH)
def read_user_file(filename):
    """
    VULNERABLE: Unsanitized path allows reading arbitrary files.
    Attacker can use ../../../etc/passwd to read system files.
    """
    # BAD: Direct path concatenation
    with open(f"./data/{filename}", 'r') as f:
        return f.read()

# Issue 6: Weak Crypto (HIGH)
import hashlib
def hash_password(password):
    """
    VULNERABLE: MD5 is cryptographically broken.
    Passwords can be cracked in seconds with rainbow tables.
    """
    # BAD: Using MD5 for passwords
    return hashlib.md5(password.encode()).hexdigest()

# Issue 7: Debug Mode Enabled (HIGH)
DEBUG = True  # VULNERABLE: Debug mode exposes stack traces and sensitive info

# Issue 8: Missing Authentication (MEDIUM)
@app.route('/admin/users', methods=['GET'])
def get_all_users():
    """
    VULNERABLE: Admin endpoint without authentication.
    Anyone can access sensitive user data.
    """
    # BAD: No @require_auth decorator
    return {"users": User.query.all()}

# Issue 9: Insecure Random (MEDIUM)
import random
def generate_session_token():
    """
    VULNERABLE: Using non-cryptographic random for security token.
    Tokens are predictable and can be guessed.
    """
    # BAD: random.random() is not cryptographically secure
    return str(random.random())

# Issue 10: Missing CSRF Protection (MEDIUM)
@app.route('/api/update-email', methods=['POST'])
def update_email():
    """
    VULNERABLE: State-changing operation without CSRF token.
    Attacker can trick user into changing their email.
    """
    new_email = request.form['email']
    # BAD: No CSRF token validation
    current_user.email = new_email
    current_user.save()
    return {"success": True}
