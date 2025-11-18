"""
AWS Systems Manager Patch Management
=====================================

Functions for creating patch baselines and patch groups.
"""

from cdktf_cdktf_provider_aws.ssm_patch_baseline import (
    SsmPatchBaseline,
    SsmPatchBaselineApprovalRule,
    SsmPatchBaselineApprovalRulePatchFilter
)
from cdktf_cdktf_provider_aws.ssm_patch_group import SsmPatchGroup


def create_patch_baseline(
    scope,
    baseline_name: str,
    operating_system: str = "AMAZON_LINUX_2",
    resource_id: str = "patch_baseline",
    approved_patches: list = None,
    rejected_patches: list = None,
    approval_rules: list = None,
    description: str = None,
    tags: dict = None
):
    """
    Create an AWS Systems Manager patch baseline.

    A patch baseline defines which patches are approved for installation.

    :param scope: The CDKTF construct scope (stack instance)
    :param baseline_name: Name for the patch baseline
    :type baseline_name: str
    :param operating_system: Operating system (default: AMAZON_LINUX_2)
    :type operating_system: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param approved_patches: List of explicitly approved patches (KB IDs)
    :type approved_patches: list
    :param rejected_patches: List of explicitly rejected patches (KB IDs)
    :type rejected_patches: list
    :param approval_rules: List of approval rule configurations
    :type approval_rules: list of dict
    :param description: Description of the patch baseline
    :type description: str
    :param tags: Resource tags
    :type tags: dict
    :returns: Patch baseline resource
    :rtype: SsmPatchBaseline

    **Supported Operating Systems:**
    
    - AMAZON_LINUX_2
    - AMAZON_LINUX_2022
    - UBUNTU
    - REDHAT_ENTERPRISE_LINUX
    - SUSE
    - CENTOS
    - ORACLE_LINUX
    - DEBIAN
    - WINDOWS

    **Approval Rule Format:**
    
    .. code-block:: python
    
        {
            'approve_after_days': 7,           # Days after release
            'compliance_level': 'CRITICAL',    # CRITICAL, HIGH, MEDIUM, LOW
            'enable_non_security': False,      # Include non-security updates
            'patch_filters': [
                {
                    'key': 'CLASSIFICATION',
                    'values': ['Security', 'Bugfix']
                },
                {
                    'key': 'SEVERITY',
                    'values': ['Critical', 'Important']
                }
            ]
        }

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import systems_manager
        >>> 
        >>> # Auto-approve critical security patches after 7 days
        >>> baseline = systems_manager.create_patch_baseline(
        ...     scope=self,
        ...     baseline_name="ftr-security-patches",
        ...     operating_system="AMAZON_LINUX_2",
        ...     approval_rules=[{
        ...         'approve_after_days': 7,
        ...         'compliance_level': 'CRITICAL',
        ...         'patch_filters': [
        ...             {'key': 'CLASSIFICATION', 'values': ['Security']},
        ...             {'key': 'SEVERITY', 'values': ['Critical', 'Important']}
        ...         ]
        ...     }]
        ... )

    .. note::
       **Default Baselines**: AWS provides default baselines for each OS.
       Create custom baselines for specific compliance requirements.
       
       **Patch Filters**:
       - CLASSIFICATION: Security, Bugfix, Enhancement, Recommended
       - SEVERITY: Critical, Important, Medium, Low
       - PRODUCT: Specific products/packages
    """
    # Build approval rules
    approval_rule_objects = None
    if approval_rules:
        approval_rule_objects = []
        for rule in approval_rules:
            # Build patch filters
            filter_objects = []
            for pf in rule.get('patch_filters', []):
                filter_objects.append(
                    SsmPatchBaselineApprovalRulePatchFilter(
                        key=pf['key'],
                        values=pf['values']
                    )
                )
            
            approval_rule_objects.append(
                SsmPatchBaselineApprovalRule(
                    approve_after_days=rule.get('approve_after_days', 7),
                    compliance_level=rule.get('compliance_level', 'UNSPECIFIED'),
                    enable_non_security=rule.get('enable_non_security', False),
                    patch_filter=filter_objects
                )
            )

    # Create patch baseline
    baseline = SsmPatchBaseline(
        scope,
        resource_id,
        name=baseline_name,
        description=description or f"Patch baseline: {baseline_name}",
        operating_system=operating_system,
        approved_patches=approved_patches,
        rejected_patches=rejected_patches,
        approval_rule=approval_rule_objects,
        tags=tags
    )

    return baseline


def create_patch_group(
    scope,
    patch_group_name: str,
    baseline_id: str,
    resource_id: str = "patch_group"
):
    """
    Create a patch group and associate it with a patch baseline.

    Patch groups allow you to organize instances for patching.

    :param scope: The CDKTF construct scope (stack instance)
    :param patch_group_name: Name for the patch group
    :type patch_group_name: str
    :param baseline_id: Patch baseline ID to associate
    :type baseline_id: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: Patch group resource
    :rtype: SsmPatchGroup

    Example:
        >>> # Associate instances tagged with PatchGroup=production
        >>> patch_group = systems_manager.create_patch_group(
        ...     scope=self,
        ...     patch_group_name="production",
        ...     baseline_id=baseline.id
        ... )

    .. note::
       **How to Use**:
       1. Create patch baseline
       2. Create patch group
       3. Tag EC2 instances with `Patch Group=<patch_group_name>`
       4. Instances automatically use the associated baseline
    """
    patch_group = SsmPatchGroup(
        scope,
        resource_id,
        baseline_id=baseline_id,
        patch_group=patch_group_name
    )

    return patch_group
