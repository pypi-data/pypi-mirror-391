# SQL Injection Vulnerability #1: Basic SQL Injection
# CWE-89: Improper Neutralization of Special Elements used in an SQL Command
# CVSS: 9.8 (CRITICAL)
# Expected: Should detect SQL injection in line 12

import sqlite3

def get_user_by_id(user_id):
    """
    Vulnerable function that allows SQL injection.
    User input is directly concatenated into SQL query.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # VULNERABLE: Direct string formatting with user input
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result

# Attack vector: get_user_by_id("1 OR 1=1")
# Result: Returns all users instead of single user
