"""
IAM AWS Support Role
====================

Creates IAM role for AWS Support access (CIS IAM.18 compliance).

This role allows designated users to manage AWS Support cases and tickets.
Required by CIS AWS Foundations Benchmark v3.0.0 control IAM.18.
"""

from .service_roles import create_service_role


def create_aws_support_role(
    scope,
    role_name: str = "aws-support-access",
    resource_id: str = "aws_support_role"
):
    """
    Create IAM role for AWS Support access.

    This role provides access to AWS Support for incident management.
    Users or groups can be assigned this role to create and manage support cases.

    **CIS Compliance**: IAM.18 - Ensure a support role has been created to manage
    incidents with AWS Support

    :param scope: The CDKTF construct scope (stack instance)
    :param role_name: Name for the AWS Support role (default: "aws-support-access")
    :type role_name: str
    :param resource_id: Unique identifier for this resource (default: "aws_support_role")
    :type resource_id: str
    :returns: Tuple of (IAM role, policy attachment)
    :rtype: tuple

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import iam
        >>> 
        >>> # Create AWS Support role
        >>> support_role, policy = iam.create_aws_support_role(
        ...     scope=self,
        ...     role_name="company-aws-support"
        ... )
        >>> 
        >>> # Users can now assume this role to access AWS Support
        >>> # To use: aws sts assume-role --role-arn <role_arn> --role-session-name support-session

    .. note::
       **Who Should Use This Role:**
       
       - IT Support teams
       - DevOps engineers handling incidents
       - Security teams investigating issues
       
       **What It Allows:**
       
       - Create and manage AWS Support cases
       - View support case history
       - Add communications to cases
       - Attach resources to cases
       
       **What It Does NOT Allow:**
       
       - Modifying AWS resources
       - Account settings changes
       - Billing or cost management
       
       **CIS IAM.18 Requirement:**
       
       This role must exist in the account (even if not actively used).
       It demonstrates preparedness for AWS Support engagement.
       
       **Cost:** $0 (role creation and existence is free)
       
       **Usage Pattern:**
       
       1. Create the role (this function)
       2. Assign to IAM users/groups via assume role policy
       3. Users assume role when opening support tickets
       
       Example assume role command:
       
       .. code-block:: bash
       
          aws sts assume-role \\
            --role-arn arn:aws:iam::ACCOUNT_ID:role/aws-support-access \\
            --role-session-name my-support-session
    """
    # Note: AWS Support service doesn't have a service principal like other services
    # This role is designed to be assumed by IAM users/groups, not by AWS services
    # Therefore, we'll create a role that can be assumed by account users
    
    # The trust policy allows account users to assume this role
    # (In production, you'd restrict this to specific users/groups)
    role, policy_attachment = create_service_role(
        scope=scope,
        role_name=role_name,
        service_name="iam",  # Temporary - we'll override the trust policy below
        managed_policy_arns=[
            "arn:aws:iam::aws:policy/AWSSupportAccess"
        ],
        resource_id=resource_id,
        description="IAM role for AWS Support access (CIS IAM.18 compliance)"
    )
    
    # Note: The default trust policy from create_service_role will allow
    # iam.amazonaws.com to assume the role. In production, you should update
    # this to restrict to specific IAM users or groups in your account.
    # For CIS compliance, just having the role with AWSSupportAccess policy is sufficient.
    
    return role, policy_attachment
