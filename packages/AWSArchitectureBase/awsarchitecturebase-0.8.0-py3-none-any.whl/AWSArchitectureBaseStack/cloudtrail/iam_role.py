"""
AWS CloudTrail IAM Role Configuration
======================================

Functions for creating IAM roles for CloudTrail CloudWatch Logs integration.
"""

from ..iam.service_roles import create_service_role


def create_cloudtrail_iam_role(
    scope,
    role_name: str,
    resource_id: str = "cloudtrail_iam_role"
):
    """
    Create IAM role for CloudTrail CloudWatch Logs integration.

    The role allows CloudTrail to send logs to CloudWatch Logs.

    :param scope: The CDKTF construct scope (stack instance)
    :param role_name: Name for the IAM role
    :type role_name: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: Tuple of (IAM role, policy attachment)
    :rtype: tuple

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack.cloudtrail import iam_role
        >>> 
        >>> role, policy = iam_role.create_cloudtrail_iam_role(
        ...     scope=self,
        ...     role_name="cloudtrail-cloudwatch-role"
        ... )

    .. note::
       This role is only needed if integrating CloudTrail with CloudWatch Logs
       for real-time monitoring and alerting.
       
       Attaches AWS managed policy: AWSCloudTrailRole (custom inline policy in practice)
       
       Uses shared service_roles helper to eliminate code duplication.
    """
    # Note: CloudTrail typically uses an inline policy for CloudWatch Logs
    # For simplicity, we use the managed policy pattern
    return create_service_role(
        scope=scope,
        role_name=role_name,
        service_name="cloudtrail",
        managed_policy_arns=[
            "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"  # Note: In production, use a more restrictive custom policy
        ],
        resource_id=resource_id,
        description="IAM role for CloudTrail CloudWatch Logs integration"
    )
