"""
AWS Security Hub Module
=======================

Provides centralized security findings management and compliance monitoring.

AWS Security Hub:
- Aggregates security findings from AWS services and third-party tools
- Provides continuous security posture assessment
- Enables compliance standards (CIS, PCI-DSS, AWS Foundational Security Best Practices)
- Automated security checks and remediation guidance
"""

from .account import enable_security_hub_account
from .standards import enable_security_standards, enable_ftr_compliance_standards
from .resources import create_security_hub_resources

__all__ = [
    "enable_security_hub_account",
    "enable_security_standards",
    "enable_ftr_compliance_standards",
    "create_security_hub_resources",
]
