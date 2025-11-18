"""
AWS Backup S3 Bucket Creation

This module handles S3 bucket creation specifically for AWS Backup service.
Backup owns its bucket policy, lifecycle rules, and configuration.

"""

import json
from .. import s3


def create_backup_bucket_policy_json(bucket_name: str, account_id: str) -> str:
    """
    Create AWS Backup bucket policy JSON.
    
    This defines the least-privilege policy for AWS Backup service.
    
    Args:
        bucket_name: Name of the Backup S3 bucket
        account_id: AWS account ID
    
    Returns:
        JSON string with bucket policy
    """
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AWSBackupBucketPermissionsCheck",
                "Effect": "Allow",
                "Principal": {
                    "Service": "backup.amazonaws.com"
                },
                "Action": [
                    "s3:GetBucketAcl",
                    "s3:GetBucketLocation"
                ],
                "Resource": f"arn:aws:s3:::{bucket_name}",
                "Condition": {
                    "StringEquals": {
                        "AWS:SourceAccount": account_id
                    }
                }
            },
            {
                "Sid": "AWSBackupBucketPutObject",
                "Effect": "Allow",
                "Principal": {
                    "Service": "backup.amazonaws.com"
                },
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject"
                ],
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                "Condition": {
                    "StringEquals": {
                        "AWS:SourceAccount": account_id
                    }
                }
            }
        ]
    }
    
    return json.dumps(policy)


def create_backup_s3_bucket(
    scope,
    bucket_name: str,
    account_id: str,
    project_name: str,
    environment: str,
    logging_bucket: str = None,
    kms_key_id: str = None,
    resource_id: str = "backup_bucket"
):
    """
    Create FTR-compliant S3 bucket for AWS Backup.
    
    This creates a bucket with:
    - Backup-specific bucket policy
    - 7-year retention lifecycle
    - Public access blocking
    - Versioning and encryption
    - Optional access logging
    
    Args:
        scope: The CDKTF construct scope
        bucket_name: Name of the bucket
        account_id: AWS account ID
        project_name: Project name
        environment: Environment (dev, staging, prod)
        logging_bucket: Optional logs bucket name
        kms_key_id: Optional KMS key ID
        resource_id: Terraform resource ID
    
    Returns:
        dict: Created S3 resources
    
    Example:
        >>> from . import s3_bucket
        >>> backup_bucket = s3_bucket.create_backup_s3_bucket(
        ...     scope=stack,
        ...     bucket_name="myapp-backup-us-east-1",
        ...     account_id="123456789012",
        ...     project_name="myapp",
        ...     environment="prod",
        ...     logging_bucket="myapp-logs"
        ... )
    """
    # Create Backup-specific bucket policy
    policy_json = create_backup_bucket_policy_json(bucket_name, account_id)
    
    # Create Backup-specific lifecycle rule (7-year retention)
    lifecycle_rule = s3.create_lifecycle_rule(
        rule_id="backup-data-lifecycle",
        retention_days=2555,  # 7 years for compliance
        ia_transition_days=90,
        glacier_transition_days=180,
        deep_archive_transition_days=365,
        noncurrent_retention_days=90
    )
    
    # Build tags
    tags = {
        "Service": "AWSBackup",
        "Project": project_name,
        "Environment": environment
    }
    
    # Create the bucket using generic S3 method
    return s3.create_bucket(
        scope=scope,
        bucket_name=bucket_name,
        block_public_access=True,
        enable_versioning=True,
        enable_encryption=True,
        kms_key_id=kms_key_id,
        bucket_policy_json=policy_json,
        lifecycle_rules=[lifecycle_rule],
        logging_target_bucket=logging_bucket,
        logging_prefix="backup-access-logs/" if logging_bucket else None,
        tags=tags,
        resource_id=resource_id
    )
