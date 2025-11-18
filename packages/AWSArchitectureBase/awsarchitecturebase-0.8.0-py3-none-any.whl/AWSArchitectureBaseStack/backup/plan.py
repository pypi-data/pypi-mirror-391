"""
AWS Backup Plan Configuration
==============================

Functions for creating backup plans and resource selections.
"""

from cdktf_cdktf_provider_aws.backup_plan import (
    BackupPlan,
    BackupPlanRule,
    BackupPlanRuleLifecycle
)
from cdktf_cdktf_provider_aws.backup_selection import (
    BackupSelection,
    BackupSelectionSelectionTag
)


def create_backup_plan(
    scope,
    plan_name: str,
    vault_name: str,
    resource_id: str = "backup_plan",
    schedule: str = "cron(0 5 ? * * *)",
    start_window_minutes: int = 60,
    completion_window_minutes: int = 120,
    delete_after_days: int = 35,
    move_to_cold_storage_after_days: int = None,
    enable_continuous_backup: bool = False,
    tags: dict = None
):
    """
    Create an AWS Backup plan with scheduling and lifecycle rules.

    A backup plan defines when and how to backup resources.

    :param scope: The CDKTF construct scope (stack instance)
    :param plan_name: Name for the backup plan
    :type plan_name: str
    :param vault_name: Target backup vault name
    :type vault_name: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param schedule: Backup schedule in cron format (default: daily at 5am UTC)
    :type schedule: str
    :param start_window_minutes: Backup must start within this window (default: 60)
    :type start_window_minutes: int
    :param completion_window_minutes: Backup must complete within this window (default: 120)
    :type completion_window_minutes: int
    :param delete_after_days: Delete backups after this many days (default: 35)
    :type delete_after_days: int
    :param move_to_cold_storage_after_days: Move to cold storage after days (optional)
    :type move_to_cold_storage_after_days: int
    :param enable_continuous_backup: Enable point-in-time recovery (supported resources only)
    :type enable_continuous_backup: bool
    :param tags: Resource tags
    :type tags: dict
    :returns: Backup plan resource
    :rtype: BackupPlan

    **Common Schedule Patterns:**
    
    - Daily: `cron(0 5 ? * * *)` - 5am UTC daily
    - Hourly: `cron(0 * ? * * *)` - Every hour
    - Weekly: `cron(0 5 ? * 1 *)` - 5am UTC every Monday
    - Monthly: `cron(0 5 1 * ? *)` - 5am UTC first day of month

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import backup
        >>> 
        >>> # Daily backup with 35-day retention
        >>> plan = backup.create_backup_plan(
        ...     scope=self,
        ...     plan_name="ftr-daily-backup",
        ...     vault_name="ftr-backup-vault",
        ...     schedule="cron(0 5 ? * * *)",  # 5am UTC daily
        ...     delete_after_days=35
        ... )
        >>> 
        >>> # Backup with cold storage transition
        >>> plan = backup.create_backup_plan(
        ...     scope=self,
        ...     plan_name="ftr-long-term-backup",
        ...     vault_name="ftr-backup-vault",
        ...     delete_after_days=365,
        ...     move_to_cold_storage_after_days=90  # Cold storage after 3 months
        ... )

    .. note::
       **Cold Storage**: Cheaper storage tier (~$0.01/GB/month vs $0.05/GB/month)
       but backups must be stored for at least 90 days in cold storage.
       
       **Continuous Backup**: Point-in-time recovery (5-minute intervals) for
       supported services (RDS, DynamoDB, etc.). Additional cost applies.
    """
    lifecycle = None
    if delete_after_days or move_to_cold_storage_after_days:
        lifecycle = BackupPlanRuleLifecycle(
            delete_after=delete_after_days,
            cold_storage_after=move_to_cold_storage_after_days
        )

    rule = BackupPlanRule(
        rule_name=f"{plan_name}-rule",
        target_vault_name=vault_name,
        schedule=schedule,
        start_window=start_window_minutes,
        completion_window=completion_window_minutes,
        lifecycle=lifecycle,
        enable_continuous_backup=enable_continuous_backup
    )

    plan = BackupPlan(
        scope,
        resource_id,
        name=plan_name,
        rule=[rule],
        tags=tags
    )

    return plan


def create_backup_selection(
    scope,
    selection_name: str,
    plan_id: str,
    iam_role_arn: str,
    resource_id: str = "backup_selection",
    resources: list = None,
    selection_tags: list = None,
    not_resources: list = None
):
    """
    Create a backup selection to specify which resources to backup.

    Backup selections define which resources the backup plan applies to.

    :param scope: The CDKTF construct scope (stack instance)
    :param selection_name: Name for the backup selection
    :type selection_name: str
    :param plan_id: Backup plan ID
    :type plan_id: str
    :param iam_role_arn: IAM role ARN for AWS Backup
    :type iam_role_arn: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param resources: List of resource ARNs to backup (specific resources)
    :type resources: list
    :param selection_tags: List of tag-based selections (backup resources with tags)
    :type selection_tags: list of dict [{'type': 'STRINGEQUALS', 'key': 'Backup', 'value': 'true'}]
    :param not_resources: List of resource ARNs to exclude from backup
    :type not_resources: list
    :returns: Backup selection resource
    :rtype: BackupSelection

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import backup
        >>> 
        >>> # Backup all resources tagged with Backup=true
        >>> selection = backup.create_backup_selection(
        ...     scope=self,
        ...     selection_name="ftr-tagged-resources",
        ...     plan_id=plan.id,
        ...     iam_role_arn=role.arn,
        ...     selection_tags=[
        ...         {'type': 'STRINGEQUALS', 'key': 'Backup', 'value': 'true'}
        ...     ]
        ... )
        >>> 
        >>> # Backup specific resources by ARN
        >>> selection = backup.create_backup_selection(
        ...     scope=self,
        ...     selection_name="ftr-critical-resources",
        ...     plan_id=plan.id,
        ...     iam_role_arn=role.arn,
        ...     resources=[
        ...         'arn:aws:rds:us-east-1:123456789012:db:production-db',
        ...         'arn:aws:dynamodb:us-east-1:123456789012:table/Users'
        ...     ]
        ... )

    .. note::
       **Selection Priority**: Tag-based selections are more flexible than
       ARN-based. Use tags to automatically backup new resources.
       
       **Supported Resources**: EC2, EBS, RDS, DynamoDB, EFS, FSx, Storage Gateway,
       Aurora, DocumentDB, Neptune, S3, and more.
    """
    # Convert selection_tags dict to BackupSelectionSelectionTag objects
    tag_objects = None
    if selection_tags:
        tag_objects = [
            BackupSelectionSelectionTag(
                type=tag.get('type', 'STRINGEQUALS'),
                key=tag['key'],
                value=tag['value']
            )
            for tag in selection_tags
        ]

    selection = BackupSelection(
        scope,
        resource_id,
        name=selection_name,
        plan_id=plan_id,
        iam_role_arn=iam_role_arn,
        resources=resources,
        selection_tag=tag_objects,
        not_resources=not_resources
    )

    return selection
