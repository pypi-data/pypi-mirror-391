# XSS Vulnerability #1: Reflected Cross-Site Scripting
# CWE-79: Improper Neutralization of Input During Web Page Generation
# CVSS: 6.1 (MEDIUM)
# Expected: Should detect XSS in line 13

from flask import Flask, request

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    # VULNERABLE: Directly embedding user input in HTML without escaping
    return f'''
        <html>
            <h1>Search Results for: {query}</h1>
        </html>
    '''

# Attack vector: /search?q=<script>alert('XSS')</script>
# Result: Executes JavaScript in victim's browser
