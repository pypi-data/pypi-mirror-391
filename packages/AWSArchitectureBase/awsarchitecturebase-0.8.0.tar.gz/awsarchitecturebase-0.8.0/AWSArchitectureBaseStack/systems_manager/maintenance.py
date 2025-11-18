"""
AWS Systems Manager Maintenance Windows
========================================

Functions for creating maintenance windows and tasks.
"""

from cdktf_cdktf_provider_aws.ssm_maintenance_window import SsmMaintenanceWindow
from cdktf_cdktf_provider_aws.ssm_maintenance_window_target import (
    SsmMaintenanceWindowTarget,
    SsmMaintenanceWindowTargetTargets
)
from cdktf_cdktf_provider_aws.ssm_maintenance_window_task import (
    SsmMaintenanceWindowTask,
    SsmMaintenanceWindowTaskTaskInvocationParameters,
    SsmMaintenanceWindowTaskTaskInvocationParametersRunCommandParameters
)


def create_maintenance_window(
    scope,
    window_name: str,
    resource_id: str = "maintenance_window",
    schedule: str = "cron(0 2 ? * SUN *)",
    duration: int = 3,
    cutoff: int = 1,
    allow_unassociated_targets: bool = False,
    enabled: bool = True,
    description: str = None,
    tags: dict = None
):
    """
    Create an AWS Systems Manager maintenance window.

    Maintenance windows define when maintenance tasks can run.

    :param scope: The CDKTF construct scope (stack instance)
    :param window_name: Name for the maintenance window
    :type window_name: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param schedule: Schedule in cron format (default: Sundays at 2am UTC)
    :type schedule: str
    :param duration: Window duration in hours (default: 3)
    :type duration: int
    :param cutoff: Hours before end to stop starting new tasks (default: 1)
    :type cutoff: int
    :param allow_unassociated_targets: Allow targets not registered (default: False)
    :type allow_unassociated_targets: bool
    :param enabled: Enable the maintenance window (default: True)
    :type enabled: bool
    :param description: Description of the maintenance window
    :type description: str
    :param tags: Resource tags
    :type tags: dict
    :returns: Maintenance window resource
    :rtype: SsmMaintenanceWindow

    **Schedule Examples:**
    
    - Every Sunday 2am UTC: `cron(0 2 ? * SUN *)`
    - Every day 3am UTC: `cron(0 3 ? * * *)`
    - First Sunday of month: `cron(0 2 ? * SUN#1 *)`
    - Weekdays 10pm UTC: `cron(0 22 ? * MON-FRI *)`

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import systems_manager
        >>> 
        >>> # Weekly maintenance window on Sundays
        >>> window = systems_manager.create_maintenance_window(
        ...     scope=self,
        ...     window_name="ftr-weekly-patching",
        ...     schedule="cron(0 2 ? * SUN *)",
        ...     duration=4,
        ...     cutoff=1
        ... )

    .. note::
       **Duration**: Total window duration in hours (1-24)
       **Cutoff**: Stop starting new tasks X hours before end
       
       Example: duration=4, cutoff=1 means:
       - Window open for 4 hours
       - Stop starting new tasks after 3 hours
       - Give running tasks 1 hour to complete
    """
    window = SsmMaintenanceWindow(
        scope,
        resource_id,
        name=window_name,
        description=description or f"Maintenance window: {window_name}",
        schedule=schedule,
        duration=duration,
        cutoff=cutoff,
        allow_unassociated_targets=allow_unassociated_targets,
        enabled=enabled,
        tags=tags
    )

    return window


def create_maintenance_window_target(
    scope,
    window_id: str,
    target_key: str = "tag:PatchGroup",
    target_values: list = None,
    resource_id: str = "maintenance_window_target",
    description: str = None
):
    """
    Create a maintenance window target (instances to patch).

    Targets specify which resources the maintenance window applies to.

    :param scope: The CDKTF construct scope (stack instance)
    :param window_id: Maintenance window ID
    :type window_id: str
    :param target_key: Target key (tag key or instance IDs)
    :type target_key: str
    :param target_values: Target values (tag values or instance IDs)
    :type target_values: list
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param description: Description of the target
    :type description: str
    :returns: Maintenance window target resource
    :rtype: SsmMaintenanceWindowTarget

    **Target Types:**
    
    - Tag-based: `tag:<TagKey>` with values like `['production', 'staging']`
    - Instance IDs: `InstanceIds` with values like `['i-1234567890abcdef0']`
    - Resource groups: `ResourceGroup` with resource group name

    Example:
        >>> # Target instances tagged with PatchGroup=production
        >>> target = systems_manager.create_maintenance_window_target(
        ...     scope=self,
        ...     window_id=window.id,
        ...     target_key="tag:PatchGroup",
        ...     target_values=["production"]
        ... )
        >>> 
        >>> # Target specific instances
        >>> target = systems_manager.create_maintenance_window_target(
        ...     scope=self,
        ...     window_id=window.id,
        ...     target_key="InstanceIds",
        ...     target_values=["i-1234567890abcdef0", "i-0987654321fedcba0"]
        ... )

    .. note::
       Most common: Use tags to automatically include instances
       in maintenance windows.
    """
    if not target_values:
        target_values = ["production"]

    targets = SsmMaintenanceWindowTargetTargets(
        key=target_key,
        values=target_values
    )

    target = SsmMaintenanceWindowTarget(
        scope,
        resource_id,
        window_id=window_id,
        resource_type="INSTANCE",
        targets=[targets],
        description=description or "Maintenance window target"
    )

    return target


def create_maintenance_window_task(
    scope,
    window_id: str,
    target_id: str,
    task_arn: str = "AWS-RunPatchBaseline",
    service_role_arn: str = None,
    resource_id: str = "maintenance_window_task",
    task_type: str = "RUN_COMMAND",
    priority: int = 1,
    max_concurrency: str = "50%",
    max_errors: str = "25%",
    parameters: dict = None,
    description: str = None
):
    """
    Create a maintenance window task (what to execute).

    Tasks define the operations to perform during the maintenance window.

    :param scope: The CDKTF construct scope (stack instance)
    :param window_id: Maintenance window ID
    :type window_id: str
    :param target_id: Maintenance window target ID
    :type target_id: str
    :param task_arn: SSM document ARN or name (default: AWS-RunPatchBaseline)
    :type task_arn: str
    :param service_role_arn: IAM role ARN for task execution
    :type service_role_arn: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param task_type: Task type (default: RUN_COMMAND)
    :type task_type: str
    :param priority: Task priority, lower = higher priority (default: 1)
    :type priority: int
    :param max_concurrency: Max concurrent executions (default: 50%)
    :type max_concurrency: str
    :param max_errors: Max errors before stopping (default: 25%)
    :type max_errors: str
    :param parameters: Task parameters
    :type parameters: dict
    :param description: Description of the task
    :type description: str
    :returns: Maintenance window task resource
    :rtype: SsmMaintenanceWindowTask

    **Common SSM Documents:**
    
    - `AWS-RunPatchBaseline`: Install patches
    - `AWS-UpdateSSMAgent`: Update SSM agent
    - `AWS-ConfigureAWSPackage`: Install/uninstall packages
    - `AWS-RunShellScript`: Run custom shell scripts
    - `AWS-RunPowerShellScript`: Run PowerShell scripts

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import systems_manager
        >>> 
        >>> # Patch baseline installation task
        >>> task = systems_manager.create_maintenance_window_task(
        ...     scope=self,
        ...     window_id=window.id,
        ...     target_id=target.id,
        ...     task_arn="AWS-RunPatchBaseline",
        ...     service_role_arn=role.arn,
        ...     parameters={'Operation': ['Install']}
        ... )

    .. note::
       **Max Concurrency**: 
       - Percentage: "50%" = run on 50% of targets at once
       - Absolute: "10" = run on 10 instances at once
       
       **Max Errors**:
       - Percentage: "25%" = stop if 25% fail
       - Absolute: "5" = stop if 5 instances fail
    """
    # Build task invocation parameters only if parameters are provided
    task_invocation = None
    if parameters:
        run_command_params = SsmMaintenanceWindowTaskTaskInvocationParametersRunCommandParameters(
            parameter=parameters
        )
        task_invocation = SsmMaintenanceWindowTaskTaskInvocationParameters(
            run_command_parameters=run_command_params
        )

    # Create maintenance window task
    task = SsmMaintenanceWindowTask(
        scope,
        resource_id,
        window_id=window_id,
        task_arn=task_arn,
        task_type=task_type,
        service_role_arn=service_role_arn,
        targets=[{"key": "WindowTargetIds", "values": [target_id]}],
        priority=priority,
        max_concurrency=max_concurrency,
        max_errors=max_errors,
        task_invocation_parameters=task_invocation,
        description=description or f"Maintenance task: {task_arn}"
    )

    return task
