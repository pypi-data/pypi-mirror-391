"""
AWS Backup Module
=================

Provides centralized backup management for AWS resources.

AWS Backup:
- Centralized backup policies across AWS services
- Automated backup scheduling
- Backup lifecycle management
- Cross-region and cross-account backup
- Compliance and audit reporting
"""

from .vault import create_backup_vault
from .plan import create_backup_plan, create_backup_selection
from .iam_role import create_backup_iam_role
from .resources import create_backup_resources

__all__ = [
    "create_backup_vault",
    "create_backup_plan",
    "create_backup_selection",
    "create_backup_iam_role",
    "create_backup_resources",
]
