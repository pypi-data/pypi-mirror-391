"""
Security Hub Standards Configuration
====================================

Functions for enabling and managing compliance standards in Security Hub.
"""

from cdktf_cdktf_provider_aws.securityhub_standards_subscription import (
    SecurityhubStandardsSubscription
)


def enable_security_standards(
    scope,
    standards_arn: str,
    resource_id: str = None,
):
    """
    Enable a compliance standard in Security Hub.

    Activates specific compliance frameworks for continuous assessment.

    :param scope: The CDKTF construct scope (stack instance)
    :param standards_arn: ARN of the security standard to enable
    :type standards_arn: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: Standards subscription resource
    :rtype: SecurityhubStandardsSubscription

    Available Standards ARNs:
        - AWS Foundational Security Best Practices v1.0.0:
          arn:aws:securityhub:{region}::standards/aws-foundational-security-best-practices/v/1.0.0
        
        - CIS AWS Foundations Benchmark v1.2.0:
          arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0
        
        - PCI DSS v3.2.1:
          arn:aws:securityhub:{region}::standards/pci-dss/v/3.2.1
        
        - CIS AWS Foundations Benchmark v1.4.0:
          arn:aws:securityhub:{region}::standards/cis-aws-foundations-benchmark/v/1.4.0

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import security_hub
        >>> 
        >>> # Enable AWS Foundational Security Best Practices
        >>> standard = security_hub.enable_security_standards(
        ...     scope=self,
        ...     standards_arn="arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0",
        ...     resource_id="fsbp_standard"
        ... )

    .. note::
       Each standard enabled incurs additional Security Hub charges.
       For FTR compliance, typically enable: FSBP, CIS, and PCI-DSS.
    """
    if not resource_id:
        # Extract standard name from ARN for resource ID
        standard_name = standards_arn.split("/")[-2]
        resource_id = f"standard_{standard_name.replace('-', '_')}"

    standard = SecurityhubStandardsSubscription(
        scope,
        resource_id,
        standards_arn=standards_arn,
    )

    return standard


def get_standard_arn(region: str, standard_name: str) -> str:
    """
    Build a Security Hub standard ARN from a standard name.
    
    :param region: AWS region
    :param standard_name: Standard name (e.g., 'aws-foundational-security-best-practices/v/1.0.0')
    :returns: Full ARN for the standard
    :rtype: str
    
    Example:
        >>> arn = get_standard_arn('us-east-1', 'aws-foundational-security-best-practices/v/1.0.0')
        >>> # Returns: arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0
    """
    return f"arn:aws:securityhub:{region}::standards/{standard_name}"


def enable_ftr_compliance_standards(
    scope, 
    region: str,
    standards: list = None
):
    """
    Enable compliance standards for FTR compliance.

    Activates compliance standards based on your organization's requirements.
    By default, enables FSBP v1.0.0, CIS v1.4.0, and PCI DSS v3.2.1 for
    comprehensive FTR compliance.

    :param scope: The CDKTF construct scope (stack instance)
    :param region: AWS region
    :type region: str
    :param standards: List of standard ARNs or standard paths to enable.
                     Can be full ARNs or just the path portion (e.g., 'aws-foundational-security-best-practices/v/1.0.0')
                     If None, uses default FTR standards.
    :type standards: list
    :returns: Dictionary of enabled standards
    :rtype: dict

    **Common Standards (pass as strings):**
    
    - `'aws-foundational-security-best-practices/v/1.0.0'` - AWS FSBP
    - `'cis-aws-foundations-benchmark/v/1.2.0'` - CIS Benchmark v1.2.0
    - `'cis-aws-foundations-benchmark/v/1.4.0'` - CIS Benchmark v1.4.0
    - `'pci-dss/v/3.2.1'` - PCI DSS v3.2.1
    - `'nist-800-53/v/5.0.0'` - NIST 800-53 v5.0.0

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import security_hub
        >>> 
        >>> # Enable default FTR standards (FSBP + CIS v1.4.0 + PCI DSS)
        >>> standards = security_hub.enable_ftr_compliance_standards(
        ...     scope=self,
        ...     region="us-east-1"
        ... )
        >>> 
        >>> # Enable specific standards by path
        >>> standards = security_hub.enable_ftr_compliance_standards(
        ...     scope=self,
        ...     region="us-east-1",
        ...     standards=[
        ...         'aws-foundational-security-best-practices/v/1.0.0',
        ...         'cis-aws-foundations-benchmark/v/1.4.0'
        ...     ]
        ... )
        >>> 
        >>> # Or use full ARNs
        >>> standards = security_hub.enable_ftr_compliance_standards(
        ...     scope=self,
        ...     region="us-east-1",
        ...     standards=[
        ...         'arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0',
        ...         'arn:aws:securityhub:us-east-1::standards/nist-800-53/v/5.0.0'
        ...     ]
        ... )

    .. note::
       **Standard Selection Guide:**
       
       - **FSBP**: Always recommended. AWS's baseline security checks.
       - **CIS**: Industry standard, often required by auditors and SOC 2.
       - **PCI DSS**: REQUIRED if you process, store, or transmit payment card data.
       - **NIST 800-53**: Required for US federal government compliance.
       
       **Cost**: Each standard costs ~$0.40-0.70/month per account.
       
       To find available standards, use AWS CLI:
       `aws securityhub describe-standards --region us-east-1`
    """
    enabled_standards = {}
    
    # Default FTR compliance standards
    if standards is None:
        standards = [
            'aws-foundational-security-best-practices/v/1.0.0',
            'cis-aws-foundations-benchmark/v/1.4.0',
            'pci-dss/v/3.2.1'
        ]
    
    # Enable each requested standard
    for idx, standard in enumerate(standards):
        # If it's already a full ARN, use it; otherwise build the ARN
        if standard.startswith('arn:aws:securityhub:'):
            standard_arn = standard
            # Extract standard name from ARN for resource ID
            standard_path = standard.split('::standards/')[-1]
        else:
            standard_arn = get_standard_arn(region, standard)
            standard_path = standard
        
        # Create a clean resource ID from the standard path
        # Remove slashes and special chars, replace with underscores
        resource_id = f"standard_{standard_path.replace('/', '_').replace('-', '_').replace('.', '_')}"
        
        enabled_standards[standard_path] = enable_security_standards(
            scope=scope,
            standards_arn=standard_arn,
            resource_id=resource_id
        )
    
    return enabled_standards
