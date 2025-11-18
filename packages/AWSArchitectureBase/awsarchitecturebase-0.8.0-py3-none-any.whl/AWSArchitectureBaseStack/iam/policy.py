"""
IAM Policy management utilities.

This module provides functions for creating and managing AWS IAM policies,
including loading policies from files and attaching them to users.
"""

import os
from cdktf_cdktf_provider_aws import iam_user_policy


def load_iam_policy_from_file(file_path: str) -> str:
    """
    Load IAM policy document from a JSON file.

    Reads an IAM policy document from a JSON file. The file_path can be
    absolute or relative to the calling module's directory.

    :param file_path: Path to IAM policy JSON file (absolute or relative)
    :type file_path: str
    :returns: The IAM policy as a JSON string
    :rtype: str
    :raises FileNotFoundError: If the policy file does not exist
    :raises IOError: If there's an error reading the file

    """
    with open(file_path, "r") as f:
        policy = f.read()
    return policy


def create_iam_policy_from_file(
    scope,
    file_path: str,
    user_name: str,
    policy_type: str,
    project_name: str,
    environment: str
) -> iam_user_policy.IamUserPolicy:
    """
    Create IAM policy from JSON file and attach to user.

    Loads an IAM policy document from a JSON file and attaches it to an IAM user.
    This is a generic method useful for any AWS architecture that needs to load
    IAM policies from external files.

    :param scope: The CDKTF construct scope (usually the stack instance)
    :param file_path: Path to IAM policy JSON file (absolute or relative to calling module)
    :type file_path: str
    :param user_name: Name of the IAM user to attach the policy to
    :type user_name: str
    :param policy_type: Type/purpose of the policy (e.g., "service-policy", "s3-access", "db-read")
    :type policy_type: str
    :param project_name: Project name for naming the policy
    :type project_name: str
    :param environment: Environment name (dev, staging, prod) for naming the policy
    :type environment: str
    :returns: IAM user policy resource
    :rtype: IamUserPolicy

    """
    policy = load_iam_policy_from_file(file_path)
    policy_name = f"{project_name}-{environment}-{policy_type}"
    
    return iam_user_policy.IamUserPolicy(
        scope,
        policy_name,
        name=policy_name,
        user=user_name,
        policy=policy,
    )
