"""
AWS Inspector Module
====================

Provides automated vulnerability scanning for AWS resources.

AWS Inspector v2:
- Automated vulnerability discovery
- Continuous scanning for EC2 instances
- Container image scanning (ECR)
- Lambda function scanning
- Network reachability analysis
- Integration with Security Hub
"""

from .enablement import enable_inspector
from .resources import create_inspector_resources

__all__ = [
    "enable_inspector",
    "create_inspector_resources",
]
