"""
Security Hub Resources Orchestration
====================================

High-level orchestration for creating complete Security Hub configuration.
"""

from . import account
from . import standards as standards_module


def create_security_hub_resources(
    scope,
    region: str,
    enable_standards: bool = True,
    standards: list = None,
    enable_default_standards: bool = True,
    auto_enable_controls: bool = True
):
    """
    Create complete Security Hub infrastructure with configurable FTR compliance settings.

    This orchestration function enables Security Hub and configures
    compliance standards based on your organization's requirements.

    :param scope: The CDKTF construct scope (stack instance)
    :param region: AWS region
    :type region: str
    :param enable_standards: Whether to enable compliance standards
    :type enable_standards: bool
    :param standards: List of standard ARNs or paths to enable (e.g., ['aws-foundational-security-best-practices/v/1.0.0'])
                     If None, uses default FTR standards (FSBP, CIS v1.4.0, PCI DSS)
    :type standards: list
    :param enable_default_standards: Enable AWS Foundational Security Best Practices in account settings
    :type enable_default_standards: bool
    :param auto_enable_controls: Automatically enable new controls as they're released
    :type auto_enable_controls: bool
    :returns: Dictionary with Security Hub resources
    :rtype: dict

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import security_hub
        >>> 
        >>> # Default FTR compliance (FSBP + CIS v1.4.0 + PCI DSS)
        >>> resources = security_hub.create_security_hub_resources(
        ...     scope=self,
        ...     region="us-east-1"
        ... )
        >>> 
        >>> # Specific standards
        >>> resources = security_hub.create_security_hub_resources(
        ...     scope=self,
        ...     region="us-east-1",
        ...     standards=[
        ...         'aws-foundational-security-best-practices/v/1.0.0',
        ...         'cis-aws-foundations-benchmark/v/1.4.0'
        ...     ]
        ... )
        >>> 
        >>> # Use newer versions as they become available
        >>> resources = security_hub.create_security_hub_resources(
        ...     scope=self,
        ...     region="us-east-1",
        ...     standards=[
        ...         'aws-foundational-security-best-practices/v/2.0.0',  # Future version
        ...         'nist-800-53/v/5.0.0'
        ...     ]
        ... )

    .. note::
       **Default Standards:**
       - AWS Foundational Security Best Practices v1.0.0
       - CIS AWS Foundations Benchmark v1.4.0
       - PCI DSS v3.2.1
       
       Pass custom `standards` list to override defaults.
       Find available standards: `aws securityhub describe-standards --region <region>`
    """
    resources = {}

    # 1. Enable Security Hub account
    resources['account'] = account.enable_security_hub_account(
        scope=scope,
        resource_id="security_hub_account",
        enable_default_standards=enable_default_standards,
        control_finding_generator="SECURITY_CONTROL",
        auto_enable_controls=auto_enable_controls
    )

    # 2. Enable compliance standards
    if enable_standards:
        resources['standards'] = standards_module.enable_ftr_compliance_standards(
            scope=scope,
            region=region,
            standards=standards
        )

    return resources
