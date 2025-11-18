"""
AWS KMS (Key Management Service) Module
========================================

Customer-managed encryption keys for AWS services.

Public Functions:
-----------------
- create_kms_key() - Create a customer-managed KMS key with automatic rotation
- create_cloudtrail_kms_key() - Create KMS key for CloudTrail log encryption (CIS 3.7)
"""

from .key import create_kms_key, create_cloudtrail_kms_key

__all__ = [
    'create_kms_key',
    'create_cloudtrail_kms_key',
]
