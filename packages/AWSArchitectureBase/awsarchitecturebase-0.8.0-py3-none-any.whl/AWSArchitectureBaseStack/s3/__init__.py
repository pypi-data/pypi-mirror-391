"""
S3 Module - Simple & Clean
===========================

Generic S3 bucket creation. No service-specific logic here.
Services import this and provide their own policies/lifecycle rules.

"""

from .bucket import create_bucket, create_lifecycle_rule, boto_create_bucket
from .resources import create_s3_resources

__all__ = [
    "create_bucket",
    "create_lifecycle_rule",
    "boto_create_bucket",
    "create_s3_resources",  # For state bucket setup
]
