"""
Multi-Chain Blockchain Scanner

Supports analysis across multiple blockchain platforms:
- Ethereum & EVM compatible chains (Polygon, BSC, Arbitrum, Optimism)
- Solana blockchain programs
- Cross-chain bridge security analysis
- Chain-specific vulnerability patterns
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

class BlockchainType(Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon" 
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"
    SOLANA = "solana"

@dataclass
class ChainProfile:
    """Profile for each blockchain platform"""
    type: BlockchainType
    name: str
    network_id: int
    rpc_url: str
    native_token: str
    max_gas_limit: int
    average_block_time: int  # seconds
    typical_gas_cost: int  # gwei
    security_considerations: List[str]

class MultiChainScanner:
    """
    Multi-chain blockchain scanner for comprehensive Web3 security
    """
    
    def __init__(self):
        self.supported_chains = self._initialize_chain_profiles()
        self.chain_specific_patterns = self._initialize_chain_patterns()
    
    def scan_blockchain_context(self, code: str, context_chain: str = "ethereum") -> Dict[str, Any]:
        """
        Analyze blockchain-specific security considerations
        
        Args:
            code: Contract or program code
            context_chain: Target blockchain platform
            
        Returns:
            Blockchain-specific security analysis
        """
        chain_type = self._parse_chain_type(context_chain)
        if not chain_type:
            return {'error': f'Unsupported blockchain: {context_chain}'}
        
        profile = self.supported_chains[chain_type]
        
        # Chain-specific security patterns
        patterns = self.chain_specific_patterns.get(chain_type, {})
        
        security_analysis = {
            'blockchain': profile.name,
            'chain_specific_vulnerabilities': [],
            'gas_optimizations': [],
            'cross_chain_considerations': [],
            'economic_impact_factors': []
        }
        
        # Analyze for chain-specific patterns
        code_lower = code.lower()
        
        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if pattern in code_lower:
                    vulnerability = {
                        'type': pattern_type,
                        'pattern': pattern,
                        'description': self._get_pattern_description(pattern_type, chain_type),
                        'severity': self._get_pattern_severity(pattern_type, chain_type),
                        'blockchain': profile.name
                    }
                    security_analysis['chain_specific_vulnerabilities'].append(vulnerability)
        
        # Add cross-chain considerations
        cross_chain_risks = self._analyze_cross_chain_risks(code, chain_type)
        security_analysis['cross_chain_considerations'] = cross_chain_risks
        
        # Add economic impact factors
        economic_factors = self._analyze_economic_impact_factors(code, chain_type)
        security_analysis['economic_impact_factors'] = economic_factors
        
        return security_analysis
    
    def get_chain_vulnerabilities(self, blockchain: str) -> List[Dict[str, Any]]:
        """
        Get known vulnerabilities and attack vectors for specific blockchain
        """
        chain_type = self._parse_chain_type(blockchain)
        if not chain_type:
            return []
        
        vulnerabilities = []
        
        # Chain-specific vulnerability database
        chain_vulns = {
            BlockchainType.ETHEREUM: [
                {
                    'type': 'gas_limit',
                    'description': 'Gas limit exhaustion attacks',
                    'severity': 'medium',
                    'examples': ['Bancor exploitation', 'Parity wallet freeze']
                },
                {
                    'type': 'self_destruct',
                    'description': 'Self-destruct function abuse',
                    'severity': 'high',
                    'examples': ['Parity multisig wallet', 'Multiple DeFi hacks']
                }
            ],
            BlockchainType.POLYGON: [
                {
                    'type': 'low_gas_fees',
                    'description': 'Low gas enables cheap spam attacks',
                    'severity': 'medium',
                    'examples': ['MEV extraction exploitation']
                },
                {
                    'type': 'bridge_dependency',
                    'description': 'Cross-chain bridge dependency risks',
                    'severity': 'high',
                    'examples': ['Cross-chain bridge exploits']
                }
            ],
            BlockchainType.SOLANA: [
                {
                    'type': 'account_rent', 
                    'description': 'Account rent exhaustion attacks',
                    'severity': 'medium',
                    'examples': ['Account rent bug']
                },
                {
                    'type': 'network_partition',
                    'description': 'Network partition vulnerabilities',
                    'severity': 'high',
                    'examples': ['DDoS attacks on validators']
                }
            ]
        }
        
        return chain_vulns.get(chain_type, [])
    
    def analyze_cross_chain_bridge(self, bridge_code: str, source_chain: str, target_chain: str) -> Dict[str, Any]:
        """
        Analyze cross-chain bridge security
        """
        source = self._parse_chain_type(source_chain)
        target = self._parse_chain_type(target_chain)
        
        if not source or not target:
            return {'error': 'Unsupported blockchain for bridge analysis'}
        
        bridge_analysis = {
            'source_chain': source_chain,
            'target_chain': target_chain,
            'vulnerabilities': [],
            'economic_risks': [],
            'recommendations': []
        }
        
        # Common bridge vulnerability patterns
        bridge_patterns = [
            ('mint', 'Fake token minting', 'critical'),
            ('burn', 'Invalid burn validation', 'high'),
            ('swap', 'Exchange rate manipulation', 'high'),
            ('fee', 'Fee manipulation attacks', 'medium'),
            ('delay', 'Withdrawal delay exploitation', 'medium')
        ]
        
        code_lower = bridge_code.lower()
        for pattern, description, severity in bridge_patterns:
            if pattern in code_lower:
                vulnerability = {
                    'pattern': pattern,
                    'description': description,
                    'severity': severity,
                    'context': 'cross-chain bridge'
                }
                bridge_analysis['vulnerabilities'].append(vulnerability)
        
        # Add economic risk assessment
        economic_risks = self._assess_bridge_economic_risks(bridge_code, source, target)
        bridge_analysis['economic_risks'] = economic_risks
        
        return bridge_analysis
    
    def _initialize_chain_profiles(self) -> Dict[BlockchainType, ChainProfile]:
        """Initialize blockchain profiles"""
        return {
            BlockchainType.ETHEREUM: ChainProfile(
                type=BlockchainType.ETHEREUM,
                name="Ethereum Mainnet",
                network_id=1,
                rpc_url="https://eth.llamarpc.com",
                native_token="ETH",
                max_gas_limit=30000000,
                average_block_time=12,
                typical_gas_cost=20,
                security_considerations=[
                    "High gas costs limit attack viability",
                    "Mature security ecosystem",
                    "Extensive tooling available",
                    "Complex DeFi ecosystem increases attack surface"
                ]
            ),
            BlockchainType.POLYGON: ChainProfile(
                type=BlockchainType.POLYGON,
                name="Polygon",
                network_id=137,
                rpc_url="https://polygon.llamarpc.com",
                native_token="MATIC",
                max_gas_limit=20000000,
                average_block_time=2,
                typical_gas_cost=30,
                security_considerations=[
                    "Low gas costs enable cheap attacks",
                    "Cross-chain bridge dependencies",
                    "Fast block times increase race condition risks",
                    "Less mature security tools than Ethereum"
                ]
            ),
            BlockchainType.BSC: ChainProfile(
                type=BlockchainType.BSC,
                name="BNB Smart Chain",
                network_id=56,
                rpc_url="https://bsc.llamarpc.com",
                native_token="BNB",
                max_gas_limit=30000000,
                average_block_time=3,
                typical_gas_cost=5,
                security_considerations=[
                    "Validator centralization risks",
                    "Lower security standards than Ethereum",
                    "Faster transactions increase attack vectors",
                    "BSC bridge vulnerabilities"
                ]
            ),
            BlockchainType.SOLANA: ChainProfile(
                type=BlockchainType.SOLANA,
                name="Solana",
                network_id=0,  # Solana uses different ID system
                rpc_url="https://api.mainnet-beta.solana.com",
                native_token="SOL",
                max_gas_limit=1400000,  # Compute units, not gas
                average_block_time=0.4,  # ~400ms
                typical_gas_cost=0,  # Transactions prioritized by fees
                security_considerations=[
                    "No gas limits → possible DoS vectors",
                    "Account rent system creates new attack surface",
                    "Network partition vulnerabilities",
                    "Different programming model requires specialized tools"
                ]
            )
        }
    
    def _initialize_chain_patterns(self) -> Dict[BlockchainType, Dict[str, List[str]]]:
        """Initialize chain-specific vulnerability patterns"""
        return {
            BlockchainType.ETHEREUM: {
                'gas_griefing': ['selfdestruct', 'gas', 'block.gaslimit'],
                'reentrancy': ['call', 'send', 'transfer'],
                'access_control': ['onlyOwner', 'require', 'modifiers'],
                'gas_optimization': ['assembly', 'bytes', 'memory']
            },
            BlockchainType.POLYGON: {
                'low_gas_spam': ['spam', 'attacker', 'griefing'],
                'bridge_risks': ['polygon_bridge', 'cross_chain', 'withdraw'],
                'mev_extraction': ['mev', 'arbitrage', 'front_run'],
                'gas_optimization': ['optimistic', 'rollups']
            },
            BlockchainType.BSC: {
                'validator_risks': ['validator', 'staking', 'centralized'],
                'cross_chain': ['bridge', 'wormhole', 'bnb'],
                'copy_ethereum_patterns': ['fork', 'ethereum', 'hardhat'],
                'speed_attacks': ['fast_blocks', 'race_condition']
            },
            BlockchainType.SOLANA: {
                'rent_attack': ['account_rent', 'rent exemption', 'lamports'],
                'network_partition': ['partition', 'ddos', 'validators'],
                'account_model': ['account_info', 'system_program', 'pda'],
                'mev_exploitation': ['mev', 'priority_fee', 'jito']
            }
        }
    
    def _parse_chain_type(self, chain_name: str) -> Optional[BlockchainType]:
        """Parse chain name to enum type"""
        chain_map = {
            'ethereum': BlockchainType.ETHEREUM,
            'eth': BlockchainType.ETHEREUM,
            'mainnet': BlockchainType.ETHEREUM,
            'polygon': BlockchainType.POLYGON,
            'matic': BlockchainType.POLYGON,
            'bsc': BlockchainType.BSC,
            'binance': BlockchainType.BSC,
            'solana': BlockchainType.SOLANA,
            'sol': BlockchainType.SOLANA
        }
        
        return chain_map.get(chain_name.lower())
    
    def _get_pattern_description(self, pattern_type: str, chain: BlockchainType) -> str:
        """Get description for chain-specific pattern"""
        descriptions = {
            'gas_griefing': "Gas exhaustion attack vectors",
            'reentrancy': "Reentrancy vulnerabilities",
            'low_gas_spam': "Low gas enables spam attacks",
            'bridge_risks': "Cross-chain bridge vulnerabilities",
            'rent_attack': "Account rent exhaustion attacks",
            'network_partition': "Network partition vulnerabilities"
        }
        return descriptions.get(pattern_type, f"{pattern_type} vulnerability")
    
    def _get_pattern_severity(self, pattern_type: str, chain: BlockchainType) -> str:
        """Get severity level for chain-specific pattern"""
        severity_map = {
            BlockchainType.ETHEREUM: {
                'gas_griefing': 'medium',  # High gas limits mitigate
                'reentrancy': 'high',
                'mev_extraction': 'high'
            },
            BlockchainType.POLYGON: {
                'low_gas_spam': 'high',      # Low gas enables spam
                'bridge_risks': 'critical',  # Bridge dependencies are critical
                'mev_extraction': 'high'
            },
            BlockchainType.SOLANA: {
                'rent_attack': 'medium',
                'network_partition': 'critical',
                'mev_exploitation': 'high'
            }
        }
        return severity_map.get(chain, {}).get(pattern_type, 'medium')
    
    def _analyze_cross_chain_risks(self, code: str, chain_type: BlockchainType) -> List[Dict[str, Any]]:
        """Analyze cross-chain bridge and protocol interaction risks"""
        cross_chain_risks = []
        
        code_lower = code.lower()
        
        # Check for bridge integrations
        if any(bridge_token in code_lower for bridge_token in ['bridge', 'wormhole', 'layerzero']):
            risk = {
                'type': 'bridge_dependency',
                'description': 'Cross-chain bridge integration detected',
                'severity': 'high',
                'mitigation': 'Validate bridge security and implement withdrawal delays'
            }
            cross_chain_risks.append(risk)
        
        # Check for multi-chain deployment patterns
        if any(multi_token in code_lower for multi_token in ['polygon', 'bsc', 'arbitrum']):
            risk = {
                'type': 'multi_chain_deployment',
                'description': 'Multi-chain deployment increases attack surface',
                'severity': 'medium',
                'mitigation': 'Ensure consistent security across all chains'
            }
            cross_chain_risks.append(risk)
        
        return cross_chain_risks
    
    def _analyze_economic_impact_factors(self, code: str, chain_type: BlockchainType) -> List[Dict[str, Any]]:
        """Analyze factors affecting economic impact of vulnerabilities"""
        impact_factors = []
        
        profile = self.supported_chains.get(chain_type)
        if not profile:
            return impact_factors
        
        # Gas cost impact
        if profile.typical_gas_cost > 50:
            impact_factors.append({
                'factor': 'high_gas_costs',
                'impact': 'reduces attack viability but increases user cost',
                'severity': 'medium'
            })
        elif profile.typical_gas_cost < 10:
            impact_factors.append({
                'factor': 'low_gas_costs',
                'impact': 'enables cheap attacks and spam',
                'severity': 'high'
            })
        
        # Block time impact
        if profile.average_block_time > 10:
            impact_factors.append({
                'factor': 'slow_blocks',
                'impact': 'slower response to attacks but higher finality',
                'severity': 'low'
            })
        elif profile.average_block_time < 2:
            impact_factors.append({
                'factor': 'fast_blocks',
                'impact': 'enables faster attacks and MEV extraction',
                'severity': 'medium'
            })
        
        return impact_factors
    
    def _assess_bridge_economic_risks(self, code: str, source: BlockchainType, target: BlockchainType) -> List[Dict[str, Any]]:
        """Assess economic risks in cross-chain bridges"""
        economic_risks = []
        
        # Check for liquidity provision risks
        if 'liquidity' in code.lower() or 'pool' in code.lower():
            risk = {
                'type': 'liquidity_manipulation',
                'description': 'Liquidity pool manipulation attacks',
                'potential_loss': 'Complete liquidity drain',
                'severity': 'critical'
            }
            economic_risks.append(risk)
        
        # Check for mint/burn validation
        if ('mint' in code.lower() and 'require' not in code.lower()) or \
           ('burn' in code.lower() and 'require' not in code.lower()):
            risk = {
                'type': 'token_manipulation',
                'description': 'Invalid token mint/burn validation',
                'potential_loss': 'Token supply manipulation',
                'severity': 'critical'
            }
            economic_risks.append(risk)
        
        return economic_risks
