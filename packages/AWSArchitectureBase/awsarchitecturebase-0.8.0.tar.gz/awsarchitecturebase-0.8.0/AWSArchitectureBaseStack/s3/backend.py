"""
Terraform backend configuration utilities.

This module provides functions for configuring Terraform S3 backends
for remote state storage.
"""

from cdktf import S3Backend, TerraformOutput
from ..utils.naming import properize_string


def create_terraform_backend(
    scope,
    state_bucket_name: str,
    project_name: str,
    region: str,
    profile: str = "default",
    class_name: str = None
) -> None:
    """
    Configure Terraform S3 backend for state storage.

    Sets up remote state storage in S3 with proper bucket naming and
    creates a Terraform output with the bucket name for reference.

    :param scope: The CDKTF construct scope (usually the stack instance)
    :param state_bucket_name: Name of the S3 bucket for state storage (will be sanitized)
    :type state_bucket_name: str
    :param project_name: Project name for the state file key
    :type project_name: str
    :param region: AWS region where the bucket exists
    :type region: str
    :param profile: AWS profile to use (default: "default")
    :type profile: str
    :param class_name: Class name for bucket naming if state_bucket_name not provided
    :type class_name: str

    """
    if not state_bucket_name and class_name:
        state_bucket_name = properize_string(f"{region}-{class_name}-tfstate")
    
    state_bucket_name = properize_string(state_bucket_name)

    TerraformOutput(
        scope,
        "state_bucket_name",
        value=state_bucket_name,
        description=(
            "Name of the S3 bucket for Terraform state. "
            "This bucket is automatically created by s3.create_s3_resources()."
        ),
    )

    S3Backend(
        scope,
        bucket=state_bucket_name,
        key=f"{project_name}/terraform.tfstate",
        region=region,
        profile=profile
    )
