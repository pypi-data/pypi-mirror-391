"""
AWS Backup Resources Orchestration
===================================

High-level functions for creating complete AWS Backup setup.
"""

from . import vault, plan, iam_role, s3_bucket


def create_backup_resources(
    scope,
    region: str,
    project_name: str,
    account_id: str = None,
    environment: str = None,
    s3_bucket_name: str = None,
    logging_bucket: str = None,
    create_bucket: bool = True,
    vault_name: str = None,
    plan_name: str = None,
    role_name: str = None,
    enable_backup: bool = False,
    schedule: str = "cron(0 5 ? * * *)",
    retention_days: int = 35,
    cold_storage_after_days: int = None,
    enable_continuous_backup: bool = False,
    selection_tags: list = None,
    resources_to_backup: list = None,
    enable_vault_lock: bool = False,
    min_retention_days: int = None,
    tags: dict = None
):
    """
    Create complete AWS Backup infrastructure with vault, plan, and selection.

    This orchestration function sets up:
    - Backup vault for storing backups
    - IAM role for Backup service
    - Backup plan with schedule and lifecycle
    - Optional: Resource selection (tag-based or ARN-based)

    :param scope: The CDKTF construct scope (stack instance)
    :param region: AWS region
    :type region: str
    :param project_name: Project name for resource naming
    :type project_name: str
    :param vault_name: Backup vault name (default: "{project_name}-backup-vault")
    :type vault_name: str
    :param plan_name: Backup plan name (default: "{project_name}-backup-plan")
    :type plan_name: str
    :param role_name: IAM role name (default: "{project_name}-backup-role")
    :type role_name: str
    :param enable_backup: Create backup selection to start backing up (default: False)
    :type enable_backup: bool
    :param schedule: Backup schedule in cron format (default: daily at 5am UTC)
    :type schedule: str
    :param retention_days: Delete backups after this many days (default: 35)
    :type retention_days: int
    :param cold_storage_after_days: Move to cold storage after days (optional)
    :type cold_storage_after_days: int
    :param enable_continuous_backup: Enable point-in-time recovery (default: False)
    :type enable_continuous_backup: bool
    :param selection_tags: Tag-based selection (default: [{'type': 'STRINGEQUALS', 'key': 'Backup', 'value': 'true'}])
    :type selection_tags: list of dict
    :param resources_to_backup: Specific resource ARNs to backup (optional)
    :type resources_to_backup: list
    :param enable_vault_lock: Enable vault lock for compliance (default: False)
    :type enable_vault_lock: bool
    :param min_retention_days: Minimum retention for vault lock (required if vault_lock enabled)
    :type min_retention_days: int
    :param tags: Resource tags
    :type tags: dict
    :returns: Dictionary with created resources
    :rtype: dict

    **Resource Dictionary Keys:**
    
    - `vault`: Backup vault
    - `iam_role`: IAM role for Backup service
    - `iam_policy`: IAM backup policy attachment
    - `iam_restore_policy`: IAM restore policy attachment
    - `plan`: Backup plan
    - `selection`: Backup selection (if enable_backup=True)

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import backup
        >>> 
        >>> # Infrastructure only (safe for testing)
        >>> resources = backup.create_backup_resources(
        ...     scope=self,
        ...     region="us-east-1",
        ...     project_name="my-app"
        ... )
        >>> 
        >>> # Active backup with tag-based selection
        >>> resources = backup.create_backup_resources(
        ...     scope=self,
        ...     region="us-east-1",
        ...     project_name="my-app",
        ...     enable_backup=True,
        ...     selection_tags=[
        ...         {'type': 'STRINGEQUALS', 'key': 'Backup', 'value': 'true'}
        ...     ],
        ...     retention_days=90,
        ...     cold_storage_after_days=30
        ... )
        >>> 
        >>> # Compliance backup with vault lock
        >>> resources = backup.create_backup_resources(
        ...     scope=self,
        ...     region="us-east-1",
        ...     project_name="ftr-app",
        ...     enable_backup=True,
        ...     enable_vault_lock=True,
        ...     min_retention_days=365,  # 1 year minimum
        ...     retention_days=2555      # 7 years
        ... )

    .. note::
       **Cost Estimates:**
       
       - Infrastructure only: $0.00/month (vault and plan have no cost)
       - Active backup: ~$0.05/GB/month (standard) or ~$0.01/GB/month (cold storage)
       - Continuous backup: Additional ~$0.20/GB/month (supported resources only)
       
       **Safe Defaults:**
       
       - enable_backup=False: Creates infrastructure but doesn't start backing up
       - Default tags: Resources must be tagged with Backup=true to be backed up
       
       **To Enable Backup:**
       
       1. Set enable_backup=True
       2. Tag resources with Backup=true (or specify resources_to_backup ARNs)
       3. Backups will run on the specified schedule
    """
    resources_dict = {}

    # Step 1: Create Backup's S3 bucket (if requested)
    if create_bucket:
        if not all([account_id, environment]):
            raise ValueError("When create_bucket=True, account_id and environment are required")
        
        if not s3_bucket_name:
            s3_bucket_name = f"{project_name}-backup-{region}"
        
        bucket_resources = s3_bucket.create_backup_s3_bucket(
            scope=scope,
            bucket_name=s3_bucket_name,
            account_id=account_id,
            project_name=project_name,
            environment=environment,
            logging_bucket=logging_bucket,
            resource_id="backup_bucket"
        )
        resources_dict['s3_bucket'] = bucket_resources['bucket']
        resources_dict['s3_public_access_block'] = bucket_resources['public_access_block']
        resources_dict['s3_bucket_policy'] = bucket_resources['bucket_policy']
        resources_dict['s3_lifecycle'] = bucket_resources.get('lifecycle')
        resources_dict['s3_logging'] = bucket_resources.get('logging')

    # Step 2: Set default names
    if not vault_name:
        vault_name = f"{project_name}-backup-vault"
    if not plan_name:
        plan_name = f"{project_name}-backup-plan"
    if not role_name:
        role_name = f"{project_name}-backup-role"

    # Merge tags
    resource_tags = tags or {}
    if 'Project' not in resource_tags:
        resource_tags['Project'] = project_name
    if 'ManagedBy' not in resource_tags:
        resource_tags['ManagedBy'] = 'AWS Backup'

    # Step 3: Create backup vault
    backup_vault = vault.create_backup_vault(
        scope=scope,
        vault_name=vault_name,
        enable_vault_lock=enable_vault_lock,
        min_retention_days=min_retention_days if enable_vault_lock else None,
        tags=resource_tags
    )
    resources_dict['vault'] = backup_vault

    # Create IAM role for Backup
    backup_role, policy_attach, restore_attach = iam_role.create_backup_iam_role(
        scope=scope,
        role_name=role_name
    )
    resources_dict['iam_role'] = backup_role
    resources_dict['iam_policy'] = policy_attach
    resources_dict['iam_restore_policy'] = restore_attach

    # Create backup plan
    backup_plan = plan.create_backup_plan(
        scope=scope,
        plan_name=plan_name,
        vault_name=backup_vault.name,
        schedule=schedule,
        delete_after_days=retention_days,
        move_to_cold_storage_after_days=cold_storage_after_days,
        enable_continuous_backup=enable_continuous_backup,
        tags=resource_tags
    )
    resources_dict['plan'] = backup_plan

    # Create backup selection if enabled
    if enable_backup:
        # Default to tag-based selection if not specified
        if not selection_tags and not resources_to_backup:
            selection_tags = [
                {'type': 'STRINGEQUALS', 'key': 'Backup', 'value': 'true'}
            ]

        backup_selection = plan.create_backup_selection(
            scope=scope,
            selection_name=f"{plan_name}-selection",
            plan_id=backup_plan.id,
            iam_role_arn=backup_role.arn,
            resources=resources_to_backup,
            selection_tags=selection_tags
        )
        resources_dict['selection'] = backup_selection

    return resources_dict
