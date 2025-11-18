"""
AWS Config IAM Role Configuration
==================================

Functions for creating IAM roles and policies for AWS Config.
"""

from ..iam.service_roles import create_service_role


def create_config_iam_role(
    scope,
    role_name: str,
    resource_id: str = "config_iam_role"
):
    """
    Create IAM role for AWS Config service.

    The role allows Config to access resources and write to S3.

    :param scope: The CDKTF construct scope (stack instance)
    :param role_name: Name for the IAM role
    :type role_name: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: Tuple of (IAM role, policy attachment)
    :rtype: tuple

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack.config import iam_role
        >>> 
        >>> role, policy = iam_role.create_config_iam_role(
        ...     scope=self,
        ...     role_name="config-service-role"
        ... )

    .. note::
       Attaches AWS managed policy: AWS_ConfigRole
    """
    return create_service_role(
        scope=scope,
        role_name=role_name,
        service_name="config",
        managed_policy_arns=["arn:aws:iam::aws:policy/service-role/AWS_ConfigRole"],
        resource_id=resource_id,
        description="IAM role for AWS Config service"
    )
