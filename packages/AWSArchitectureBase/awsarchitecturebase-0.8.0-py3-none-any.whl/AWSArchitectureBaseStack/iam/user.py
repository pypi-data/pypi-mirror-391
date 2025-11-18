"""
IAM User management utilities.

This module provides functions for creating and managing AWS IAM users,
access keys, and related resources.
"""

from cdktf_cdktf_provider_aws import iam_user, iam_access_key
from typing import Tuple


def create_iam_user_with_key(
    scope,
    user_name: str,
    resource_id: str
) -> Tuple[iam_user.IamUser, iam_access_key.IamAccessKey]:
    """
    Create an IAM user with an access key.

    Creates both an IAM user and generates programmatic access credentials
    (access key and secret key) for the user.

    :param scope: The CDKTF construct scope (usually the stack instance)
    :param user_name: Name of the IAM user to create
    :type user_name: str
    :param resource_id: Unique resource identifier for CDKTF constructs
    :type resource_id: str
    :returns: Tuple of (IamUser, IamAccessKey)
    :rtype: tuple[iam_user.IamUser, iam_access_key.IamAccessKey]

    """
    iam_user_resource = iam_user.IamUser(
        scope,
        resource_id + "_user",
        name=user_name
    )
    
    iam_access_key_resource = iam_access_key.IamAccessKey(
        scope,
        resource_id + "_access_key",
        user=iam_user_resource.name
    )
    
    return iam_user_resource, iam_access_key_resource
