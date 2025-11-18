"""
Silent Agent Loader Utility

Loads optional agent modules silently without spamming warnings to users.
Logs are kept at DEBUG level for developers only.
"""

import logging
from typing import Optional, Any

# Use Python's standard logging instead of loguru for more control
logger = logging.getLogger(__name__)


def load_agent_module_silent(module_path: str, agent_name: str) -> tuple[bool, Optional[Any]]:
    """
    Silently load an agent module.
    
    Args:
        module_path: Full module path (e.g., 'alprina.agents')
        agent_name: Name of agent to get
        
    Returns:
        Tuple of (success: bool, agent_class: Optional[Any])
    """
    try:
        from alprina.agents import get_agent_by_name
        logger.debug(f"✓ Agent '{agent_name}' loaded successfully")
        return True, get_agent_by_name
    except ImportError as e:
        # Only log at DEBUG level - invisible to normal users
        logger.debug(f"Agent '{agent_name}' not available: {e}")
        return False, None
    except Exception as e:
        logger.debug(f"Failed to load agent '{agent_name}': {e}")
        return False, None


def get_local_agent(agent_name: str) -> Optional[Any]:
    """
    Load a local agent from the agents directory.
    
    Args:
        agent_name: Name of the local agent to load
        
    Returns:
        Agent instance or None if not found
    """
    try:
        # Import the local agent wrapper
        if agent_name == "cicd_guardian":
            from alprina_cli.agents.cicd_guardian import CicdGuardianAgentWrapper
            return CicdGuardianAgentWrapper()
        elif agent_name == "web3_auditor":
            from alprina_cli.agents.web3_auditor import Web3AuditorAgentWrapper
            return Web3AuditorAgentWrapper()
        # Add more local agents here as they're implemented
        else:
            from alprina_cli.agents.red_teamer import RedTeamerAgentWrapper
            if agent_name == "red_teamer":
                return RedTeamerAgentWrapper()
    except ImportError as e:
        logger.debug(f"Local agent '{agent_name}' not available: {e}")
        return None
    except Exception as e:
        logger.debug(f"Failed to load local agent '{agent_name}': {e}")
        return None


# Agent availability flag
CAI_AVAILABLE = False

# Try to import once at module level
try:
    from alprina.agents import get_agent_by_name
    CAI_AVAILABLE = True
    logger.debug("Alprina agents framework available")
except ImportError:
    logger.debug("Alprina agents framework not available (optional dependency)")
