"""
API Security Sentinel Agent Module

Enterprise-grade API security platform with unified REST + GraphQL security analysis.
Provides comprehensive vulnerability detection, business logic vulnerability assessment, and real-time monitoring.

Core Capabilities:
- REST API security scanning (OpenAPI/Swagger parsing)
- GraphQL security analysis (schema analysis, injection testing)
- Business logic vulnerability detection (AI-enhanced)
- Real-time API monitoring and alerting
- Multi-protocol support (REST, GraphQL, WebSocket, gRPC)
- Enterprise features (SSO/SOC2, integrations, compliance)
"""

from .api_security_sentinel import APISecurityAgentWrapper

__all__ = ["APISecurityAgentWrapper"]

__version__ = "1.0.0"
