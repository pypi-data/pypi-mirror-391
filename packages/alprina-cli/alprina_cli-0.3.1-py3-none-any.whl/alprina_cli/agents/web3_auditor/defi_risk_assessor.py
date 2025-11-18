"""
DeFi Economic Risk Assessor with AI Enhancement

Analyzes smart contracts for economic attack vectors that traditional static analysis misses.
Uses both pattern matching and LLM-powered contextual analysis.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class EconomicRiskType(Enum):
    FLASH_LOAN_ATTACK = "flash_loan_attack"
    PRICE_ORACLE_MANIPULATION = "price_oracle_manipulation"
    LIQUIDITY_DRAIN = "liquidity_drain"
    MEV_EXTRACTION = "mev_extraction"
    YIELD_FARMING_EXPLOIT = "yield_farming_exploit"
    CROSS_CHAIN_BRIDGE = "cross_chain_bridge"
    TOKEN_MINT_MANIPULATION = "token_mint_manipulation"
    GOVERNANCE_ATTACK = "governance_attack"

@dataclass
class EconomicRisk:
    """Represents an economic risk in a DeFi protocol"""
    risk_type: EconomicRiskType
    severity: str  # "critical", "high", "medium", "low" 
    title: str
    description: str
    attack_scenario: str
    file_path: str
    line_number: Optional[int]
    contract_name: str
    economic_impact: str
    remediation: str
    confidence: int = 80  # 0-100

class DeFiRiskAssessor:
    """
    AI-powered DeFi economic risk assessor
    Goes beyond code vulnerabilities to detect business logic flaws
    """
    
    def __init__(self):
        self.risk_patterns = self._initialize_risk_patterns()
        self.llm_client = self._initialize_llm_client()
    
    def assess_economic_risks(self, contract_code: str, protocol_context: Dict[str, Any]) -> List[EconomicRisk]:
        """
        Comprehensive economic risk assessment for DeFi protocols
        
        Args:
            contract_code: Solidity or other blockchain contract code
            protocol_context: Information about the DeFi protocol
            
        Returns:
            List of detected economic risks
        """
        risks = []
        
        # Traditional pattern-based analysis
        flash_loan_risks = self._detect_flash_loan_vulnerabilities(contract_code, protocol_context)
        oracle_risks = self._detect_price_oracle_risks(contract_code, protocol_context)
        liquidity_risks = self._detect_liquidity_drain_risks(contract_code, protocol_context)
        governance_risks = self._detect_governance_attacks(contract_code, protocol_context)
        
        risks.extend(flash_loan_risks)
        risks.extend(oracle_risks)
        risks.extend(liquidity_risks)
        risks.extend(governance_risks)
        
        # AI-enhanced analysis for complex patterns
        llm_risks = self._llm_economic_analysis(contract_code, protocol_context)
        risks.extend(llm_risks)
        
        return risks
    
    def _detect_flash_loan_vulnerabilities(self, contract_code: str, context: Dict[str, Any]) -> List[EconomicRisk]:
        """Detect flash loan attack vectors"""
        risks = []
        lines = contract_code.split('\n')
        
        for i, line in enumerate(lines):
            line_content = line.strip()
            
            # Pattern 1: Functions that update state based on token balances
            if any(pattern in line_content for pattern in ['balanceOf', 'totalSupply', 'reserve']):
                # Check if this is a liquidity function
                next_lines = lines[i+1:i+10]  # Look at next several lines
                function_block = '\n'.join(next_lines)
                
                if 'update' in function_block.lower() or 'calculate' in function_block.lower():
                    # Look for missing reentrancy checks or price validation
                    has_protection = any(
                        protection in function_block.lower() 
                        for protection in ['reentrancyguard', 'nonreentrant', 'require(msg.value']
                    )
                    
                    if not has_protection:
                        risk = EconomicRisk(
                            risk_type=EconomicRiskType.FLASH_LOAN_ATTACK,
                            severity="high",
                            title="Flash Loan Manipulation Risk",
                            description="Function updates state based on balances without flash loan protection",
                            attack_scenario="Attacker takes flash loan → Manipulates token prices → Exploits price-dependent calculation → Repays loan with profit",
                            file_path=context.get('file_path', 'unknown'),
                            line_number=i + 1,
                            contract_name=context.get('contract_name', 'unknown'),
                            economic_impact="Potential protocol fund drain if exploited",
                            remediation="Add reentrancy protection and validate price calculations with time-weighted averages",
                            confidence=75
                        )
                        risks.append(risk)
        
        # Pattern 2: Liquidity provision functions with price calculation
        liquidity_patterns = ['addLiquidity', 'removeLiquidity', 'swap', 'exchange']
        for pattern in liquidity_patterns:
            context_window = contract_code[max(0, i-5):i+5]
            if pattern in context_window and 'calculate' in context_window:
                # Check for price oracle usage
                if 'uniswap' in context_window.lower() or 'getAmountsOut' in context_window:
                    risk = EconomicRisk(
                        risk_type=EconomicRiskType.FLASH_LOAN_ATTACK,
                        severity="high", 
                        title="Flash Loan Oracle Manipulation",
                        description="Liquidity function uses on-chain price oracle vulnerable to manipulation",
                        attack_scenario="Attaker uses flash loan to manipulate exchange rate → Drains liquidity pool → Repays loan",
                        file_path=context.get('file_path', 'unknown'),
                        line_number=i + 1,
                        contract_name=context.get('contract_name', 'unknown'),
                        economic_impact="Complete liquidity pool drain possible",
                        remediation="Use TWAP price oracle or validate against multiple sources",
                        confidence=80
                    )
                    risks.append(risk)
        
        return risks
    
    def _detect_price_oracle_risks(self, contract_code: str, context: Dict[str, Any]) -> List[EconomicRisk]:
        """Detect price oracle manipulation vulnerabilities"""
        risks = []
        lines = contract_code.split('\n')
        
        oracle_sources = ['uniswap', 'sushiswap', 'curve', 'balancer', 'getAmountsOut']
        
        for i, line in enumerate(lines):
            line_content = line.strip()
            
            # Check for direct oracle usage without validation
            for oracle in oracle_sources:
                if oracle in line_content.lower():
                    # Look at surrounding code for price usage
                    context_lines = lines[max(0, i-3):i+8]  # 3 lines before, 7 after
                    context_block = '\n'.join(context_lines)
                    
                    # Check for price-dependent calculations
                    if any(calc in context_block for calc in ['amount', 'price', 'value', 'calculate']):
                        # Check for validation
                        has_validation = any(
                            validation in context_block.lower() 
                            for validation in ['min', 'max', '>=', '<=', 'require']
                        )
                        
                        if not has_validation:
                            risk = EconomicRisk(
                                risk_type=EconomicRiskType.PRICE_ORACLE_MANIPULATION,
                                severity="high",
                                title="Unvalidated Price Oracle",
                                description=f"Using {oracle.title()} price oracle without validation",
                                attack_scenario="Attacker manipulates pool reserves → Invalid price data → Protocol miscalculates → Economic loss",
                                file_path=context.get('file_path', 'unknown'),
                                line_number=i + 1,
                                contract_name=context.get('contract_name', 'unknown'),
                                economic_impact="Protocol calculates wrong prices, leading to fund loss",
                                remediation="Implement price deviation checks and use multiple oracle sources",
                                confidence=85
                            )
                            risks.append(risk)
        
        return risks
    
    def _detect_liquidity_drain_risks(self, contract_code: str, context: Dict[str, Any]) -> List[EconomicRisk]:
        """Detect liquidity draining attack vectors"""
        risks = []
        lines = contract_code.split('\n')
        
        # Pattern: Functions that provide liquidity without restrictions
        liquidity_patterns = [
            'function.*withdraw',
            'function.*redeem',
            'function.*claim',
            'function.*removeLiquidity'
        ]
        
        for i, line in enumerate(lines):
            line_content = line.strip()
            
            for pattern in liquidity_patterns:
                if re.search(pattern, line_content):
                    # Look for access controls
                    function_context = lines[max(0, i-2):i+20]  # Function scope
                    function_block = '\n'.join(function_context)
                    
                    has_auth = any(
                        auth in function_block.lower() 
                        for auth in ['onlyowner', 'require', 'modifiers']
                    )
                    
                    has_amount_validation = any(
                        validation in function_block.lower()
                        for validation in ['require.*amount', 'min.*amount', '< balance']
                    )
                    
                    if not has_auth or not has_amount_validation:
                        risk = EconomicRisk(
                            risk_type=EconomicRiskType.LIQUIDITY_DRAIN,
                            severity="critical",
                            title="Liquidity Drain Vulnerability",
                            description="Liquidity withdrawal function lacking proper controls",
                            attack_scenario="Attacker calls unauthorized withdrawal → Drains all available liquidity → Protocol becomes insolvent",
                            file_path=context.get('file_path', 'unknown'),
                            line_number=i + 1,
                            contract_name=context.get('contract_name', 'unknown'),
                            economic_impact="Complete fund loss through liquidity drain",
                            remediation="Add proper access controls, amount validations, and withdrawal limits",
                            confidence=90
                        )
                        risks.append(risk)
        
        return risks
    
    def _detect_governance_attacks(self, contract_code: str, context: Dict[str, Any]) -> List[EconomicRisk]:
        """Detect governance system attack vectors"""
        risks = []
        lines = contract_code.split('\n')
        
        governance_patterns = [
            'function vote',
            'function propose',
            'function execute',
            'function delegate'
        ]
        
        for i, line in enumerate(lines):
            line_content = line.strip()
            
            for pattern in governance_patterns:
                if pattern in line_content:
                    # Check for voting power manipulation risks
                    context_lines = lines[max(0, i-3):i+15]  # Goverance function scope
                    context_block = '\n'.join(context_lines)
                    
                    # Look for token balance usage without time-lock
                    if ('balance' in context_block and 'vote' in context_block.lower()):
                        has_timelock = any(
                            timelock in context_block.lower()
                            for timelock in ['timelock', 'delay', 'waiting', 'period']
                        )
                        
                        if not has_timelock:
                            risk = EconomicRisk(
                                risk_type=EconomicRiskType.GOVERNANCE_ATTACK,
                                severity="high",
                                title="Governance Flash Loan Attack",
                                description="Voting mechanism vulnerable to flash loan manipulation",
                                attack_scenario="Attaker takes flash loan → Gains voting power → Passes malicious proposal → Executes against protocol → Repays loan",
                                file_path=context.get('file_path', 'unknown'),
                                line_number=i + 1,
                                contract_name=context.get('contract_name', 'unknown'),
                                economic_impact="Protocol governance can be seized, leading to full protocol control",
                                remediation="Implement voting power time-locks and minimum holding periods",
                                confidence=80
                            )
                            risks.append(risk)
        
        return risks
    
    def _llm_economic_analysis(self, contract_code: str, context: Dict[str, Any]) -> List[EconomicRisk]:
        """AI-powered economic risk analysis for complex attack vectors"""
        risks = []
        
        try:
            # Prepare context for LLM analysis
            protocol_type = context.get('protocol_type', 'DeFi Protocol')
            contract_name = context.get('contract_name', 'Smart Contract')
            
            prompt = f"""
            Analyze this DeFi smart contract for complex economic attack vectors that traditional static analysis might miss:
            
            Protocol Type: {protocol_type}
            Contract Name: {contract_name}
            
            Contract Code:
            {contract_code}
            
            Focus on these economic attack patterns:
            1. Flash Loan Attack Vectors - identify where price calculations could be manipulated
            2. Cross-Protocol Arbitrage Exploits - look for interactions with other DeFi protocols
            3. MEV (Maximal Extractable Value) opportunities - identify transaction ordering exploits
            4. Token Supply/Governance Manipulation - check for voting/influence manipulation
            5. Liquidity Manipulation Scenarios - identify pool manipulation possibilities
            6. Cross-Chain Bridge Risks - if applicable, check for multi-chain vulnerabilities
            
            For each risk identified, provide:
            - Attack scenario in step-by-step format
            - Economic impact assessment  
            - Mitigation strategies
            
            Analyze deeply and think about complex multi-step attacks.
            """
            
            # Simulate LLM response (in production, this would call actual LLM)
            llm_response = self._simulate_llm_analysis(contract_code, context)
            
            if llm_response:
                # Parse LLM response into EconomicRisk objects
                llm_risks = self._parse_llm_response(llm_response, contract_code, context)
                risks.extend(llm_risks)
                
        except Exception as e:
            # Add fallback risk if LLM analysis fails
            fallback_risk = EconomicRisk(
                risk_type=EconomicRiskType.LIQUIDITY_DRAIN,
                severity="medium",
                title="AI Analysis Limitation",
                description=f"Complete economic analysis unavailable: {str(e)[:100]}",
                attack_scenario="Consider manual security audit for complex economic vectors",
                file_path=context.get('file_path', 'unknown'),
                line_number=None,
                contract_name=context.get('contract_name', 'unknown'),
                economic_impact="Unknown - manual review recommended",
                remediation="Manual security audit recommended for comprehensive economic analysis",
                confidence=30
            )
            risks.append(fallback_risk)
        
        return risks
    
    def _simulate_llm_analysis(self, contract_code: str, context: Dict[str, Any]) -> Optional[str]:
        """Simulate LLM analysis - in production, this would call actual LLM API"""
        
        # Check for common DeFi patterns and return simulated responses
        contract_lower = contract_code.lower()
        
        if 'uniswap' in contract_lower and 'getamountsout' in contract_lower:
            return """
            RISK: Flash Loan Oracle Manipulation
            Severity: High
            
            Description: This contract uses Uniswap price oracle (getAmountsOut) without validation, making it vulnerable to flash loan manipulation attacks.
            
            Attack Scenario:
            1. Attaker identifies large reserves in Uniswap pool
            2. Takes flash loan from Aave/Compound
            3. Uses flash loan to manipulate pool prices
            4. Calls protocol function using manipulated oracle prices
            5. Protocol calculates incorrect prices, allowing arbitrage
            6. Attaker repays flash loan and keeps profit
            
            Economic Impact: Complete liquidity drain possible
            
            Mitigation: Implement TWAP price oracle, validate maximum price deviations
            """
        
        elif 'token' in contract_lower and 'mint' in contract_lower:
            return """
            RISK: Token Supply Manipulation
            Severity: High
            
            Description: Minting function lacks proper access controls, potentially allowing unlimited token creation.
            
            Attack Scenario:
            1. Attaker identifies minting privilege escalation
            2. Mints large number of tokens
            3. Uses tokens to manipulate voting/proportions
            4. Drains platform resources through voting power
            5. Results in protocol fund loss
            
            Economic Impact: Protocol governance and fund control loss
            
            Mitigation: Add strict access controls, implement minting caps, add governance delays
            """
        
        elif 'withdraw' in contract_lower and 'balance' in contract_lower:
            return """
            RISK: Liquidity Drain Attack
            Severity: Critical
            
            Description: Withdrawal function lacks adequate access controls and balance validations.
            
            Attack Scenario:
            1. Attaker identifies unprotected withdrawal function
            2. Calls withdrawal to drain available funds
            3. Protocol becomes insolvent or drained completely
            4. All other users lose access to funds
            
            Economic Impact: Complete fund loss possible
            
            Mitigation: Implement withdrawal limits, access controls, and balance validations
            """
        
        return None
    
    def _parse_llm_response(self, llm_response: str, contract_code: str, context: Dict[str, Any]) -> List[EconomicRisk]:
        """Parse LLM response into EconomicRisk objects"""
        risks = []
        
        try:
            # Parse simulated response format
            if 'RISK:' in llm_response:
                sections = llm_response.split('RISK:')[1:]
                
                for section in sections:
                    lines = section.strip().split('\n')
                    if len(lines) < 5:
                        continue
                    
                    # Extract key information
                    title = lines[0].split(':')[1].strip() if ':' in lines[0] else "Economic Risk"
                    severity = lines[1].split(':')[1].strip().lower() if ':' in lines[1] else "medium"
                    description = lines[2].split(':')[1].strip() if ':' in lines[2] else "Economic vulnerability detected"
                    
                    # Find attack scenario
                    attack_scenario = ""
                    description_start = False
                    for line in lines[3:]:
                        if line.strip().startswith("Attack Scenario:"):
                            description_start = True
                            attack_scenario = line.split("Attack Scenario:")[1].strip()
                        elif description_start:
                            if line.strip().startswith("Economic Impact:"):
                                break
                            attack_scenario += " " + line.strip()
                    
                    # Determine risk type based on content
                    risk_type = EconomicRiskType.LIQUIDITY_DRAIN  # default
                    if "flash loan" in llm_response.lower():
                        risk_type = EconomicRiskType.FLASH_LOAN_ATTACK
                    elif "oracle" in llm_response.lower() or "price" in llm_response.lower():
                        risk_type = EconomicRiskType.PRICE_ORACLE_MANIPULATION
                    elif "token" in llm_response.lower() or "mint" in llm_response.lower():
                        risk_type = EconomicRiskType.TOKEN_MINT_MANIPULATION
                    
                    # Extract economic impact and mitigation
                    economic_impact = "Potential economic loss"
                    remediation = "Security audit recommended"
                    
                    for line in lines:
                        if line.strip().startswith("Economic Impact:"):
                            economic_impact = line.split("Economic Impact:")[1].strip()
                        elif line.strip().startswith("Mitigation:"):
                            remediation = line.split("Mitigation:")[1].strip()
                    
                    risk = EconomicRisk(
                        risk_type=risk_type,
                        severity=severity if severity in ["critical", "high", "medium", "low"] else "medium",
                        title=title,
                        description=description,
                        attack_scenario=attack_scenario.strip(),
                        file_path=context.get('file_path', 'unknown'),
                        line_number=None,
                        contract_name=context.get('contract_name', 'unknown'),
                        economic_impact=economic_impact,
                        remediation=remediation,
                        confidence=75  # LLM-based confidence
                    )
                    risks.append(risk)
        
        except Exception as e:
            # Debug: LLM parsing failed
            pass
        
        return risks
    
    def _initialize_risk_patterns(self) -> Dict[str, List[str]]:
        """Initialize economic risk pattern detectors"""
        return {
            'flash_loan': [
                r'flashloan',
                r'borrow.*flash',
                r'uniswap.*price',
                r'getAmountsOut'
            ],
            'oracle_manipulation': [
                r'oracle',
                r'price.*feed',
                r'uniswap.*router',
                r'chainlink'
            ],
            'liquidity_drain': [
                r'withdraw.*all',
                r'balance.*transfer',
                r'drain.*liquidity'
            ],
            'governance': [
                r'vote.*balance',
                r'governance.*token',
                r'propose.*execute',
                r'timelock'
            ]
        }
    
    def _initialize_llm_client(self):
        """Initialize LLM client - in production, this would connect to Claude/ChatGPT"""
        # For now, return None - LLM logic uses simulated responses
        return None
