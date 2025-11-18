"""
AWS Inspector Enablement Configuration
=======================================

Functions for enabling AWS Inspector v2 vulnerability scanning.
"""

from cdktf_cdktf_provider_aws.inspector2_enabler import Inspector2Enabler


def enable_inspector(
    scope,
    account_id: str,
    resource_id: str = "inspector_enabler",
    enable_ec2: bool = True,
    enable_ecr: bool = True,
    enable_lambda: bool = True,
    enable_lambda_code: bool = False
):
    """
    Enable AWS Inspector v2 for automated vulnerability scanning.

    Inspector v2 automatically discovers and continuously scans resources
    for software vulnerabilities and network exposure.

    :param scope: The CDKTF construct scope (stack instance)
    :param account_id: AWS account ID to enable Inspector for
    :type account_id: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param enable_ec2: Enable EC2 instance scanning (default: True)
    :type enable_ec2: bool
    :param enable_ecr: Enable ECR container image scanning (default: True)
    :type enable_ecr: bool
    :param enable_lambda: Enable Lambda function scanning (default: True)
    :type enable_lambda: bool
    :param enable_lambda_code: Enable Lambda code scanning (default: False)
    :type enable_lambda_code: bool
    :returns: Inspector enabler resource
    :rtype: Inspector2Enabler

    **Scan Types:**
    
    - **EC2**: Scans instances for CVEs in OS and application packages
    - **ECR**: Scans container images for vulnerabilities
    - **Lambda**: Scans Lambda function packages and layers
    - **Lambda Code**: Scans application code for vulnerabilities (additional cost)

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import inspector
        >>> 
        >>> # Enable all scanning types
        >>> enabler = inspector.enable_inspector(
        ...     scope=self,
        ...     enable_ec2=True,
        ...     enable_ecr=True,
        ...     enable_lambda=True
        ... )
        >>> 
        >>> # Enable only EC2 and ECR scanning
        >>> enabler = inspector.enable_inspector(
        ...     scope=self,
        ...     enable_ec2=True,
        ...     enable_ecr=True,
        ...     enable_lambda=False
        ... )

    .. note::
       **Automatic Discovery**: Inspector v2 automatically discovers and scans
       resources. No need to manually specify targets.
       
       **Cost**: 
       - EC2: $0.125/instance/month
       - ECR: First 30-day rescan free, then $0.09/image/month
       - Lambda: $0.01/function/month
       - Lambda Code: $0.30/100,000 lines of code scanned/month
       
       **Security Hub Integration**: Findings automatically sent to Security Hub
       if enabled in your account.
       
       **Scan Frequency**:
       - EC2: Continuous monitoring, daily scans
       - ECR: On push and continuous rescanning
       - Lambda: On deployment and continuous rescanning
    """
    # Build resource types list
    resource_types = []
    if enable_ec2:
        resource_types.append("EC2")
    if enable_ecr:
        resource_types.append("ECR")
    if enable_lambda:
        resource_types.append("LAMBDA")
    if enable_lambda_code:
        resource_types.append("LAMBDA_CODE")

    # Enable Inspector v2
    enabler = Inspector2Enabler(
        scope,
        resource_id,
        account_ids=[account_id],  # Current AWS account ID
        resource_types=resource_types
    )

    return enabler
