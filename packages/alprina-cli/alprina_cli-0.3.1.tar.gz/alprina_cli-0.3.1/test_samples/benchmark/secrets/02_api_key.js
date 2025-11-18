// Hardcoded Secret #2: API Key
// CWE-798: Hardcoded Credentials
// CVSS: 7.5 (HIGH)
// Expected: Should detect API key in line 8

const axios = require('axios');

// VULNERABLE: Hardcoded API key
const STRIPE_SECRET_KEY = "sk_live_51HqK2xKz9AABBCCDD123456789";
const OPENAI_API_KEY = "sk-proj-1234567890abcdefghij";

async function processPayment(amount) {
    return axios.post('https://api.stripe.com/v1/charges', {
        amount: amount,
        currency: 'usd'
    }, {
        headers: {
            'Authorization': `Bearer ${STRIPE_SECRET_KEY}`
        }
    });
}

// Security Issue: API keys exposed in source code
// Best Practice: Use .env files and environment variables
