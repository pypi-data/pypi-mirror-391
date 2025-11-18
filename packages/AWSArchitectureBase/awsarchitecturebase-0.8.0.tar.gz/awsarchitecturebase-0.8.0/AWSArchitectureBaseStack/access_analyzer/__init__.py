"""
AWS IAM Access Analyzer Module
===============================

Analyzes resource policies to identify unintended external access.

Public Functions:
-----------------
- create_access_analyzer() - Enable IAM Access Analyzer
"""

from .analyzer import create_access_analyzer

__all__ = [
    'create_access_analyzer',
]
