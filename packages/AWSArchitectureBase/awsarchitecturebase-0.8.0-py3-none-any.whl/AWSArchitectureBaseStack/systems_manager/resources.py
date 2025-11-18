"""
AWS Systems Manager Resources Orchestration
============================================

High-level functions for creating complete Systems Manager setup.
"""

from . import patch, maintenance, iam_role


def create_systems_manager_resources(
    scope,
    project_name: str,
    enable_patching: bool = False,
    operating_system: str = "AMAZON_LINUX_2",
    patch_baseline_name: str = None,
    patch_group_name: str = None,
    maintenance_window_name: str = None,
    maintenance_schedule: str = "cron(0 2 ? * SUN *)",
    maintenance_duration: int = 3,
    maintenance_cutoff: int = 1,
    role_name: str = None,
    approval_rules: list = None,
    patch_targets: list = None,
    tags: dict = None
):
    """
    Create complete AWS Systems Manager setup with patch management.

    This orchestration function sets up:
    - Patch baseline with approval rules
    - Patch group for organizing instances
    - IAM role for maintenance windows
    - Maintenance window with schedule
    - Maintenance window targets (instances to patch)
    - Maintenance window task (patch installation)

    :param scope: The CDKTF construct scope (stack instance)
    :param project_name: Project name for resource naming
    :type project_name: str
    :param enable_patching: Enable automated patching (default: False)
    :type enable_patching: bool
    :param operating_system: OS for patch baseline (default: AMAZON_LINUX_2)
    :type operating_system: str
    :param patch_baseline_name: Patch baseline name (default: {project}-patch-baseline)
    :type patch_baseline_name: str
    :param patch_group_name: Patch group name (default: {project}-patch-group)
    :type patch_group_name: str
    :param maintenance_window_name: Maintenance window name (default: {project}-maintenance)
    :type maintenance_window_name: str
    :param maintenance_schedule: Maintenance schedule (default: Sundays 2am UTC)
    :type maintenance_schedule: str
    :param maintenance_duration: Maintenance duration in hours (default: 3)
    :type maintenance_duration: int
    :param maintenance_cutoff: Cutoff hours before end (default: 1)
    :type maintenance_cutoff: int
    :param role_name: IAM role name (default: {project}-ssm-maintenance-role)
    :type role_name: str
    :param approval_rules: Patch approval rules (default: FTR compliance rules)
    :type approval_rules: list of dict
    :param patch_targets: Target instances (default: tag:PatchGroup=[patch_group_name])
    :type patch_targets: list of dict [{'key': 'tag:PatchGroup', 'values': ['production']}]
    :param tags: Resource tags
    :type tags: dict
    :returns: Dictionary with created resources or None if not enabled
    :rtype: dict or None

    **Resource Dictionary Keys:**
    
    - `patch_baseline`: Patch baseline
    - `patch_group`: Patch group
    - `iam_role`: IAM role for maintenance
    - `iam_policy`: IAM policy attachment
    - `maintenance_window`: Maintenance window (if enable_patching=True)
    - `maintenance_target`: Maintenance target (if enable_patching=True)
    - `maintenance_task`: Maintenance task (if enable_patching=True)

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import systems_manager
        >>> 
        >>> # Infrastructure only (safe for testing)
        >>> resources = systems_manager.create_systems_manager_resources(
        ...     scope=self,
        ...     project_name="my-app"
        ... )
        >>> 
        >>> # Active patching with default FTR compliance rules
        >>> resources = systems_manager.create_systems_manager_resources(
        ...     scope=self,
        ...     project_name="my-app",
        ...     enable_patching=True,
        ...     maintenance_schedule="cron(0 2 ? * SUN *)",  # Sundays 2am
        ...     patch_targets=[{
        ...         'key': 'tag:Environment',
        ...         'values': ['production']
        ...     }]
        ... )
        >>> 
        >>> # Custom approval rules
        >>> resources = systems_manager.create_systems_manager_resources(
        ...     scope=self,
        ...     project_name="ftr-app",
        ...     enable_patching=True,
        ...     approval_rules=[{
        ...         'approve_after_days': 3,
        ...         'compliance_level': 'CRITICAL',
        ...         'patch_filters': [
        ...             {'key': 'CLASSIFICATION', 'values': ['Security']},
        ...             {'key': 'SEVERITY', 'values': ['Critical', 'Important']}
        ...         ]
        ...     }]
        ... )

    .. note::
       **Cost Estimates:**
       
       - Infrastructure only: $0.00/month (baseline and groups free)
       - Active patching: $0.00/month (patching itself is free)
       - CloudWatch logs: ~$0.50/GB (patch execution logs)
       
       **Safe Defaults:**
       
       - enable_patching=False: Creates baseline/group but no maintenance windows
       - Default schedule: Sundays at 2am UTC
       - Default approval: Critical security patches after 7 days
       
       **How It Works:**
       
       1. Patch baseline defines which patches are approved
       2. Patch group associates baseline with instances
       3. Tag instances with `Patch Group=<patch_group_name>`
       4. Maintenance window runs weekly to install patches
       5. Patches installed according to approval rules
       
       **To Enable Patching:**
       
       1. Set enable_patching=True
       2. Tag instances with appropriate tags (default: PatchGroup=<patch_group_name>)
       3. Ensure instances have SSM agent and proper IAM role
       4. Patches will install during maintenance window
       
       **Instance Requirements:**
       
       - SSM agent installed and running
       - IAM instance profile with AmazonSSMManagedInstanceCore policy
       - Network access to Systems Manager endpoints
       - Proper tags for targeting
    """
    resources_dict = {}

    # Set default names
    if not patch_baseline_name:
        patch_baseline_name = f"{project_name}-patch-baseline"
    if not patch_group_name:
        patch_group_name = f"{project_name}-patch-group"
    if not maintenance_window_name:
        maintenance_window_name = f"{project_name}-maintenance"
    if not role_name:
        role_name = f"{project_name}-ssm-maintenance-role"

    # Merge tags
    resource_tags = tags or {}
    if 'Project' not in resource_tags:
        resource_tags['Project'] = project_name
    if 'ManagedBy' not in resource_tags:
        resource_tags['ManagedBy'] = 'AWS Systems Manager'

    # Default FTR compliance approval rules
    if not approval_rules:
        approval_rules = [{
            'approve_after_days': 7,
            'compliance_level': 'CRITICAL',
            'enable_non_security': False,
            'patch_filters': [
                {'key': 'CLASSIFICATION', 'values': ['Security', 'Bugfix']},
                {'key': 'SEVERITY', 'values': ['Critical', 'Important']}
            ]
        }]

    # Create patch baseline
    patch_baseline = patch.create_patch_baseline(
        scope=scope,
        baseline_name=patch_baseline_name,
        operating_system=operating_system,
        approval_rules=approval_rules,
        description=f"FTR compliance patch baseline for {project_name}",
        tags=resource_tags
    )
    resources_dict['patch_baseline'] = patch_baseline

    # Create patch group
    patch_group = patch.create_patch_group(
        scope=scope,
        patch_group_name=patch_group_name,
        baseline_id=patch_baseline.id
    )
    resources_dict['patch_group'] = patch_group

    # Create IAM role for maintenance windows
    ssm_role, ssm_policy = iam_role.create_ssm_maintenance_iam_role(
        scope=scope,
        role_name=role_name
    )
    resources_dict['iam_role'] = ssm_role
    resources_dict['iam_policy'] = ssm_policy

    # Only create maintenance window if patching is enabled
    if not enable_patching:
        return resources_dict

    # Create maintenance window
    maint_window = maintenance.create_maintenance_window(
        scope=scope,
        window_name=maintenance_window_name,
        schedule=maintenance_schedule,
        duration=maintenance_duration,
        cutoff=maintenance_cutoff,
        enabled=True,
        description=f"Automated patching window for {project_name}",
        tags=resource_tags
    )
    resources_dict['maintenance_window'] = maint_window

    # Default patch targets
    if not patch_targets:
        patch_targets = [{'key': 'tag:PatchGroup', 'values': [patch_group_name]}]

    # Create maintenance window target
    target_key = patch_targets[0].get('key', 'tag:PatchGroup')
    target_values = patch_targets[0].get('values', [patch_group_name])
    
    maint_target = maintenance.create_maintenance_window_target(
        scope=scope,
        window_id=maint_window.id,
        target_key=target_key,
        target_values=target_values,
        description=f"Patch targets for {project_name}"
    )
    resources_dict['maintenance_target'] = maint_target

    # Create maintenance window task (install patches using AWS default operation)
    maint_task = maintenance.create_maintenance_window_task(
        scope=scope,
        window_id=maint_window.id,
        target_id=maint_target.id,
        task_arn="AWS-RunPatchBaseline",
        service_role_arn=ssm_role.arn,
        parameters=None,  # Use AWS default operation
        max_concurrency="50%",
        max_errors="25%",
        description=f"Install patches for {project_name}"
    )
    resources_dict['maintenance_task'] = maint_task

    return resources_dict
