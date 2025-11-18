# Alprina Vulnerability Benchmark Suite

This directory contains **100 vulnerable code samples** for testing Alprina's detection capabilities.

## Purpose

Prove Alprina's accuracy with real-world vulnerability patterns based on OWASP Top 10 and CWE database.

## Structure

```
benchmark/
├── sql_injection/       # CWE-89  (10 samples)
├── xss/                 # CWE-79  (10 samples)
├── secrets/             # CWE-798 (10 samples)
├── auth_bypass/         # CWE-287 (10 samples)
├── csrf/                # CWE-352 (10 samples)
├── path_traversal/      # CWE-22  (10 samples)
├── command_injection/   # CWE-78  (10 samples)
├── xxe/                 # CWE-611 (10 samples)
├── deserialization/     # CWE-502 (10 samples)
└── ssrf/                # CWE-918 (10 samples)
```

## Running the Benchmark

```bash
# Run full benchmark
alprina benchmark

# Run specific category
alprina benchmark --category sql_injection

# Generate HTML report
alprina benchmark --format html

# Compare with other tools
alprina benchmark --compare snyk
```

## Expected Results

Alprina should detect **95%+ of vulnerabilities** (95/100).

### By Category:
- SQL Injection: 100% (10/10)
- XSS: 90% (9/10)
- Hardcoded Secrets: 100% (10/10)
- Auth Bypass: 80% (8/10)
- CSRF: 100% (10/10)
- Path Traversal: 90% (9/10)
- Command Injection: 100% (10/10)
- XXE: 90% (9/10)
- Deserialization: 80% (8/10)
- SSRF: 100% (10/10)

## Vulnerability Details

Each file includes:
- **CWE ID**: Common Weakness Enumeration
- **CVSS Score**: Severity rating
- **Description**: What vulnerability is present
- **Line Number**: Where to detect
- **Attack Vector**: Example exploit
- **Expected Result**: What should be detected

## Languages Covered

- Python (.py)
- JavaScript/Node.js (.js)
- Java (.java)
- PHP (.php)
- Go (.go)
- Ruby (.rb)
- C# (.cs)
- TypeScript (.ts)

## Contributing

To add new test cases:
1. Create file in appropriate category
2. Follow naming convention: `##_description.ext`
3. Include CWE, CVSS, and expected detection line
4. Add attack vector comment
5. Update this README

## Verification

Each vulnerability has been verified to be:
- ✅ **Realistic**: Based on real-world issues
- ✅ **Exploitable**: Can be demonstrated
- ✅ **Documented**: Maps to CWE/CVE
- ✅ **Clear**: Obvious vulnerability pattern

## References

- OWASP Top 10: https://owasp.org/Top10/
- CWE Database: https://cwe.mitre.org/
- NVD: https://nvd.nist.gov/
- CVSS Calculator: https://www.first.org/cvss/calculator/

## License

Public Domain - Use freely for security testing
