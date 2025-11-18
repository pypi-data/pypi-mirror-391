"""
AWS KMS Customer-Managed Keys
==============================

Functions for creating and managing KMS keys with automatic rotation.

CIS AWS Foundations Benchmark v3.0.0:
- Control 3.7: Ensure CloudTrail logs are encrypted at rest using KMS CMKs
- Control 3.8: Ensure rotation for customer-created CMKs is enabled
"""

import json
from cdktf_cdktf_provider_aws.kms_key import KmsKey
from cdktf_cdktf_provider_aws.kms_alias import KmsAlias


def create_kms_key(
    scope,
    key_description: str,
    alias_name: str,
    enable_key_rotation: bool = True,
    deletion_window_in_days: int = 30,
    key_policy: dict = None,
    resource_id: str = "kms_key"
):
    """
    Create a customer-managed KMS key (CMK) with automatic rotation.

    KMS keys provide envelope encryption for AWS services and allow you to
    control access and rotation of encryption keys.

    :param scope: The CDKTF construct scope (stack instance)
    :param key_description: Description of the key's purpose
    :type key_description: str
    :param alias_name: Alias name for the key (must start with 'alias/')
    :type alias_name: str
    :param enable_key_rotation: Enable automatic annual key rotation
    :type enable_key_rotation: bool
    :param deletion_window_in_days: Days before key deletion (7-30)
    :type deletion_window_in_days: int
    :param key_policy: Custom IAM policy for key access (JSON dict)
    :type key_policy: dict
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: Dictionary with KMS key and alias resources
    :rtype: dict

    **CIS v3.0.0 Requirements:**
    
    - **Control 3.7**: CloudTrail logs must use KMS CMKs (not AWS-managed keys)
    - **Control 3.8**: Customer-created CMKs must have rotation enabled
    
    **Key Rotation:**
    
    - Automatic rotation happens annually
    - Old key material is retained for decryption
    - No re-encryption of existing data needed
    - Rotation is transparent to applications

    **Deletion Window:**
    
    - Minimum: 7 days
    - Maximum: 30 days
    - Default: 30 days (recommended for safety)
    - Allows recovery from accidental deletion

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import kms
        >>> 
        >>> # Create KMS key for CloudTrail
        >>> key = kms.create_kms_key(
        ...     scope=self,
        ...     key_description="CloudTrail log encryption",
        ...     alias_name="alias/cloudtrail-logs",
        ...     enable_key_rotation=True
        ... )

    .. note::
       **Cost**: ~$1/month per key + $0.03 per 10,000 encryption/decryption requests
       
       **Best Practice**: Enable key rotation for compliance (CIS Control 3.8)
       
    .. warning::
       Deleting a KMS key makes all data encrypted with it unrecoverable.
       Use the deletion window to prevent accidental data loss.
    """
    # Create KMS key
    kms_key = KmsKey(
        scope,
        resource_id,
        description=key_description,
        enable_key_rotation=enable_key_rotation,
        deletion_window_in_days=deletion_window_in_days,
        policy=json.dumps(key_policy) if key_policy else None
    )

    # Create alias for easier key reference
    kms_alias = KmsAlias(
        scope,
        f"{resource_id}_alias",
        name=alias_name,
        target_key_id=kms_key.key_id
    )

    return {
        'key': kms_key,
        'alias': kms_alias
    }


def create_cloudtrail_kms_key(
    scope,
    account_id: str,
    cloudtrail_name: str,
    region: str = None,
    resource_id: str = "cloudtrail_kms_key"
):
    """
    Create a KMS key specifically for CloudTrail log encryption (CIS Control 3.7).

    This function creates a KMS key with the proper policy to allow CloudTrail
    to encrypt logs. The policy allows CloudTrail to use the key and allows
    account administrators to manage it.

    :param scope: The CDKTF construct scope (stack instance)
    :param account_id: AWS account ID
    :type account_id: str
    :param cloudtrail_name: Name of the CloudTrail trail
    :type cloudtrail_name: str
    :param region: AWS region (uses '*' if not specified)
    :type region: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: Dictionary with KMS key and alias resources
    :rtype: dict

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import kms
        >>> 
        >>> # Create CloudTrail KMS key
        >>> key = kms.create_cloudtrail_kms_key(
        ...     scope=self,
        ...     account_id="123456789012",
        ...     cloudtrail_name="my-trail",
        ...     region="us-east-1"
        ... )
    """
    region_pattern = region if region else "*"
    
    # CloudTrail-specific KMS key policy
    key_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Enable IAM User Permissions",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{account_id}:root"
                },
                "Action": "kms:*",
                "Resource": "*"
            },
            {
                "Sid": "Allow CloudTrail to encrypt logs",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "kms:GenerateDataKey*",
                "Resource": "*",
                "Condition": {
                    "StringLike": {
                        "kms:EncryptionContext:aws:cloudtrail:arn": f"arn:aws:cloudtrail:{region_pattern}:{account_id}:trail/{cloudtrail_name}"
                    }
                }
            },
            {
                "Sid": "Allow CloudTrail to describe key",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "kms:DescribeKey",
                "Resource": "*"
            },
            {
                "Sid": "Allow principals in the account to decrypt log files",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{account_id}:root"
                },
                "Action": [
                    "kms:Decrypt",
                    "kms:ReEncryptFrom"
                ],
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "kms:CallerAccount": account_id
                    },
                    "StringLike": {
                        "kms:EncryptionContext:aws:cloudtrail:arn": f"arn:aws:cloudtrail:{region_pattern}:{account_id}:trail/{cloudtrail_name}"
                    }
                }
            },
            {
                "Sid": "Allow alias creation during setup",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{account_id}:root"
                },
                "Action": "kms:CreateAlias",
                "Resource": "*"
            }
        ]
    }

    return create_kms_key(
        scope=scope,
        key_description=f"KMS key for CloudTrail log encryption - {cloudtrail_name}",
        alias_name=f"alias/{cloudtrail_name}-logs",
        enable_key_rotation=True,
        deletion_window_in_days=30,
        key_policy=key_policy,
        resource_id=resource_id
    )
