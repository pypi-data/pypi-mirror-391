"""
CI/CD Pipeline Guardian Agent Module

Enterprise-grade CI/CD pipeline security monitoring and threat detection.
Provides comprehensive analysis of GitHub Actions, GitLab CI, Jenkins, and other pipeline configurations.

Main capabilities:
- Poisoned Pipeline Execution (PPE) detection
- GitHub Actions vulnerability scanning  
- Secrets detection in workflows
- Permissions and privilege escalation analysis
- Supply chain security monitoring
- Real-time pipeline threat assessment
"""

from .cicd_guardian import CicdGuardianAgentWrapper

__all__ = ["CicdGuardianAgentWrapper"]
