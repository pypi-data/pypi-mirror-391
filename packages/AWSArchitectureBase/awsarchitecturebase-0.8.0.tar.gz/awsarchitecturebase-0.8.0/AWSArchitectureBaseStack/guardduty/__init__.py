"""
AWS GuardDuty Module
====================

Threat detection service monitoring AWS accounts and workloads.

Public Functions:
-----------------
- create_guardduty_detector() - Enable GuardDuty detector
"""

from .detector import create_guardduty_detector

__all__ = [
    'create_guardduty_detector',
]
