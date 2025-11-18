"""
AWS Backup Vault Configuration
===============================

Functions for creating and managing backup vaults.
"""

from cdktf_cdktf_provider_aws.backup_vault import BackupVault
from cdktf_cdktf_provider_aws.backup_vault_lock_configuration import BackupVaultLockConfiguration


def create_backup_vault(
    scope,
    vault_name: str,
    resource_id: str = "backup_vault",
    kms_key_arn: str = None,
    enable_vault_lock: bool = False,
    min_retention_days: int = None,
    max_retention_days: int = None,
    changeable_for_days: int = None,
    tags: dict = None
):
    """
    Create an AWS Backup vault for storing backup data.

    A backup vault is a container that stores and organizes backups.

    :param scope: The CDKTF construct scope (stack instance)
    :param vault_name: Name for the backup vault
    :type vault_name: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param kms_key_arn: KMS key ARN for encryption (uses AWS managed key if None)
    :type kms_key_arn: str
    :param enable_vault_lock: Enable vault lock for compliance (WORM)
    :type enable_vault_lock: bool
    :param min_retention_days: Minimum retention period in days (vault lock)
    :type min_retention_days: int
    :param max_retention_days: Maximum retention period in days (vault lock)
    :type max_retention_days: int
    :param changeable_for_days: Days before vault lock becomes immutable
    :type changeable_for_days: int
    :param tags: Resource tags
    :type tags: dict
    :returns: Backup vault resource
    :rtype: BackupVault

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import backup
        >>> 
        >>> vault = backup.create_backup_vault(
        ...     scope=self,
        ...     vault_name="ftr-backup-vault",
        ...     tags={'Environment': 'production', 'Compliance': 'FTR'}
        ... )
        >>> 
        >>> # With vault lock for compliance (immutable backups)
        >>> vault = backup.create_backup_vault(
        ...     scope=self,
        ...     vault_name="ftr-compliance-vault",
        ...     enable_vault_lock=True,
        ...     min_retention_days=365,  # 1 year minimum
        ...     changeable_for_days=3     # 3 day grace period
        ... )

    .. note::
       **Vault Lock (WORM)**: When enabled, prevents backup deletion before
       min_retention_days expires. Use for regulatory compliance.
       
       **Cost**: Vault itself is free, you pay for backup storage (~$0.05/GB/month)
    """
    vault = BackupVault(
        scope,
        resource_id,
        name=vault_name,
        kms_key_arn=kms_key_arn,
        tags=tags
    )

    # Enable vault lock if requested (for compliance/immutability)
    if enable_vault_lock:
        BackupVaultLockConfiguration(
            scope,
            f"{resource_id}_lock",
            backup_vault_name=vault.name,
            min_retention_days=min_retention_days,
            max_retention_days=max_retention_days,
            changeable_for_days=changeable_for_days
        )

    return vault
