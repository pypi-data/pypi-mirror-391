"""
IAM Service Roles Helper
=========================

Shared functions for creating AWS service IAM roles.

This module provides reusable functions to eliminate code duplication
across FTR compliance services that need IAM roles.
"""

from cdktf_cdktf_provider_aws.iam_role import IamRole
from cdktf_cdktf_provider_aws.iam_role_policy_attachment import IamRolePolicyAttachment
import json


def create_service_role(
    scope,
    role_name: str,
    service_name: str,
    managed_policy_arns: list,
    resource_id: str,
    description: str = None,
    additional_services: list = None
):
    """
    Create an IAM role for an AWS service with managed policy attachments.

    This is a generic helper to reduce code duplication across service modules.
    Each service (Config, Backup, SSM, etc.) uses this to create their roles.

    :param scope: The CDKTF construct scope (stack instance)
    :param role_name: Name for the IAM role
    :type role_name: str
    :param service_name: AWS service name (e.g., 'config', 'backup', 'ssm')
    :type service_name: str
    :param managed_policy_arns: List of AWS managed policy ARNs to attach
    :type managed_policy_arns: list
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param description: Role description (default: "IAM role for {service_name} service")
    :type description: str
    :param additional_services: Additional service principals for trust policy
    :type additional_services: list
    :returns: Tuple of (IAM role, *policy attachments)
    :rtype: tuple

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack.iam import service_roles
        >>> 
        >>> # Create role for AWS Config
        >>> role, policy = service_roles.create_service_role(
        ...     scope=self,
        ...     role_name="config-service-role",
        ...     service_name="config",
        ...     managed_policy_arns=["arn:aws:iam::aws:policy/service-role/ConfigRole"],
        ...     resource_id="config_iam_role"
        ... )
        >>> 
        >>> # Create role with multiple policies
        >>> role, policy1, policy2 = service_roles.create_service_role(
        ...     scope=self,
        ...     role_name="backup-service-role",
        ...     service_name="backup",
        ...     managed_policy_arns=[
        ...         "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup",
        ...         "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
        ...     ],
        ...     resource_id="backup_iam_role"
        ... )
        >>> 
        >>> # Create role with multiple service principals
        >>> role, policy = service_roles.create_service_role(
        ...     scope=self,
        ...     role_name="ssm-maintenance-role",
        ...     service_name="ssm",
        ...     managed_policy_arns=["arn:aws:iam::aws:policy/service-role/AmazonSSMMaintenanceWindowRole"],
        ...     resource_id="ssm_iam_role",
        ...     additional_services=["ec2.amazonaws.com"]
        ... )

    .. note::
       This helper follows the DRY (Don't Repeat Yourself) principle.
       All FTR compliance service modules use this instead of duplicating code.
       
       **Service Names**: Use short form without '.amazonaws.com' suffix
       - Config: 'config'
       - Backup: 'backup'
       - Systems Manager: 'ssm'
       - CloudTrail: 'cloudtrail'
       
       **Multiple Policies**: Returns tuple of (role, *attachments)
       - 1 policy: (role, attachment)
       - 2 policies: (role, attachment1, attachment2)
       - N policies: (role, attachment1, ..., attachmentN)
    """
    # Build trust policy with service principals
    services = [f"{service_name}.amazonaws.com"]
    if additional_services:
        services.extend(additional_services)

    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": services
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    # Create IAM role
    role = IamRole(
        scope,
        resource_id,
        name=role_name,
        assume_role_policy=json.dumps(assume_role_policy),
        description=description or f"IAM role for {service_name} service"
    )

    # Attach managed policies
    policy_attachments = []
    for idx, policy_arn in enumerate(managed_policy_arns):
        attachment = IamRolePolicyAttachment(
            scope,
            f"{resource_id}_policy_{idx}",
            role=role.name,
            policy_arn=policy_arn
        )
        policy_attachments.append(attachment)

    # Return role and all policy attachments
    return (role, *policy_attachments)
