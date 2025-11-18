# Alprina Security Scan Report

**Scan ID**: alprina_1763040488
**Timestamp**: 2025-11-13 14:28:08
**Contract**: SimpleERC20.sol
**Scan Time**: 0.10s

## Summary

- **Total Vulnerabilities**: 40
- **Critical**: 1
- **High**: 6
- **Medium**: 25
- **Low**: 8

## Vulnerabilities

### CRITICAL (1)

#### Missing Access Control

- **File**: SimpleERC20.sol:82
- **Function**: burn
- **Analyzer**: static

Critical function burn lacks proper access control modifier

**Recommendation**: Add access control modifier (e.g., onlyOwner) to burn function

### HIGH (6)

#### [MEV] Front-Running: Public Price-Affecting Change in transfer

- **File**: SimpleERC20.sol:31
- **Function**: transfer
- **Analyzer**: mev

Function transfer makes public state changes that affect prices. MEV bots can front-run to profit from predictable price impact.

**Recommendation**: Use commit-reveal schemes or time-locks for sensitive operations. Consider using private mempools (e.g., Flashbots Protect) or submarine sends to hide transactions from front-runners.

#### [MEV] Front-Running: Public Price-Affecting Change in transferFrom

- **File**: SimpleERC20.sol:54
- **Function**: transferFrom
- **Analyzer**: mev

Function transferFrom makes public state changes that affect prices. MEV bots can front-run to profit from predictable price impact.

**Recommendation**: Use commit-reveal schemes or time-locks for sensitive operations. Consider using private mempools (e.g., Flashbots Protect) or submarine sends to hide transactions from front-runners.

#### [MEV] Front-Running: Public Price-Affecting Change in batchMint

- **File**: SimpleERC20.sol:69
- **Function**: batchMint
- **Analyzer**: mev

Function batchMint makes public state changes that affect prices. MEV bots can front-run to profit from predictable price impact.

**Recommendation**: Use commit-reveal schemes or time-locks for sensitive operations. Consider using private mempools (e.g., Flashbots Protect) or submarine sends to hide transactions from front-runners.

#### [MEV] Front-Running: Public Price-Affecting Change in burn

- **File**: SimpleERC20.sol:82
- **Function**: burn
- **Analyzer**: mev

Function burn makes public state changes that affect prices. MEV bots can front-run to profit from predictable price impact.

**Recommendation**: Use commit-reveal schemes or time-locks for sensitive operations. Consider using private mempools (e.g., Flashbots Protect) or submarine sends to hide transactions from front-runners.

#### Missing Address Zero Validation

- **File**: SimpleERC20.sol:54
- **Function**: transferFrom
- **Analyzer**: input_validation

Parameter 'from' in function 'transferFrom' lacks address(0) check. OWASP 2025: Lack of Input Validation ($14.6M in losses). Funds sent to address(0) are permanently lost - no private key exists. This is a common attack vector in 2024-2025.

**Recommendation**: Add validation:
require(from != address(0), 'Zero address not allowed');

#### Loop Length Not Cached

- **File**: SimpleERC20.sol:74
- **Function**: batchMint
- **Analyzer**: gas

Array length is read from storage in every loop iteration. Cache it in a local variable.

**Recommendation**: Cache array.length in a local variable before the loop. Use ++i instead of i++ for slightly lower gas.

### MEDIUM (25)

#### Missing Array Bounds Validation

- **File**: SimpleERC20.sol:37
- **Function**: transfer
- **Analyzer**: input_validation

Array access 'balanceOf[to]' lacks bounds checking. Out-of-bounds access causes revert but wastes gas. OWASP 2025: Input Validation.

**Recommendation**: Add bounds check:
require(to < balanceOf.length, 'Index out of bounds');

#### Missing Array Bounds Validation

- **File**: SimpleERC20.sol:55
- **Function**: transferFrom
- **Analyzer**: input_validation

Array access 'balanceOf[from]' lacks bounds checking. Out-of-bounds access causes revert but wastes gas. OWASP 2025: Input Validation.

**Recommendation**: Add bounds check:
require(from < balanceOf.length, 'Index out of bounds');

#### Missing Array Bounds Validation

- **File**: SimpleERC20.sol:56
- **Function**: transferFrom
- **Analyzer**: input_validation

Array access 'allowance[from]' lacks bounds checking. Out-of-bounds access causes revert but wastes gas. OWASP 2025: Input Validation.

**Recommendation**: Add bounds check:
require(from < allowance.length, 'Index out of bounds');

#### Missing Array Bounds Validation

- **File**: SimpleERC20.sol:60
- **Function**: transferFrom
- **Analyzer**: input_validation

Array access 'balanceOf[from]' lacks bounds checking. Out-of-bounds access causes revert but wastes gas. OWASP 2025: Input Validation.

**Recommendation**: Add bounds check:
require(from < balanceOf.length, 'Index out of bounds');

#### Missing Array Bounds Validation

- **File**: SimpleERC20.sol:61
- **Function**: transferFrom
- **Analyzer**: input_validation

Array access 'balanceOf[to]' lacks bounds checking. Out-of-bounds access causes revert but wastes gas. OWASP 2025: Input Validation.

**Recommendation**: Add bounds check:
require(to < balanceOf.length, 'Index out of bounds');

#### Missing Array Bounds Validation

- **File**: SimpleERC20.sol:62
- **Function**: transferFrom
- **Analyzer**: input_validation

Array access 'allowance[from]' lacks bounds checking. Out-of-bounds access causes revert but wastes gas. OWASP 2025: Input Validation.

**Recommendation**: Add bounds check:
require(from < allowance.length, 'Index out of bounds');

#### Potential Integer Overflow/Underflow

- **File**: SimpleERC20.sol:36
- **Function**: N/A
- **Analyzer**: static

Arithmetic operation without overflow protection: balanceOf[msg.sender] = balanceOf[msg.sender] - amount;...

**Recommendation**: Use SafeMath library or Solidity 0.8+ which has built-in overflow protection

#### Potential Integer Overflow/Underflow

- **File**: SimpleERC20.sol:37
- **Function**: N/A
- **Analyzer**: static

Arithmetic operation without overflow protection: balanceOf[to] = balanceOf[to] + amount;...

**Recommendation**: Use SafeMath library or Solidity 0.8+ which has built-in overflow protection

#### Potential Integer Overflow/Underflow

- **File**: SimpleERC20.sol:60
- **Function**: N/A
- **Analyzer**: static

Arithmetic operation without overflow protection: balanceOf[from] = balanceOf[from] - amount;...

**Recommendation**: Use SafeMath library or Solidity 0.8+ which has built-in overflow protection

#### Potential Integer Overflow/Underflow

- **File**: SimpleERC20.sol:61
- **Function**: N/A
- **Analyzer**: static

Arithmetic operation without overflow protection: balanceOf[to] = balanceOf[to] + amount;...

**Recommendation**: Use SafeMath library or Solidity 0.8+ which has built-in overflow protection

#### Potential Integer Overflow/Underflow

- **File**: SimpleERC20.sol:62
- **Function**: N/A
- **Analyzer**: static

Arithmetic operation without overflow protection: allowance[from][msg.sender] = allowance[from][msg.sender] - amount;...

**Recommendation**: Use SafeMath library or Solidity 0.8+ which has built-in overflow protection

#### Potential Integer Overflow/Underflow

- **File**: SimpleERC20.sol:75
- **Function**: N/A
- **Analyzer**: static

Arithmetic operation without overflow protection: balanceOf[recipients[i]] = balanceOf[recipients[i]] + amounts[i];...

**Recommendation**: Use SafeMath library or Solidity 0.8+ which has built-in overflow protection

#### Potential Integer Overflow/Underflow

- **File**: SimpleERC20.sol:76
- **Function**: N/A
- **Analyzer**: static

Arithmetic operation without overflow protection: totalSupply = totalSupply + amounts[i];...

**Recommendation**: Use SafeMath library or Solidity 0.8+ which has built-in overflow protection

#### Potential Integer Overflow/Underflow

- **File**: SimpleERC20.sol:85
- **Function**: N/A
- **Analyzer**: static

Arithmetic operation without overflow protection: balanceOf[msg.sender] = balanceOf[msg.sender] - amount;...

**Recommendation**: Use SafeMath library or Solidity 0.8+ which has built-in overflow protection

#### Potential Integer Overflow/Underflow

- **File**: SimpleERC20.sol:86
- **Function**: N/A
- **Analyzer**: static

Arithmetic operation without overflow protection: totalSupply = totalSupply - amount;...

**Recommendation**: Use SafeMath library or Solidity 0.8+ which has built-in overflow protection

#### Redundant Storage Access

- **File**: SimpleERC20.sol:36
- **Function**: transfer
- **Analyzer**: gas

Same storage location accessed multiple times in a single expression. Consider caching in memory.

**Recommendation**: Cache the storage value in a memory variable and reuse it.

#### Redundant Storage Access

- **File**: SimpleERC20.sol:37
- **Function**: transfer
- **Analyzer**: gas

Same storage location accessed multiple times in a single expression. Consider caching in memory.

**Recommendation**: Cache the storage value in a memory variable and reuse it.

#### Redundant Storage Access

- **File**: SimpleERC20.sol:60
- **Function**: transferFrom
- **Analyzer**: gas

Same storage location accessed multiple times in a single expression. Consider caching in memory.

**Recommendation**: Cache the storage value in a memory variable and reuse it.

#### Redundant Storage Access

- **File**: SimpleERC20.sol:61
- **Function**: transferFrom
- **Analyzer**: gas

Same storage location accessed multiple times in a single expression. Consider caching in memory.

**Recommendation**: Cache the storage value in a memory variable and reuse it.

#### Redundant Storage Access

- **File**: SimpleERC20.sol:62
- **Function**: transferFrom
- **Analyzer**: gas

Same storage location accessed multiple times in a single expression. Consider caching in memory.

**Recommendation**: Cache the storage value in a memory variable and reuse it.

#### Redundant Storage Access

- **File**: SimpleERC20.sol:75
- **Function**: batchMint
- **Analyzer**: gas

Same storage location accessed multiple times in a single expression. Consider caching in memory.

**Recommendation**: Cache the storage value in a memory variable and reuse it.

#### Redundant Storage Access

- **File**: SimpleERC20.sol:85
- **Function**: burn
- **Analyzer**: gas

Same storage location accessed multiple times in a single expression. Consider caching in memory.

**Recommendation**: Cache the storage value in a memory variable and reuse it.

#### Use Unchecked Block for Loop Counter

- **File**: SimpleERC20.sol:74
- **Function**: batchMint
- **Analyzer**: gas

Loop counters in Solidity 0.8+ have overflow checks. Use unchecked{} block for loop increments to save gas.

**Recommendation**: Wrap loop increments in unchecked{} blocks. Loop counters will never realistically overflow.

#### [Symbolic Execution] Potential Integer Overflow in batchMint

- **File**: SimpleERC20.sol:74
- **Function**: batchMint
- **Analyzer**: symbolic

Addition `i = 0; i < recipients.length; i + +)` at line 74 can overflow without `unchecked` block or overflow protection.

**Recommendation**: Use Solidity 0.8+ which has built-in overflow protection, or wrap arithmetic in `unchecked {}` only when overflow is intended. Consider using SafeMath library for Solidity <0.8.

#### [Symbolic Execution] Potential Integer Overflow in batchMint

- **File**: SimpleERC20.sol:76
- **Function**: batchMint
- **Analyzer**: symbolic

Addition `totalSupply = totalSupply + amounts[i]` at line 76 can overflow without `unchecked` block or overflow protection.

**Recommendation**: Use Solidity 0.8+ which has built-in overflow protection, or wrap arithmetic in `unchecked {}` only when overflow is intended. Consider using SafeMath library for Solidity <0.8.

### LOW (8)

#### Use Prefix Increment (++i) Instead of Postfix (i++)

- **File**: SimpleERC20.sol:74
- **Function**: batchMint
- **Analyzer**: gas

Prefix increment (++i) is slightly cheaper than postfix (i++) in loops.

**Recommendation**: Use ++i instead of i++ in loops to save gas.

#### Function 'approve' Can Be External

- **File**: SimpleERC20.sol:44
- **Function**: approve
- **Analyzer**: gas

Function is marked 'public' but appears to never be called internally. Use 'external' to save gas.

**Recommendation**: Change 'public' to 'external' for functions not called internally. External functions can read arguments from calldata instead of copying to memory.

#### Function 'transferFrom' Can Be External

- **File**: SimpleERC20.sol:54
- **Function**: transferFrom
- **Analyzer**: gas

Function is marked 'public' but appears to never be called internally. Use 'external' to save gas.

**Recommendation**: Change 'public' to 'external' for functions not called internally. External functions can read arguments from calldata instead of copying to memory.

#### Function 'batchMint' Can Be External

- **File**: SimpleERC20.sol:69
- **Function**: batchMint
- **Analyzer**: gas

Function is marked 'public' but appears to never be called internally. Use 'external' to save gas.

**Recommendation**: Change 'public' to 'external' for functions not called internally. External functions can read arguments from calldata instead of copying to memory.

#### Function 'burn' Can Be External

- **File**: SimpleERC20.sol:82
- **Function**: burn
- **Analyzer**: gas

Function is marked 'public' but appears to never be called internally. Use 'external' to save gas.

**Recommendation**: Change 'public' to 'external' for functions not called internally. External functions can read arguments from calldata instead of copying to memory.

#### Cache msg.sender

- **File**: SimpleERC20.sol:36
- **Function**: transfer
- **Analyzer**: gas

msg.sender is accessed 2 times. Cache it in a local variable.

**Recommendation**: Cache msg.sender in a local variable at the start of the function.

#### Cache msg.sender

- **File**: SimpleERC20.sol:62
- **Function**: transferFrom
- **Analyzer**: gas

msg.sender is accessed 2 times. Cache it in a local variable.

**Recommendation**: Cache msg.sender in a local variable at the start of the function.

#### Cache msg.sender

- **File**: SimpleERC20.sol:85
- **Function**: burn
- **Analyzer**: gas

msg.sender is accessed 2 times. Cache it in a local variable.

**Recommendation**: Cache msg.sender in a local variable at the start of the function.
