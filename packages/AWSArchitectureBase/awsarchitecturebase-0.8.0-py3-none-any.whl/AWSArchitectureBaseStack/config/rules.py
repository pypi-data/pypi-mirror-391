"""
AWS Config Rules Configuration
===============================

Functions for creating and managing AWS Config compliance rules.
"""

from cdktf_cdktf_provider_aws.config_config_rule import (
    ConfigConfigRule,
    ConfigConfigRuleSource,
    ConfigConfigRuleSourceSourceDetail
)


def create_config_rule(
    scope,
    rule_name: str,
    source_identifier: str,
    resource_id: str = None,
    description: str = None,
    depends_on: list = None
):
    """
    Create an AWS Config managed rule.

    Config rules evaluate resource compliance against specific conditions.

    :param scope: The CDKTF construct scope (stack instance)
    :param rule_name: Name for the Config rule
    :type rule_name: str
    :param source_identifier: AWS managed rule identifier
    :type source_identifier: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param description: Description of the rule
    :type description: str
    :param depends_on: List of resources this depends on (recorder)
    :type depends_on: list
    :returns: Config rule resource
    :rtype: ConfigConfigRule

    **Common AWS Managed Rules:**
    
    - `S3_BUCKET_VERSIONING_ENABLED` - S3 buckets have versioning enabled
    - `S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED` - S3 buckets are encrypted
    - `ENCRYPTED_VOLUMES` - EBS volumes are encrypted
    - `IAM_PASSWORD_POLICY` - Account has strong password policy
    - `ROOT_ACCOUNT_MFA_ENABLED` - Root account has MFA enabled
    - `IAM_USER_MFA_ENABLED` - IAM users have MFA enabled
    - `RDS_STORAGE_ENCRYPTED` - RDS instances use encryption
    - `CLOUDTRAIL_ENABLED` - CloudTrail is enabled

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import config
        >>> 
        >>> rule = config.create_config_rule(
        ...     scope=self,
        ...     rule_name="s3-bucket-encryption",
        ...     source_identifier="S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED",
        ...     description="Ensure S3 buckets have encryption enabled"
        ... )

    .. note::
       Find available managed rules:
       `aws configservice describe-config-rules --region <region>`
       
       Or visit: https://docs.aws.amazon.com/config/latest/developerguide/managed-rules-by-aws-config.html
    """
    if not resource_id:
        resource_id = f"rule_{rule_name.replace('-', '_')}"

    source = ConfigConfigRuleSource(
        owner="AWS",
        source_identifier=source_identifier
    )

    rule = ConfigConfigRule(
        scope,
        resource_id,
        name=rule_name,
        description=description or f"AWS Config rule: {rule_name}",
        source=source,
        depends_on=depends_on
    )

    return rule


def enable_ftr_compliance_rules(
    scope,
    rules: list = None,
    depends_on: list = None
):
    """
    Enable AWS Config compliance rules for FTR requirements.

    Activates managed Config rules based on compliance requirements.
    By default, enables common FTR compliance rules.

    :param scope: The CDKTF construct scope (stack instance)
    :param rules: List of rule identifiers to enable (AWS managed rule names)
                 If None, uses default FTR compliance rules
    :type rules: list
    :param depends_on: List of resources these rules depend on (recorder)
    :type depends_on: list
    :returns: Dictionary of created Config rules
    :rtype: dict

    **Default FTR Compliance Rules:**
    
    - S3 encryption and versioning
    - IAM security (MFA, password policies)
    - Encryption at rest (EBS, RDS)
    - CloudTrail monitoring
    - VPC security groups

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import config
        >>> 
        >>> # Enable default FTR rules
        >>> rules = config.enable_ftr_compliance_rules(
        ...     scope=self,
        ...     depends_on=[recorder]
        ... )
        >>> 
        >>> # Enable specific rules
        >>> rules = config.enable_ftr_compliance_rules(
        ...     scope=self,
        ...     rules=[
        ...         'S3_BUCKET_VERSIONING_ENABLED',
        ...         'ENCRYPTED_VOLUMES',
        ...         'IAM_PASSWORD_POLICY'
        ...     ],
        ...     depends_on=[recorder]
        ... )

    .. note::
       **Cost**: Each rule evaluation costs ~$0.001
       With ~20 default rules and 100 resources: ~$2/month
       
       **Performance**: Rules evaluate when resources change or periodically.
    """
    enabled_rules = {}

    # Default FTR compliance rules
    if rules is None:
        rules = [
            'S3_BUCKET_VERSIONING_ENABLED',
            'S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED',
            'S3_BUCKET_PUBLIC_READ_PROHIBITED',
            'S3_BUCKET_PUBLIC_WRITE_PROHIBITED',
            'ENCRYPTED_VOLUMES',
            'RDS_STORAGE_ENCRYPTED',
            'IAM_PASSWORD_POLICY',
            'ROOT_ACCOUNT_MFA_ENABLED',
            'IAM_USER_MFA_ENABLED',
            'CLOUDTRAIL_ENABLED',
            'CLOUD_TRAIL_LOG_FILE_VALIDATION_ENABLED',
            'VPC_DEFAULT_SECURITY_GROUP_CLOSED',
            'EC2_INSTANCE_NO_PUBLIC_IP',
            'RDS_INSTANCE_PUBLIC_ACCESS_CHECK',
        ]

    # Create each Config rule
    for rule_identifier in rules:
        rule_name = rule_identifier.lower().replace('_', '-')
        
        enabled_rules[rule_identifier] = create_config_rule(
            scope=scope,
            rule_name=rule_name,
            source_identifier=rule_identifier,
            depends_on=depends_on
        )

    return enabled_rules
