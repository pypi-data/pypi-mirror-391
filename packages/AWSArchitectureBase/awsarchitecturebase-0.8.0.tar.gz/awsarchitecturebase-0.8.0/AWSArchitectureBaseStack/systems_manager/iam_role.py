"""
AWS Systems Manager IAM Role Configuration
===========================================

Functions for creating IAM roles for Systems Manager.
"""

from ..iam.service_roles import create_service_role


def create_ssm_maintenance_iam_role(
    scope,
    role_name: str,
    resource_id: str = "ssm_maintenance_role"
):
    """
    Create IAM role for Systems Manager maintenance windows.

    The role allows Systems Manager to execute tasks during maintenance windows.

    :param scope: The CDKTF construct scope (stack instance)
    :param role_name: Name for the IAM role
    :type role_name: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: Tuple of (IAM role, policy attachment)
    :rtype: tuple

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack.systems_manager import iam_role
        >>> 
        >>> role, policy = iam_role.create_ssm_maintenance_iam_role(
        ...     scope=self,
        ...     role_name="ssm-maintenance-role"
        ... )

    .. note::
       Attaches AWS managed policy: AmazonSSMMaintenanceWindowRole
       
       This policy grants permissions to:
       - Execute Run Command documents
       - Send SNS notifications
       - Access CloudWatch Logs
       - Execute automation documents
       
       Note: Includes both ssm.amazonaws.com and ec2.amazonaws.com in trust policy
       for EC2 instance access.
       
       Uses shared service_roles helper to eliminate code duplication.
    """
    return create_service_role(
        scope=scope,
        role_name=role_name,
        service_name="ssm",
        managed_policy_arns=["arn:aws:iam::aws:policy/service-role/AmazonSSMMaintenanceWindowRole"],
        resource_id=resource_id,
        description="IAM role for Systems Manager maintenance windows",
        additional_services=["ec2.amazonaws.com"]
    )
