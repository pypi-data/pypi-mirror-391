"""
AWS Config Resources Orchestration
===================================

High-level functions for creating complete AWS Config setup.
"""

from . import recorder, rules, s3_bucket


def create_config_resources(
    scope,
    region: str,
    s3_bucket_name: str = None,
    account_id: str = None,
    project_name: str = None,
    environment: str = None,
    logging_bucket: str = None,
    create_bucket: bool = True,
    recorder_name: str = "default",
    channel_name: str = "default",
    role_name: str = None,
    enable_rules: bool = False,
    config_rules: list = None,
    s3_key_prefix: str = "config",
    sns_topic_arn: str = None,
    enable_recorder: bool = False
):
    """
    Create complete AWS Config infrastructure with recorder, delivery channel, and optional rules.

    This orchestration function sets up:
    - AWS-managed service-linked role (AWSServiceRoleForConfig)
    - Configuration recorder
    - S3 delivery channel
    - Optional: Config compliance rules

    :param scope: The CDKTF construct scope (stack instance)
    :param region: AWS region for Config resources
    :type region: str
    :param s3_bucket_name: S3 bucket name for configuration storage
    :type s3_bucket_name: str
    :param account_id: AWS account ID (required for service-linked role ARN)
    :type account_id: str
    :param project_name: Project name for resource naming
    :type project_name: str
    :param environment: Environment name (dev, prod, etc.)
    :type environment: str
    :param logging_bucket: S3 bucket for access logs
    :type logging_bucket: str
    :param create_bucket: Whether to create the S3 bucket (default: True)
    :type create_bucket: bool
    :param recorder_name: Name for configuration recorder (default: "default")
    :type recorder_name: str
    :param channel_name: Name for delivery channel (default: "default")
    :type channel_name: str
    :param enable_rules: Enable Config compliance rules (default: False)
    :type enable_rules: bool
    :param config_rules: List of rule identifiers to enable (default: FTR compliance rules)
    :type config_rules: list
    :param s3_key_prefix: Prefix for S3 objects (default: "config")
    :type s3_key_prefix: str
    :param sns_topic_arn: Optional SNS topic for notifications
    :type sns_topic_arn: str
    :param enable_recorder: Start recording immediately (default: False)
    :type enable_recorder: bool
    :returns: Dictionary with created resources
    :rtype: dict

    **Resource Dictionary Keys:**
    
    - `recorder`: Configuration recorder
    - `channel`: Delivery channel
    - `recorder_status`: Recorder status (if enabled)
    - `rules`: Dictionary of Config rules (if enabled)
    - `s3_bucket`: S3 bucket (if create_bucket=True)
    - `s3_public_access_block`: Public access block
    - `s3_bucket_policy`: Bucket policy
    - `s3_lifecycle`: Lifecycle configuration
    - `s3_logging`: Logging configuration

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import config
        >>> 
        >>> # Infrastructure only (safe for testing)
        >>> resources = config.create_config_resources(
        ...     scope=self,
        ...     region="us-east-1",
        ...     s3_bucket_name="my-config-bucket"
        ... )
        >>> 
        >>> # With compliance rules enabled
        >>> resources = config.create_config_resources(
        ...     scope=self,
        ...     region="us-east-1",
        ...     s3_bucket_name="my-config-bucket",
        ...     enable_recorder=True,
        ...     enable_rules=True,
        ...     config_rules=['S3_BUCKET_VERSIONING_ENABLED', 'ENCRYPTED_VOLUMES']
        ... )

    .. note::
       **Cost Estimates:**
       
       - Infrastructure only: ~$0.003/resource/month (just recorder)
       - With rules: ~$2-10/month depending on resource count and rule evaluations
       
       **Safe Defaults:**
       
       - enable_recorder=False: Creates infrastructure but doesn't start recording
       - enable_rules=False: No compliance rule evaluations
       
       **S3 Bucket Policy Required:**
       
       Your S3 bucket needs a policy allowing Config service to write:
       
       .. code-block:: json
       
          {
            "Effect": "Allow",
            "Principal": {"Service": "config.amazonaws.com"},
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::bucket-name/config/*"
          }
    """
    resources = {}

    # Step 1: Create Config's S3 bucket (if requested)
    if create_bucket:
        if not all([account_id, project_name, environment]):
            raise ValueError("When create_bucket=True, account_id, project_name, and environment are required")
        
        if not s3_bucket_name:
            s3_bucket_name = f"{project_name}-config-{region}"
        
        bucket_resources = s3_bucket.create_config_s3_bucket(
            scope=scope,
            bucket_name=s3_bucket_name,
            account_id=account_id,
            project_name=project_name,
            environment=environment,
            logging_bucket=logging_bucket,
            resource_id="config_bucket"
        )
        resources['s3_bucket'] = bucket_resources['bucket']
        resources['s3_public_access_block'] = bucket_resources['public_access_block']
        resources['s3_bucket_policy'] = bucket_resources['bucket_policy']
        resources['s3_lifecycle'] = bucket_resources.get('lifecycle')
        resources['s3_logging'] = bucket_resources.get('logging')

    # Step 2: Use AWS service-linked role for Config
    # AWS Config automatically creates the service-linked role AWSServiceRoleForConfig
    # This is the AWS-recommended approach and resolves CONFIG_RECORDER_CUSTOM_ROLE finding
    if not account_id:
        raise ValueError("account_id is required to construct service-linked role ARN")
    
    service_linked_role_arn = f"arn:aws:iam::{account_id}:role/aws-service-role/config.amazonaws.com/AWSServiceRoleForConfig"

    # Create configuration recorder using service-linked role
    config_recorder = recorder.create_config_recorder(
        scope=scope,
        recorder_name=recorder_name,
        role_arn=service_linked_role_arn
    )
    resources['recorder'] = config_recorder

    # Create delivery channel
    delivery_channel = recorder.create_delivery_channel(
        scope=scope,
        channel_name=channel_name,
        s3_bucket_name=s3_bucket_name,
        s3_key_prefix=s3_key_prefix,
        sns_topic_arn=sns_topic_arn,
        depends_on=[config_recorder]
    )
    resources['channel'] = delivery_channel

    # Enable recorder if requested
    if enable_recorder:
        recorder_status = recorder.enable_config_recorder(
            scope=scope,
            recorder_name=recorder_name,
            depends_on=[config_recorder, delivery_channel]
        )
        resources['recorder_status'] = recorder_status

    # Enable Config rules if requested
    if enable_rules:
        config_rules_dict = rules.enable_ftr_compliance_rules(
            scope=scope,
            rules=config_rules,
            depends_on=[config_recorder]
        )
        resources['rules'] = config_rules_dict

    return resources
