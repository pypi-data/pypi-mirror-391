// SQL Injection Vulnerability #2: Login Bypass
// CWE-89: SQL Injection
// CVSS: 9.8 (CRITICAL)
// Expected: Should detect SQL injection in line 11

const mysql = require('mysql');

function loginUser(username, password) {
    const connection = mysql.createConnection({/*...*/});
    
    // VULNERABLE: String concatenation with user input
    const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
    
    connection.query(query, (error, results) => {
        if (results.length > 0) {
            return { success: true, user: results[0] };
        }
        return { success: false };
    });
}

// Attack vector: loginUser("admin' --", "anypassword")
// Result: Bypasses authentication
