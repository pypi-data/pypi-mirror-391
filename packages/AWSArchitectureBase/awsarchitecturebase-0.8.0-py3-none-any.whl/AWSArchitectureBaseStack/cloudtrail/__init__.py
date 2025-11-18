"""
AWS CloudTrail Module
=====================

Provides audit logging and compliance tracking for AWS API calls.

AWS CloudTrail:
- Records all AWS API calls
- Tracks user activity and resource changes
- Enables security analysis and compliance auditing
- Integrates with CloudWatch Logs
- Supports multi-region trails
- Data event logging for S3 and Lambda
"""

from .trail import create_cloudtrail
from .iam_role import create_cloudtrail_iam_role
from .resources import create_cloudtrail_resources

__all__ = [
    "create_cloudtrail",
    "create_cloudtrail_iam_role",
    "create_cloudtrail_resources",
]
