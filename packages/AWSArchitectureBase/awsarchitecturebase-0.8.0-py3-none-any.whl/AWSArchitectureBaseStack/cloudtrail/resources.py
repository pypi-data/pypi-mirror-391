"""
AWS CloudTrail Resources Orchestrator
======================================

Orchestrates the creation of CloudTrail resources.
"""

from .trail import create_cloudtrail
from .iam_role import create_cloudtrail_iam_role
from . import s3_bucket
from .. import kms


def create_cloudtrail_resources(
    scope,
    trail_name: str,
    s3_bucket_name: str = None,
    account_id: str = None,
    project_name: str = None,
    environment: str = None,
    region: str = None,
    logging_bucket: str = None,
    create_bucket: bool = True,
    enable_logging: bool = False,  # Safe default: disabled
    enable_cloudwatch_logs: bool = False,
    cloudwatch_logs_group_arn: str = None,
    is_multi_region_trail: bool = True,
    enable_log_file_validation: bool = True,
    kms_key_id: str = None,
    create_kms_key: bool = False,  # CIS Control 3.7: Create KMS key for log encryption
    s3_key_prefix: str = "cloudtrail",
    enable_data_events: bool = False,
    data_event_selectors: list = None,
    tags: dict = None
):
    """
    Create all CloudTrail resources with proper orchestration.

    Manages IAM role creation (if needed) and CloudTrail configuration.

    :param scope: The CDKTF construct scope (stack instance)
    :param trail_name: Name for the CloudTrail
    :type trail_name: str
    :param s3_bucket_name: S3 bucket name for CloudTrail logs
    :type s3_bucket_name: str
    :param enable_logging: Enable CloudTrail logging (default: False for safety)
    :type enable_logging: bool
    :param enable_cloudwatch_logs: Enable CloudWatch Logs integration
    :type enable_cloudwatch_logs: bool
    :param cloudwatch_logs_group_arn: CloudWatch Logs group ARN
    :type cloudwatch_logs_group_arn: str
    :param is_multi_region_trail: Apply to all regions (default: True)
    :type is_multi_region_trail: bool
    :param enable_log_file_validation: Enable log file validation (default: True)
    :type enable_log_file_validation: bool
    :param kms_key_id: KMS key ID for encryption
    :type kms_key_id: str
    :param s3_key_prefix: S3 key prefix (default: "cloudtrail")
    :type s3_key_prefix: str
    :param enable_data_events: Enable data event logging (default: False)
    :type enable_data_events: bool
    :param data_event_selectors: Data event selector configuration
    :type data_event_selectors: list
    :param tags: Resource tags
    :type tags: dict
    :returns: Dictionary with created resources
    :rtype: dict

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import cloudtrail
        >>> 
        >>> resources = cloudtrail.create_cloudtrail_resources(
        ...     scope=self,
        ...     trail_name="ftr-audit-trail",
        ...     s3_bucket_name="my-cloudtrail-bucket",
        ...     enable_logging=True,
        ...     enable_cloudwatch_logs=True,
        ...     cloudwatch_logs_group_arn=log_group.arn
        ... )
        >>> 
        >>> trail = resources['trail']
        >>> role = resources.get('iam_role')  # Only if enable_cloudwatch_logs=True

    .. note::
       **Safe Defaults**:
       - enable_logging=False (no logging until explicitly enabled)
       - enable_data_events=False (no additional costs)
       
       **CloudWatch Logs Integration**:
       - Automatically creates IAM role if enable_cloudwatch_logs=True
       - Requires cloudwatch_logs_group_arn parameter
       
       **Cost Estimates**:
       - First trail: Free for management events
       - Additional trails: $2/month
       - Data events: $0.10 per 100,000 events
       - S3 storage: ~$0.023/GB/month
       - CloudWatch Logs: ~$0.50/GB ingested
    """
    resources = {}

    # Step 1: Create KMS key for CloudTrail encryption if requested (CIS Control 3.7)
    if create_kms_key:
        if not account_id:
            raise ValueError("account_id is required when create_kms_key=True")
        if not region:
            raise ValueError("region is required when create_kms_key=True")
        
        kms_resources = kms.create_cloudtrail_kms_key(
            scope=scope,
            account_id=account_id,
            cloudtrail_name=trail_name,
            region=region,
            resource_id="cloudtrail_kms_key"
        )
        resources['kms_key'] = kms_resources['key']
        resources['kms_alias'] = kms_resources['alias']
        kms_key_id = kms_resources['key'].arn

    # Step 2: Create CloudTrail's S3 bucket (if requested)
    if create_bucket:
        if not all([account_id, project_name, environment, region]):
            raise ValueError("When create_bucket=True, account_id, project_name, environment, and region are required")
        
        if not s3_bucket_name:
            s3_bucket_name = f"{project_name}-cloudtrail-{region}"
        
        bucket_resources = s3_bucket.create_cloudtrail_s3_bucket(
            scope=scope,
            bucket_name=s3_bucket_name,
            account_id=account_id,
            project_name=project_name,
            environment=environment,
            logging_bucket=logging_bucket,
            resource_id="cloudtrail_bucket"
        )
        resources['s3_bucket'] = bucket_resources['bucket']
        resources['s3_public_access_block'] = bucket_resources['public_access_block']
        resources['s3_bucket_policy'] = bucket_resources['bucket_policy']
        resources['s3_lifecycle'] = bucket_resources.get('lifecycle')
        resources['s3_logging'] = bucket_resources.get('logging')

    # Step 3: Create IAM role for CloudWatch Logs if enabled
    cloudwatch_logs_role_arn = None
    if enable_cloudwatch_logs:
        if not cloudwatch_logs_group_arn:
            raise ValueError("cloudwatch_logs_group_arn is required when enable_cloudwatch_logs=True")
        
        role, policy = create_cloudtrail_iam_role(
            scope=scope,
            role_name=f"{trail_name}-cloudwatch-role"
        )
        resources['iam_role'] = role
        resources['iam_policy_attachment'] = policy
        cloudwatch_logs_role_arn = role.arn

    # Create CloudTrail
    trail = create_cloudtrail(
        scope=scope,
        trail_name=trail_name,
        s3_bucket_name=s3_bucket_name,
        enable_logging=enable_logging,
        is_multi_region_trail=is_multi_region_trail,
        enable_log_file_validation=enable_log_file_validation,
        cloudwatch_logs_group_arn=cloudwatch_logs_group_arn if enable_cloudwatch_logs else None,
        cloudwatch_logs_role_arn=cloudwatch_logs_role_arn,
        kms_key_id=kms_key_id,
        s3_key_prefix=s3_key_prefix,
        enable_data_events=enable_data_events,
        data_event_selectors=data_event_selectors,
        tags=tags
    )
    resources['trail'] = trail

    return resources
