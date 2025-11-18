#!/usr/bin/env python3
"""Find SolidityVulnerability instantiations missing function_name parameter"""

import re

with open('src/alprina_cli/agents/web3_auditor/solidity_analyzer.py', 'r') as f:
    lines = f.readlines()

# Find all SolidityVulnerability( occurrences
in_vulnerability = False
start_line = 0
paren_count = 0
current_block = []

for i, line in enumerate(lines, 1):
    if 'SolidityVulnerability(' in line:
        in_vulnerability = True
        start_line = i
        paren_count = line.count('(') - line.count(')')
        current_block = [line]
    elif in_vulnerability:
        current_block.append(line)
        paren_count += line.count('(') - line.count(')')

        if paren_count == 0:
            # End of this vulnerability instantiation
            block_text = ''.join(current_block)

            # Check if it has both contract_name and function_name
            has_contract_name = 'contract_name' in block_text
            has_function_name = 'function_name' in block_text

            if has_contract_name and not has_function_name:
                print(f"Line {start_line}: Missing function_name")
                print(''.join(current_block[:5]))  # Show first 5 lines
                print("...")
                print()

            in_vulnerability = False
            current_block = []
            paren_count = 0
