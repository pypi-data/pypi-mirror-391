"""
FTR Compliance Orchestration
============================

Central orchestration for FTR compliance services.
This module handles the setup and configuration of all compliance-related AWS services.
"""

from cdktf_cdktf_provider_aws.data_aws_caller_identity import DataAwsCallerIdentity
from . import security_hub, config, backup, inspector, systems_manager, cloudtrail, notifications, guardduty, access_analyzer, s3, iam


def setup_ftr_compliance(stack, flags: list):
    """
    Setup FTR compliance services based on architecture flags.
    
    This orchestrator checks flags and enables the corresponding AWS compliance
    services. All services are opt-in via architecture flags.
    
    :param stack: The AWSArchitectureBase stack instance
    :param flags: List of architecture flag values (e.g., ['enable_security_hub', 'enable_config'])
    :returns: Dictionary with enabled compliance resources
    :rtype: dict
    
    Example:
        >>> from .ArchitectureFlags import ArchitectureFlags
        >>> resources = setup_ftr_compliance(
        ...     stack=self,
        ...     flags=[ArchitectureFlags.ENABLE_SECURITY_HUB.value]
        ... )
    """
    
    resources = {}
    
    # Check if all FTR compliance should be enabled
    enable_all = 'enable_all_ftr_compliance' in flags
    
    # ========================================================================
    # STEP 1: Create shared access logs bucket
    # ========================================================================
   
    # Get AWS account ID
    caller_identity = DataAwsCallerIdentity(stack, "caller_identity")
    account_id = caller_identity.account_id
    
    # Create shared access logs bucket (used by all compliance buckets for logging)
    if enable_all or any(f in flags for f in ['enable_config', 'enable_cloudtrail', 'enable_backup']):
        logs_bucket = s3.create_bucket(
            scope=stack,
            bucket_name=f"{stack.project_name}-access-logs-{stack.region}",
            block_public_access=True,
            enable_versioning=True,
            enable_encryption=True,
            lifecycle_rules=[
                s3.create_lifecycle_rule(
                    rule_id="access-logs-cleanup",
                    retention_days=90,
                    noncurrent_retention_days=30
                )
            ],
            tags={
                "Purpose": "S3AccessLogs",
                "Project": stack.project_name,
                "Environment": stack.environment
            },
            resource_id="access_logs_bucket"
        )
        resources['logs_bucket'] = logs_bucket
        logging_bucket_name = logs_bucket['bucket'].bucket
    else:
        logging_bucket_name = None
    
    # Security Hub
    if enable_all or 'enable_security_hub' in flags:
        resources['security_hub'] = _setup_security_hub(stack)
    
    # ========================================================================
    # STEP 2-7: Create compliance services (each creates its own S3 bucket internally)
    # ========================================================================
    
    # AWS Config (creates its own config bucket internally)
    if enable_all or 'enable_config' in flags:
        resources['config'] = _setup_config(stack, account_id, logging_bucket_name)
    
    # AWS Backup (creates its own backup bucket internally)
    if enable_all or 'enable_backup' in flags:
        resources['backup'] = _setup_backup(stack, account_id, logging_bucket_name)
    
    # AWS Inspector
    if enable_all or 'enable_inspector' in flags:
        resources['inspector'] = _setup_inspector(stack)
    
    # AWS Systems Manager
    if enable_all or 'enable_systems_manager' in flags:
        resources['systems_manager'] = _setup_systems_manager(stack)
    
    # AWS CloudTrail (creates its own cloudtrail bucket internally)
    if enable_all or 'enable_cloudtrail' in flags:
        resources['cloudtrail'] = _setup_cloudtrail(stack, account_id, logging_bucket_name)
    
    # AWS GuardDuty
    if enable_all or 'enable_guardduty' in flags:
        resources['guardduty'] = _setup_guardduty(stack)
    
    # AWS IAM Access Analyzer (CIS v3.0.0 Control 1.20)
    if enable_all or 'enable_access_analyzer' in flags:
        resources['access_analyzer'] = _setup_access_analyzer(stack)
    
    # AWS Support IAM Role (CIS v3.0.0 Control IAM.18)
    # Note: Always enabled because it's free and required for CIS compliance
    # No flag needed - this is a basic security requirement
    resources['aws_support_role'] = _setup_aws_support_role(stack)
    
    # AWS SNS/SES Notifications
    if enable_all or 'enable_notifications' in flags:
        resources['notifications'] = _setup_notifications(stack)
    
    return resources


def _setup_security_hub(stack):
    """Setup AWS Security Hub with configured standards."""
    config = stack.ftr_compliance_config.get('security_hub', {})
    
    return security_hub.create_security_hub_resources(
        scope=stack,
        region=stack.region,
        enable_standards=config.get('enable_standards', False),
        auto_enable_controls=config.get('auto_enable_controls', False),
        standards=config.get('standards', None)
    )


def _setup_config(stack, account_id, logging_bucket):
    """Setup AWS Config with configuration recorder and compliance rules."""
    cfg = stack.ftr_compliance_config.get('config', {})
    
    return config.create_config_resources(
        scope=stack,
        region=stack.region,
        account_id=account_id,
        project_name=stack.project_name,
        environment=stack.environment,
        logging_bucket=logging_bucket,
        create_bucket=True,  # Config creates its own bucket
        s3_bucket_name=cfg.get('s3_bucket_name', None),  # Optional: custom bucket name
        recorder_name=cfg.get('recorder_name', 'default'),
        channel_name=cfg.get('channel_name', 'default'),
        enable_recorder=cfg.get('enable_recorder', False),
        enable_rules=cfg.get('enable_rules', False),
        config_rules=cfg.get('rules', None),
        s3_key_prefix=cfg.get('s3_key_prefix', 'config'),
        sns_topic_arn=cfg.get('sns_topic_arn', None)
    )


def _setup_backup(stack, account_id, logging_bucket):
    """Setup AWS Backup with vault, plan, and optional resource selection."""
    cfg = stack.ftr_compliance_config.get('backup', {})
    
    return backup.create_backup_resources(
        scope=stack,
        region=stack.region,
        project_name=stack.project_name,
        account_id=account_id,
        environment=stack.environment,
        logging_bucket=logging_bucket,
        create_bucket=True,  # Backup creates its own bucket
        s3_bucket_name=cfg.get('s3_bucket_name', None),  # Optional: custom bucket name
        vault_name=cfg.get('vault_name', None),
        plan_name=cfg.get('plan_name', None),
        role_name=cfg.get('role_name', None),
        enable_backup=cfg.get('enable_backup', False),
        schedule=cfg.get('schedule', 'cron(0 5 ? * * *)'),
        retention_days=cfg.get('retention_days', 35),
        cold_storage_after_days=cfg.get('cold_storage_after_days', None),
        enable_continuous_backup=cfg.get('enable_continuous_backup', False),
        selection_tags=cfg.get('selection_tags', None),
        resources_to_backup=cfg.get('resources', None),
        enable_vault_lock=cfg.get('enable_vault_lock', False),
        min_retention_days=cfg.get('min_retention_days', None),
        tags=cfg.get('tags', None)
    )


def _setup_inspector(stack):
    """Setup AWS Inspector with automated vulnerability scanning."""
    cfg = stack.ftr_compliance_config.get('inspector', {})
    
    # Get current AWS account ID
    caller_identity = DataAwsCallerIdentity(stack, "caller_identity_inspector")
    
    return inspector.create_inspector_resources(
        scope=stack,
        account_id=caller_identity.account_id,
        enable_scanning=cfg.get('enable_scanning', False),
        enable_ec2=cfg.get('enable_ec2', False),
        enable_ecr=cfg.get('enable_ecr', False),
        enable_lambda=cfg.get('enable_lambda', False),
        enable_lambda_code=cfg.get('enable_lambda_code', False)
    )


def _setup_systems_manager(stack):
    """Setup AWS Systems Manager with patch management and maintenance windows."""
    cfg = stack.ftr_compliance_config.get('systems_manager', {})
    
    return systems_manager.create_systems_manager_resources(
        scope=stack,
        project_name=stack.project_name,
        enable_patching=cfg.get('enable_patching', False),
        operating_system=cfg.get('operating_system', 'AMAZON_LINUX_2'),
        patch_baseline_name=cfg.get('patch_baseline_name', None),
        patch_group_name=cfg.get('patch_group_name', None),
        maintenance_window_name=cfg.get('maintenance_window_name', None),
        maintenance_schedule=cfg.get('maintenance_schedule', 'cron(0 2 ? * SUN *)'),
        maintenance_duration=cfg.get('maintenance_duration', 3),
        maintenance_cutoff=cfg.get('maintenance_cutoff', 1),
        role_name=cfg.get('role_name', None),
        approval_rules=cfg.get('approval_rules', None),
        patch_targets=cfg.get('patch_targets', None),
        tags=cfg.get('tags', None)
    )


def _setup_cloudtrail(stack, account_id, logging_bucket):
    """Setup AWS CloudTrail with audit logging and compliance tracking (CIS Controls 3.1-3.7)."""
    cfg = stack.ftr_compliance_config.get('cloudtrail', {})
    
    return cloudtrail.create_cloudtrail_resources(
        scope=stack,
        trail_name=cfg.get('trail_name', f"{stack.project_name}-audit-trail"),
        account_id=account_id,
        project_name=stack.project_name,
        environment=stack.environment,
        region=stack.region,
        logging_bucket=logging_bucket,
        create_bucket=True,  # CloudTrail creates its own bucket
        s3_bucket_name=cfg.get('s3_bucket_name', None),  # Optional: custom bucket name
        enable_logging=cfg.get('enable_logging', False),
        enable_cloudwatch_logs=cfg.get('enable_cloudwatch_logs', False),
        cloudwatch_logs_group_arn=cfg.get('cloudwatch_logs_group_arn', None),
        is_multi_region_trail=cfg.get('is_multi_region_trail', True),
        enable_log_file_validation=cfg.get('enable_log_file_validation', True),
        kms_key_id=cfg.get('kms_key_id', None),
        create_kms_key=cfg.get('create_kms_key', False),  # CIS Control 3.7: KMS encryption
        s3_key_prefix=cfg.get('s3_key_prefix', 'cloudtrail'),
        enable_data_events=cfg.get('enable_data_events', False),
        data_event_selectors=cfg.get('data_event_selectors', None),
        tags=cfg.get('tags', None)
    )


def _setup_notifications(stack):
    """Setup AWS SNS/SES Notifications for compliance alerts."""
    cfg = stack.ftr_compliance_config.get('notifications', {})
    
    return notifications.create_notification_resources(
        scope=stack,
        topic_name=cfg.get('topic_name', f"{stack.project_name}-compliance-alerts"),
        enable_notifications=cfg.get('enable_notifications', False),
        display_name=cfg.get('display_name', None),
        enable_encryption=cfg.get('enable_encryption', True),
        kms_master_key_id=cfg.get('kms_master_key_id', None),
        email_subscriptions=cfg.get('email_subscriptions', None),
        sms_subscriptions=cfg.get('sms_subscriptions', None),
        lambda_subscriptions=cfg.get('lambda_subscriptions', None),
        allowed_services=cfg.get('allowed_services', None),
        tags=cfg.get('tags', None)
    )


def _setup_guardduty(stack):
    """Setup AWS GuardDuty for threat detection."""
    cfg = stack.ftr_compliance_config.get('guardduty', {})
    
    return guardduty.create_guardduty_detector(
        scope=stack,
        enable=cfg.get('enable_guardduty', False),
        finding_publishing_frequency=cfg.get('finding_publishing_frequency', 'FIFTEEN_MINUTES'),
        resource_id="guardduty_detector"
    )


def _setup_access_analyzer(stack):
    """Setup AWS IAM Access Analyzer (CIS v3.0.0 Control 1.20)."""
    cfg = stack.ftr_compliance_config.get('access_analyzer', {})
    
    return access_analyzer.create_access_analyzer(
        scope=stack,
        analyzer_name=cfg.get('analyzer_name', f"{stack.project_name}-access-analyzer"),
        analyzer_type=cfg.get('analyzer_type', 'ACCOUNT'),
        resource_id="access_analyzer"
    )


def _setup_aws_support_role(stack):
    """
    Setup AWS Support IAM role (CIS v3.0.0 Control IAM.18).
    
    This role is required for CIS compliance and is free to create.
    It allows designated users to manage AWS Support cases and tickets.
    """
    cfg = stack.ftr_compliance_config.get('aws_support_role', {})
    
    role, policy = iam.create_aws_support_role(
        scope=stack,
        role_name=cfg.get('role_name', 'aws-support-access'),
        resource_id="aws_support_role"
    )
    
    return {
        'role': role,
        'policy_attachment': policy
    }

