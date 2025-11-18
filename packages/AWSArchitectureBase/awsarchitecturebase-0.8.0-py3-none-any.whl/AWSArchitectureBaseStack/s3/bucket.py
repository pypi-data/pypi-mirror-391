"""
S3 Bucket - Simple & Generic
=============================

The ONLY S3 bucket creation module you need.
Clean, simple, and reusable by any service.

"""

import json
import boto3
from botocore.exceptions import ClientError
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket
from cdktf_cdktf_provider_aws.s3_bucket_versioning import S3BucketVersioningA
from cdktf_cdktf_provider_aws.s3_bucket_public_access_block import S3BucketPublicAccessBlock
from cdktf_cdktf_provider_aws.s3_bucket_policy import S3BucketPolicy
from cdktf_cdktf_provider_aws.s3_bucket_logging import S3BucketLoggingA
from cdktf_cdktf_provider_aws.s3_bucket_lifecycle_configuration import (
    S3BucketLifecycleConfiguration,
    S3BucketLifecycleConfigurationRule,
    S3BucketLifecycleConfigurationRuleTransition,
    S3BucketLifecycleConfigurationRuleExpiration,
    S3BucketLifecycleConfigurationRuleNoncurrentVersionTransition,
    S3BucketLifecycleConfigurationRuleNoncurrentVersionExpiration,
    S3BucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload
)
from ..utils import naming


def create_ssl_enforcement_policy(bucket_name: str, existing_policy_json: str = None) -> str:
    """
    Create or merge SSL enforcement policy for S3 bucket.
    
    Creates a bucket policy that denies all non-HTTPS requests.
    This satisfies CIS AWS Foundations Benchmark control S3.5.
    
    Args:
        bucket_name: S3 bucket name
        existing_policy_json: Optional existing policy to merge with
    
    Returns:
        str: JSON policy string with SSL enforcement
    
    Example:
        >>> policy = create_ssl_enforcement_policy("my-bucket")
    """
    ssl_statement = {
        "Sid": "DenyInsecureTransport",
        "Effect": "Deny",
        "Principal": "*",
        "Action": "s3:*",
        "Resource": [
            f"arn:aws:s3:::{bucket_name}/*",
            f"arn:aws:s3:::{bucket_name}"
        ],
        "Condition": {
            "Bool": {
                "aws:SecureTransport": "false"
            }
        }
    }
    
    if existing_policy_json:
        # Merge with existing policy
        existing_policy = json.loads(existing_policy_json)
        if "Statement" not in existing_policy:
            existing_policy["Statement"] = []
        
        # Check if SSL enforcement already exists
        has_ssl_enforcement = any(
            stmt.get("Sid") == "DenyInsecureTransport"
            for stmt in existing_policy["Statement"]
        )
        
        if not has_ssl_enforcement:
            existing_policy["Statement"].append(ssl_statement)
        
        return json.dumps(existing_policy)
    else:
        # Create new policy with just SSL enforcement
        return json.dumps({
            "Version": "2012-10-17",
            "Statement": [ssl_statement]
        })


def create_bucket(
    scope,
    bucket_name: str,
    # Optional: Security settings
    block_public_access: bool = True,
    enable_versioning: bool = True,
    enable_encryption: bool = True,
    kms_key_id: str = None,
    enforce_ssl: bool = True,
    # Optional: Bucket policy (JSON string)
    bucket_policy_json: str = None,
    # Optional: Lifecycle rules
    lifecycle_rules: list = None,
    # Optional: Access logging
    logging_target_bucket: str = None,
    logging_prefix: str = None,
    # Optional: Tags
    tags: dict = None,
    # Optional: Resource IDs
    resource_id: str = None
):
    """
    Create an S3 bucket with optional compliance features.
    
    This is the ONE method for creating S3 buckets. Keep it simple.
    Services can add their specific policies and lifecycle rules.
    
    Args:
        scope: CDKTF scope
        bucket_name: Bucket name (auto-sanitized)
        block_public_access: Block all public access (default: True)
        enable_versioning: Enable versioning (default: True)
        enable_encryption: Enable encryption (default: True)
        kms_key_id: Optional KMS key (default: SSE-S3)
        enforce_ssl: Require HTTPS/TLS for all requests (default: True, CIS S3.5)
        bucket_policy_json: Optional bucket policy JSON string
        lifecycle_rules: Optional list of lifecycle rule dicts
        logging_target_bucket: Optional target bucket for access logs
        logging_prefix: Optional prefix for log objects
        tags: Optional tags dict
        resource_id: Optional resource ID (default: sanitized bucket_name)
    
    Returns:
        dict: {
            'bucket': S3Bucket,
            'public_access_block': S3BucketPublicAccessBlock (if enabled),
            'versioning': S3BucketVersioningA (if enabled),
            'policy': S3BucketPolicy (if provided),
            'lifecycle': S3BucketLifecycleConfiguration (if provided),
            'logging': S3BucketLoggingA (if enabled)
        }
    
    Example - Simple bucket:
        >>> bucket = create_bucket(stack, "my-app-data")
    
    Example - Service-specific bucket:
        >>> policy_json = json.dumps({
        ...     "Version": "2012-10-17",
        ...     "Statement": [...]
        ... })
        >>> rules = [create_lifecycle_rule(retention_days=365)]
        >>> bucket = create_bucket(
        ...     scope=stack,
        ...     bucket_name="my-app-config",
        ...     bucket_policy_json=policy_json,
        ...     lifecycle_rules=rules,
        ...     logging_target_bucket="my-logs"
        ... )
    """
    resources = {}
    
    # Sanitize bucket name
    bucket_name = naming.properize_string(bucket_name)
    if not resource_id:
        resource_id = bucket_name.replace("-", "_")
    
    # Build tags
    bucket_tags = tags or {}
    if "ManagedBy" not in bucket_tags:
        bucket_tags["ManagedBy"] = "CDKTF"
    
    # Build encryption config
    encryption_config = None
    if enable_encryption:
        if kms_key_id:
            encryption_config = {
                "rule": {
                    "apply_server_side_encryption_by_default": {
                        "sse_algorithm": "aws:kms",
                        "kms_master_key_id": kms_key_id
                    },
                    "bucket_key_enabled": True
                }
            }
        else:
            encryption_config = {
                "rule": {
                    "apply_server_side_encryption_by_default": {
                        "sse_algorithm": "AES256"
                    },
                    "bucket_key_enabled": True
                }
            }
    
    # 1. Create base bucket
    bucket = S3Bucket(
        scope,
        resource_id,
        bucket=bucket_name,
        server_side_encryption_configuration=encryption_config,
        tags=bucket_tags
    )
    resources['bucket'] = bucket
    
    # 2. Block public access
    if block_public_access:
        public_access_block = S3BucketPublicAccessBlock(
            scope,
            f"{resource_id}_public_access_block",
            bucket=bucket.id,
            block_public_acls=True,
            block_public_policy=True,
            ignore_public_acls=True,
            restrict_public_buckets=True
        )
        resources['public_access_block'] = public_access_block
    
    # 3. Enable versioning
    if enable_versioning:
        versioning = S3BucketVersioningA(
            scope,
            f"{resource_id}_versioning",
            bucket=bucket.id,
            versioning_configuration={"status": "Enabled"}
        )
        resources['versioning'] = versioning
    
    # 4. Add bucket policy (with SSL enforcement if enabled)
    final_policy_json = bucket_policy_json
    
    # Enforce SSL/TLS if requested (CIS AWS Foundations Benchmark S3.5)
    if enforce_ssl:
        final_policy_json = create_ssl_enforcement_policy(bucket_name, bucket_policy_json)
    
    if final_policy_json:
        bucket_policy = S3BucketPolicy(
            scope,
            f"{resource_id}_policy",
            bucket=bucket.id,
            policy=final_policy_json
        )
        resources['bucket_policy'] = bucket_policy
    
    # 5. Add lifecycle rules
    if lifecycle_rules:
        lifecycle = S3BucketLifecycleConfiguration(
            scope,
            f"{resource_id}_lifecycle",
            bucket=bucket.id,
            rule=lifecycle_rules
        )
        resources['lifecycle'] = lifecycle
    
    # 6. Enable access logging
    if logging_target_bucket:
        logging = S3BucketLoggingA(
            scope,
            f"{resource_id}_logging",
            bucket=bucket.id,
            target_bucket=logging_target_bucket,
            target_prefix=logging_prefix or f"{bucket_name}/"
        )
        resources['logging'] = logging
    
    return resources


def create_lifecycle_rule(
    rule_id: str,
    enabled: bool = True,
    retention_days: int = None,
    ia_transition_days: int = None,
    glacier_transition_days: int = None,
    deep_archive_transition_days: int = None,
    noncurrent_retention_days: int = None,
    abort_incomplete_multipart_days: int = 7
):
    """
    Create a lifecycle rule dict for S3 buckets.
    
    Helper function to make lifecycle rules easy to create.
    Returns a dict that can be passed to create_bucket().
    
    Args:
        rule_id: Unique ID for this rule
        enabled: Whether rule is enabled (default: True)
        retention_days: Delete objects after X days
        ia_transition_days: Transition to IA after X days
        glacier_transition_days: Transition to Glacier after X days
        deep_archive_transition_days: Transition to Deep Archive after X days
        noncurrent_retention_days: Delete noncurrent versions after X days
        abort_incomplete_multipart_days: Abort incomplete uploads after X days
    
    Returns:
        dict: Lifecycle rule configuration
    
    Example:
        >>> # 7-year retention with transitions
        >>> rule = create_lifecycle_rule(
        ...     rule_id="config-retention",
        ...     retention_days=2555,
        ...     ia_transition_days=90,
        ...     glacier_transition_days=180
        ... )
    """
    # Build rule with required fields
    rule_config = {
        "id": rule_id,
        "status": "Enabled" if enabled else "Disabled"
    }
    
    # Transitions (move to cheaper storage classes) - use S3BucketLifecycleConfigurationRuleTransition objects
    transitions = []
    if ia_transition_days:
        transitions.append(
            S3BucketLifecycleConfigurationRuleTransition(
                days=ia_transition_days,
                storage_class="STANDARD_IA"
            )
        )
    if glacier_transition_days:
        transitions.append(
            S3BucketLifecycleConfigurationRuleTransition(
                days=glacier_transition_days,
                storage_class="GLACIER"
            )
        )
    if deep_archive_transition_days:
        transitions.append(
            S3BucketLifecycleConfigurationRuleTransition(
                days=deep_archive_transition_days,
                storage_class="DEEP_ARCHIVE"
            )
        )
    if transitions:
        rule_config["transition"] = transitions
    
    # Expiration (delete objects) - use S3BucketLifecycleConfigurationRuleExpiration object
    if retention_days:
        rule_config["expiration"] = [
            S3BucketLifecycleConfigurationRuleExpiration(days=retention_days)
        ]
    
    # Noncurrent version expiration - use S3BucketLifecycleConfigurationRuleNoncurrentVersionExpiration object
    if noncurrent_retention_days:
        rule_config["noncurrent_version_expiration"] = [
            S3BucketLifecycleConfigurationRuleNoncurrentVersionExpiration(
                noncurrent_days=noncurrent_retention_days
            )
        ]
    
    # Abort incomplete multipart uploads - use S3BucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload object
    if abort_incomplete_multipart_days:
        rule_config["abort_incomplete_multipart_upload"] = [
            S3BucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload(
                days_after_initiation=abort_incomplete_multipart_days
            )
        ]
    
    # Return as S3BucketLifecycleConfigurationRule object
    return S3BucketLifecycleConfigurationRule(**rule_config)


def boto_create_bucket(
    bucket_name: str,
    region: str,
    profile: str = "default"
) -> str:
    """
    Create S3 bucket using Boto3 (for initialization/state buckets).
    
    This is for creating buckets OUTSIDE of CDKTF (like state buckets).
    For regular buckets, use create_bucket() instead.
    
    Features applied:
    - Versioning enabled
    - Encryption enabled (AES256)
    - Public access blocked
    
    Args:
        bucket_name: Bucket name
        region: AWS region
        profile: AWS profile (default: "default")
    
    Returns:
        str: Bucket name if successful
    
    Example:
        >>> boto_create_bucket("my-tfstate", "us-east-1", "devops")
    """
    session = boto3.Session(profile_name=profile)
    s3 = session.client("s3", region_name=region)
    
    bucket_name = naming.properize_string(bucket_name)
    
    # Check if exists
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"✓ Bucket '{bucket_name}' already exists")
        return bucket_name
    except ClientError as e:
        if e.response['Error']['Code'] != '404':
            raise
    
    # Create bucket
    try:
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"✓ Created bucket '{bucket_name}'")
        
        # Enable versioning
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"✓ Enabled versioning")
        
        # Enable encryption
        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    },
                    'BucketKeyEnabled': True
                }]
            }
        )
        print(f"✓ Enabled encryption")
        
        # Block public access
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print(f"✓ Blocked public access")
        
        return bucket_name
        
    except ClientError as e:
        print(f"✗ Error creating bucket: {e}")
        raise
