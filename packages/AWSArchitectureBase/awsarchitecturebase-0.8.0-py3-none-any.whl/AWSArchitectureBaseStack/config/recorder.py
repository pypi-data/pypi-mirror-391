"""
AWS Config Recorder Configuration
==================================

Functions for setting up AWS Config recorder and delivery channel.
"""

from cdktf_cdktf_provider_aws.config_configuration_recorder import (
    ConfigConfigurationRecorder,
    ConfigConfigurationRecorderRecordingGroup
)
from cdktf_cdktf_provider_aws.config_delivery_channel import (
    ConfigDeliveryChannel
)
from cdktf_cdktf_provider_aws.config_configuration_recorder_status import (
    ConfigConfigurationRecorderStatus
)


def create_config_recorder(
    scope,
    recorder_name: str,
    role_arn: str,
    resource_id: str = "config_recorder",
    record_all_resources: bool = True,
    include_global_resources: bool = True
):
    """
    Create AWS Config configuration recorder.

    The recorder continuously monitors and records AWS resource configurations.

    :param scope: The CDKTF construct scope (stack instance)
    :param recorder_name: Name for the configuration recorder
    :type recorder_name: str
    :param role_arn: ARN of IAM role for Config service
    :type role_arn: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param record_all_resources: Record all supported resource types
    :type record_all_resources: bool
    :param include_global_resources: Include global resources (IAM, etc.)
    :type include_global_resources: bool
    :returns: Configuration recorder resource
    :rtype: ConfigConfigurationRecorder

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import config
        >>> 
        >>> recorder = config.create_config_recorder(
        ...     scope=self,
        ...     recorder_name="ftr-config-recorder",
        ...     role_arn="arn:aws:iam::123456789012:role/config-role"
        ... )

    .. note::
       The IAM role must have permissions to:
       - Write to S3 bucket
       - Publish to SNS topic (optional)
       - Read resource configurations
    """
    recording_group = ConfigConfigurationRecorderRecordingGroup(
        all_supported=record_all_resources,
        include_global_resource_types=include_global_resources
    )

    recorder = ConfigConfigurationRecorder(
        scope,
        resource_id,
        name=recorder_name,
        role_arn=role_arn,
        recording_group=recording_group
    )

    return recorder


def create_delivery_channel(
    scope,
    channel_name: str,
    s3_bucket_name: str,
    resource_id: str = "config_delivery_channel",
    s3_key_prefix: str = "config",
    sns_topic_arn: str = None,
    depends_on: list = None
):
    """
    Create AWS Config delivery channel for configuration snapshots.

    Delivers configuration snapshots and history to S3 bucket.

    :param scope: The CDKTF construct scope (stack instance)
    :param channel_name: Name for the delivery channel
    :type channel_name: str
    :param s3_bucket_name: S3 bucket name for storing configuration data
    :type s3_bucket_name: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param s3_key_prefix: Prefix for S3 objects (default: "config")
    :type s3_key_prefix: str
    :param sns_topic_arn: Optional SNS topic for notifications
    :type sns_topic_arn: str
    :param depends_on: List of resources this depends on
    :type depends_on: list
    :returns: Delivery channel resource
    :rtype: ConfigDeliveryChannel

    Example:
        >>> channel = config.create_delivery_channel(
        ...     scope=self,
        ...     channel_name="ftr-config-channel",
        ...     s3_bucket_name="my-config-bucket",
        ...     depends_on=[recorder]
        ... )

    .. note::
       S3 bucket must have appropriate bucket policy for Config service.
    """
    channel = ConfigDeliveryChannel(
        scope,
        resource_id,
        name=channel_name,
        s3_bucket_name=s3_bucket_name,
        s3_key_prefix=s3_key_prefix,
        sns_topic_arn=sns_topic_arn,
        depends_on=depends_on
    )

    return channel


def enable_config_recorder(
    scope,
    recorder_name: str,
    resource_id: str = "config_recorder_status",
    depends_on: list = None
):
    """
    Enable the AWS Config recorder to start recording.

    :param scope: The CDKTF construct scope (stack instance)
    :param recorder_name: Name of the configuration recorder to enable
    :type recorder_name: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param depends_on: List of resources this depends on (recorder and channel)
    :type depends_on: list
    :returns: Recorder status resource
    :rtype: ConfigConfigurationRecorderStatus

    Example:
        >>> status = config.enable_config_recorder(
        ...     scope=self,
        ...     recorder_name="ftr-config-recorder",
        ...     depends_on=[recorder, channel]
        ... )

    .. note::
       Recorder must be created and delivery channel configured before enabling.
    """
    status = ConfigConfigurationRecorderStatus(
        scope,
        resource_id,
        name=recorder_name,
        is_enabled=True,
        depends_on=depends_on
    )

    return status
