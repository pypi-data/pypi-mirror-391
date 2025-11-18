# Command Injection #1: OS Command Injection
# CWE-78: Improper Neutralization of Special Elements used in an OS Command
# CVSS: 9.8 (CRITICAL)
# Expected: Should detect command injection in line 13

import os
import subprocess

def ping_host(hostname):
    """
    Vulnerable function that allows command injection.
    User input is passed directly to system command.
    """
    
    # VULNERABLE: Direct use of user input in system command
    result = os.system(f"ping -c 4 {hostname}")
    
    return result

# Attack vector: ping_host("google.com; rm -rf /")
# Result: Executes additional malicious commands
