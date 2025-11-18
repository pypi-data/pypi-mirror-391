// XSS Vulnerability #2: Stored Cross-Site Scripting
// CWE-79: XSS
// CVSS: 7.2 (HIGH)
// Expected: Should detect XSS in line 14

const express = require('express');
const app = express();

app.post('/comment', (req, res) => {
    const comment = req.body.comment;
    
    // Store comment in database (simplified)
    saveToDatabase(comment);
    
    // VULNERABLE: Rendering user input without sanitization
    res.send(`<div class="comment">${comment}</div>`);
});

// Attack vector: POST comment="<img src=x onerror=alert('XSS')>"
// Result: Executes when any user views the comment
