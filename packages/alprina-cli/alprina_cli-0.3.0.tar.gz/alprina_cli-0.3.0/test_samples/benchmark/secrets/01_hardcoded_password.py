# Hardcoded Secret #1: Database Password
# CWE-798: Use of Hard-coded Credentials
# CVSS: 9.8 (CRITICAL)
# Expected: Should detect hardcoded password in line 10

import psycopg2

# VULNERABLE: Hardcoded database credentials
DB_HOST = "production.db.example.com"
DB_USER = "admin"
DB_PASSWORD = "SuperSecret123!"  # HARDCODED PASSWORD
DB_NAME = "users_db"

def connect_database():
    conn = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return conn

# Security Issue: Password exposed in source code
# Best Practice: Use environment variables or secret management
