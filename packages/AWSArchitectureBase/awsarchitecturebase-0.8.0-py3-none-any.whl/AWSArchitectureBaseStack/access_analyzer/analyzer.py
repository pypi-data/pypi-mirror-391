"""
AWS IAM Access Analyzer
=======================

Analyzes resource policies to identify resources shared with external entities.

CIS AWS Foundations Benchmark v3.0.0 Control 1.20:
"Ensure that IAM Access analyzer is enabled for all regions"
"""

from cdktf_cdktf_provider_aws.accessanalyzer_analyzer import AccessanalyzerAnalyzer


def create_access_analyzer(
    scope,
    analyzer_name: str,
    analyzer_type: str = "ACCOUNT",
    resource_id: str = "access_analyzer"
):
    """
    Create IAM Access Analyzer to identify unintended resource access.

    Access Analyzer continuously monitors resource policies (S3, IAM, KMS, Lambda, 
    SQS, Secrets Manager) and alerts when resources are shared outside your account 
    or organization.

    :param scope: The CDKTF construct scope (stack instance)
    :param analyzer_name: Name for the analyzer
    :type analyzer_name: str
    :param analyzer_type: Analyzer type (ACCOUNT or ORGANIZATION)
    :type analyzer_type: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: Access Analyzer resource
    :rtype: AccessanalyzerAnalyzer

    **Analyzer Types:**
    
    - `ACCOUNT`: Analyzes resources within the current AWS account (recommended)
    - `ORGANIZATION`: Analyzes resources across the entire AWS Organization

    **What Gets Analyzed:**
    
    - S3 bucket policies
    - IAM roles and their trust policies
    - KMS key policies
    - Lambda function policies
    - SQS queue policies
    - Secrets Manager secret policies
    - SNS topic policies

    **CIS v3.0.0 Requirement:**
    
    Control 1.20: "Ensure that IAM Access analyzer is enabled for all regions"
    
    This control checks whether IAM Access Analyzer is enabled in your account
    to help identify resources shared with external entities.

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import access_analyzer
        >>> 
        >>> # Enable Access Analyzer for account
        >>> analyzer = access_analyzer.create_access_analyzer(
        ...     scope=self,
        ...     analyzer_name="my-project-access-analyzer"
        ... )

    .. note::
       **Cost**: IAM Access Analyzer is FREE for account-level analyzers.
       Organization-level analyzers may have minimal costs (~$1/month).
       
       **Best Practice**: Enable in all regions where you have resources.
       
    .. warning::
       Access Analyzer findings indicate potential security risks.
       Review all findings and update policies to restrict unintended access.
    """
    analyzer = AccessanalyzerAnalyzer(
        scope,
        resource_id,
        analyzer_name=analyzer_name,
        type=analyzer_type
    )

    return analyzer
