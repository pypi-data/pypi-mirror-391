"""
AWS Systems Manager Module
===========================

Provides centralized operational management and patch compliance.

AWS Systems Manager:
- Automated patch management
- Maintenance windows for scheduled operations
- Session Manager for secure access
- State Manager for configuration compliance
- Integration with compliance frameworks
"""

from .patch import create_patch_baseline, create_patch_group
from .maintenance import create_maintenance_window, create_maintenance_window_task, create_maintenance_window_target
from .iam_role import create_ssm_maintenance_iam_role
from .resources import create_systems_manager_resources

__all__ = [
    "create_patch_baseline",
    "create_patch_group",
    "create_maintenance_window",
    "create_maintenance_window_task",
    "create_maintenance_window_target",
    "create_ssm_maintenance_iam_role",
    "create_systems_manager_resources",
]
