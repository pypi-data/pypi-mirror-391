"""
AWS Inspector Resources Orchestration
======================================

High-level functions for creating complete AWS Inspector setup.
"""

from . import enablement


def create_inspector_resources(
    scope,
    account_id: str,
    enable_scanning: bool = False,
    enable_ec2: bool = True,
    enable_ecr: bool = True,
    enable_lambda: bool = True,
    enable_lambda_code: bool = False
):
    """
    Create complete AWS Inspector v2 setup with automated vulnerability scanning.

    This orchestration function enables Inspector v2 scanning for:
    - EC2 instances
    - ECR container images
    - Lambda functions
    - Lambda application code (optional)

    :param scope: The CDKTF construct scope (stack instance)
    :param account_id: AWS account ID to enable Inspector for
    :type account_id: str
    :param enable_scanning: Enable Inspector scanning (default: False)
    :type enable_scanning: bool
    :param enable_ec2: Enable EC2 instance scanning (default: True)
    :type enable_ec2: bool
    :param enable_ecr: Enable ECR container image scanning (default: True)
    :type enable_ecr: bool
    :param enable_lambda: Enable Lambda function scanning (default: True)
    :type enable_lambda: bool
    :param enable_lambda_code: Enable Lambda code scanning (default: False)
    :type enable_lambda_code: bool
    :returns: Dictionary with created resources or None if not enabled
    :rtype: dict or None

    **Resource Dictionary Keys:**
    
    - `enabler`: Inspector v2 enabler resource

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import inspector
        >>> 
        >>> # Enable Inspector with default scanning (EC2, ECR, Lambda)
        >>> resources = inspector.create_inspector_resources(
        ...     scope=self,
        ...     enable_scanning=True
        ... )
        >>> 
        >>> # Enable only EC2 and ECR scanning
        >>> resources = inspector.create_inspector_resources(
        ...     scope=self,
        ...     enable_scanning=True,
        ...     enable_ec2=True,
        ...     enable_ecr=True,
        ...     enable_lambda=False
        ... )
        >>> 
        >>> # Enable all scanning including Lambda code
        >>> resources = inspector.create_inspector_resources(
        ...     scope=self,
        ...     enable_scanning=True,
        ...     enable_ec2=True,
        ...     enable_ecr=True,
        ...     enable_lambda=True,
        ...     enable_lambda_code=True
        ... )

    .. note::
       **Cost Estimates:**
       
       - **Infrastructure only** (enable_scanning=False): $0.00/month
       - **Active scanning**: Varies by resource count
         - EC2: $0.125/instance/month
         - ECR: First 30-day rescan free, then $0.09/image/month
         - Lambda: $0.01/function/month
         - Lambda Code: $0.30/100,000 lines scanned/month
       
       **Example**: 10 EC2 + 20 ECR images + 50 Lambda = ~$3/month
       
       **Safe Defaults:**
       
       - enable_scanning=False: Inspector not enabled, no costs
       - When enabled: EC2, ECR, and Lambda scanning by default
       - Lambda code scanning disabled by default (additional cost)
       
       **Automatic Features:**
       
       - **Auto-discovery**: Inspector automatically finds resources
       - **Continuous scanning**: Resources scanned continuously
       - **Security Hub**: Findings sent to Security Hub automatically
       - **CVE database**: Updated daily with latest vulnerabilities
       
       **To Enable Scanning:**
       
       1. Set enable_scanning=True in configuration
       2. Inspector will automatically discover and scan resources
       3. View findings in Inspector console or Security Hub
       
       **Findings Severity:**
       
       - Critical: CVSS 9.0-10.0
       - High: CVSS 7.0-8.9
       - Medium: CVSS 4.0-6.9
       - Low: CVSS 0.1-3.9
       - Informational: CVSS 0.0
    """
    resources_dict = {}

    # Only enable Inspector if scanning is enabled
    if not enable_scanning:
        return None

    # Enable Inspector v2
    inspector_enabler = enablement.enable_inspector(
        scope=scope,
        account_id=account_id,
        enable_ec2=enable_ec2,
        enable_ecr=enable_ecr,
        enable_lambda=enable_lambda,
        enable_lambda_code=enable_lambda_code
    )
    resources_dict['enabler'] = inspector_enabler

    return resources_dict
