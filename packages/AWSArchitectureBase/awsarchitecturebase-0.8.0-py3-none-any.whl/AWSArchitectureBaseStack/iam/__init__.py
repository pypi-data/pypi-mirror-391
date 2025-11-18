"""
IAM (Identity and Access Management) module.

This package contains functions and utilities for managing AWS IAM resources
including users, access keys, policies, and roles.
"""

from .user import create_iam_user_with_key
from .policy import create_iam_policy_from_file
from .resources import create_iam_resources
from .service_roles import create_service_role
from .support_role import create_aws_support_role

__all__ = [
    "create_iam_user_with_key",
    "create_iam_policy_from_file",
    "create_iam_resources",
    "create_service_role",
    "create_aws_support_role",
]
