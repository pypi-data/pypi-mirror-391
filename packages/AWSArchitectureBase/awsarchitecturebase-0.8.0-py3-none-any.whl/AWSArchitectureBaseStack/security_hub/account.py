"""
Security Hub Account Configuration
==================================

Functions for enabling and configuring AWS Security Hub at the account level.
"""

from cdktf_cdktf_provider_aws.securityhub_account import SecurityhubAccount


def enable_security_hub_account(
    scope,
    resource_id: str = "security_hub_account",
    enable_default_standards: bool = True,
    control_finding_generator: str = "SECURITY_CONTROL",
    auto_enable_controls: bool = True
):
    """
    Enable AWS Security Hub for the account.

    Creates the Security Hub account configuration with recommended settings
    for FTR compliance monitoring.

    :param scope: The CDKTF construct scope (stack instance)
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param enable_default_standards: Enable AWS Foundational Security Best Practices
    :type enable_default_standards: bool
    :param control_finding_generator: Finding generation method
    :type control_finding_generator: str
    :param auto_enable_controls: Automatically enable new controls
    :type auto_enable_controls: bool
    :returns: Security Hub account resource
    :rtype: SecurityhubAccount

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import security_hub
        >>> 
        >>> hub = security_hub.enable_security_hub_account(
        ...     scope=self,
        ...     enable_default_standards=True,
        ...     auto_enable_controls=True
        ... )

    .. note::
       Security Hub charges apply. See AWS pricing for details.
       control_finding_generator options: "SECURITY_CONTROL" or "STANDARD_CONTROL"
    """
    security_hub = SecurityhubAccount(
        scope,
        resource_id,
        enable_default_standards=enable_default_standards,
        control_finding_generator=control_finding_generator,
        auto_enable_controls=auto_enable_controls,
    )

    return security_hub
