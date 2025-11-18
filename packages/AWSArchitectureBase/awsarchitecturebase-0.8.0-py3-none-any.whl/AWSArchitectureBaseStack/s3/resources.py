"""
S3 Resources orchestration.

This module provides high-level functions to create complete S3 infrastructure
following AWS best practices and security guidelines.
"""

from . import bucket, backend


def create_s3_resources(
    scope,
    project_name: str,
    environment: str,
    region: str,
    profile: str,
    state_bucket_name: str = None,
    app_buckets: list = None
):
    """
    Create complete S3 infrastructure with best practices.
    
    This orchestration function creates:
    - State bucket for Terraform backend (via Boto3, with versioning & encryption)
    - Terraform S3 backend configuration
    - Optional application data buckets
    
    **AWS Best Practices Applied:**
    - Bucket versioning enabled
    - Server-side encryption (AES256)
    - Bucket key enabled for cost optimization
    - Private ACL by default
    - Proper tagging for resource management
    
    :param scope: The CDKTF construct scope (stack instance)
    :param project_name: Project name for naming and tagging
    :param environment: Environment (dev, staging, prod)
    :param region: AWS region
    :param profile: AWS profile to use
    :param state_bucket_name: Optional custom state bucket name
    :param app_buckets: Optional list of dicts with bucket configurations
                        [{'name': 'my-bucket', 'resource_id': 'my_bucket'}]
    :returns: Dictionary with created resources
    :rtype: dict
    
    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import s3
        >>> resources = s3.create_s3_resources(
        ...     scope=self,
        ...     project_name="my-app",
        ...     environment="dev",
        ...     region="us-east-1",
        ...     profile="default",
        ...     app_buckets=[
        ...         {'name': 'my-app-data', 'resource_id': 'app_data'},
        ...         {'name': 'my-app-backups', 'resource_id': 'backups'}
        ...     ]
        ... )
    """
    resources = {}
    
    # Determine state bucket name
    if not state_bucket_name:
        from ..utils import naming
        state_bucket_name = naming.properize_string(
            f"{region}-{project_name}-tfstate"
        )
    
    # 1. Create state bucket using Boto3 (with versioning & encryption)
    actual_bucket_name = bucket.boto_create_bucket(
        bucket_name=state_bucket_name,
        region=region,
        profile=profile
    )
    resources['state_bucket_name'] = actual_bucket_name
    
    # 2. Configure Terraform backend
    backend.create_terraform_backend(
        scope=scope,
        state_bucket_name=actual_bucket_name,
        project_name=project_name,
        region=region,
        profile=profile
    )
    
    # 3. Create application buckets if specified
    if app_buckets:
        resources['app_buckets'] = []
        for bucket_config in app_buckets:
            bucket_resources = bucket.create_bucket(
                scope=scope,
                bucket_name=bucket_config['name'],
                resource_id=bucket_config.get('resource_id', 'app_bucket'),
                tags={
                    "Environment": environment,
                    "Project": project_name
                }
            )
            resources['app_buckets'].append({
                'resource_id': bucket_config.get('resource_id'),
                'bucket': bucket_resources['bucket']
            })
    
    return resources
