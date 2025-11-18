"""
AWS Backup IAM Role Configuration
==================================

Functions for creating IAM roles and policies for AWS Backup.
"""

from ..iam.service_roles import create_service_role


def create_backup_iam_role(
    scope,
    role_name: str,
    resource_id: str = "backup_iam_role"
):
    """
    Create IAM role for AWS Backup service.

    The role allows AWS Backup to create backups of your resources.

    :param scope: The CDKTF construct scope (stack instance)
    :param role_name: Name for the IAM role
    :type role_name: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: Tuple of (IAM role, backup policy attachment, restore policy attachment)
    :rtype: tuple

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack.backup import iam_role
        >>> 
        >>> role, backup_policy, restore_policy = iam_role.create_backup_iam_role(
        ...     scope=self,
        ...     role_name="backup-service-role"
        ... )

    .. note::
       Attaches two AWS managed policies:
       - AWSBackupServiceRolePolicyForBackup (create backups)
       - AWSBackupServiceRolePolicyForRestores (restore backups)
       
       This grants permissions to:
       - Create snapshots of EBS volumes
       - Create RDS snapshots
       - Create DynamoDB backups
       - Access EFS, FSx, Storage Gateway
       - Tag resources for backup tracking
       - Restore resources from backups
       
       Uses shared service_roles helper to eliminate code duplication.
    """
    return create_service_role(
        scope=scope,
        role_name=role_name,
        service_name="backup",
        managed_policy_arns=[
            "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup",
            "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
        ],
        resource_id=resource_id,
        description="IAM role for AWS Backup service"
    )
