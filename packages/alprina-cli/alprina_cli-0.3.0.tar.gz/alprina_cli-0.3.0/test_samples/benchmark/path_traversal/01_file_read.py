# Path Traversal #1: Directory Traversal
# CWE-22: Improper Limitation of a Pathname to a Restricted Directory
# CVSS: 7.5 (HIGH)
# Expected: Should detect path traversal in line 13

from flask import Flask, request, send_file
import os

app = Flask(__name__)

@app.route('/download')
def download_file():
    filename = request.args.get('file')
    
    # VULNERABLE: No validation of file path
    filepath = os.path.join('/var/www/uploads/', filename)
    
    return send_file(filepath)

# Attack vector: /download?file=../../../../etc/passwd
# Result: Can read any file on the system
