"""
AWS SNS Topics Configuration
==============================

Functions for creating and configuring SNS topics for compliance notifications.
"""

from cdktf_cdktf_provider_aws.sns_topic import SnsTopic
from cdktf_cdktf_provider_aws.sns_topic_policy import SnsTopicPolicy
import json


def create_sns_topic(
    scope,
    topic_name: str,
    resource_id: str = "sns_topic",
    display_name: str = None,
    enable_encryption: bool = True,
    kms_master_key_id: str = None,
    delivery_policy: dict = None,
    tags: dict = None
):
    """
    Create an SNS topic for compliance notifications.

    SNS topics receive compliance findings from Security Hub, Config, CloudWatch, etc.

    :param scope: The CDKTF construct scope (stack instance)
    :param topic_name: Name for the SNS topic
    :type topic_name: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param display_name: Display name for email subscriptions
    :type display_name: str
    :param enable_encryption: Enable server-side encryption (default: True)
    :type enable_encryption: bool
    :param kms_master_key_id: KMS key ID for encryption (default: AWS managed key)
    :type kms_master_key_id: str
    :param delivery_policy: Delivery retry policy configuration
    :type delivery_policy: dict
    :param tags: Resource tags
    :type tags: dict
    :returns: SNS Topic resource
    :rtype: SnsTopic

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import notifications
        >>> 
        >>> # Basic SNS topic
        >>> topic = notifications.create_sns_topic(
        ...     scope=self,
        ...     topic_name="ftr-compliance-alerts",
        ...     display_name="FTR Compliance Alerts"
        ... )
        >>> 
        >>> # SNS topic with custom KMS encryption
        >>> topic = notifications.create_sns_topic(
        ...     scope=self,
        ...     topic_name="ftr-compliance-alerts",
        ...     display_name="FTR Compliance Alerts",
        ...     kms_master_key_id=kms_key.id
        ... )
        >>> 
        >>> # SNS topic with delivery policy
        >>> topic = notifications.create_sns_topic(
        ...     scope=self,
        ...     topic_name="ftr-compliance-alerts",
        ...     delivery_policy={
        ...         'http': {
        ...             'defaultHealthyRetryPolicy': {
        ...                 'minDelayTarget': 20,
        ...                 'maxDelayTarget': 20,
        ...                 'numRetries': 3
        ...             }
        ...         }
        ...     }
        ... )

    .. note::
       **Cost Estimates**:
       - Email/Email-JSON: First 1,000 free, then $2 per 100,000 notifications
       - SMS: $0.00645 per message (US)
       - Mobile push: First 1 million free, then $0.50 per million
       - HTTP/HTTPS: $0.60 per million notifications
       
       **Encryption**:
       - AWS managed key: Free
       - Customer managed KMS key: $1/month + $0.03 per 10,000 requests
       
       **Best Practices**:
       - Use encryption for sensitive compliance data
       - Set display_name for recognizable email notifications
       - Configure delivery policies for critical alerts
    """
    # Create SNS topic
    topic = SnsTopic(
        scope,
        resource_id,
        name=topic_name,
        display_name=display_name or topic_name,
        kms_master_key_id=kms_master_key_id if enable_encryption and kms_master_key_id else None,
        delivery_policy=json.dumps(delivery_policy) if delivery_policy else None,
        tags=tags
    )

    return topic


def create_sns_topic_policy(
    scope,
    topic: SnsTopic,
    allowed_services: list = None,
    resource_id: str = "sns_topic_policy"
):
    """
    Create an SNS topic policy allowing AWS services to publish.

    Grants permission for services like Security Hub, Config, CloudWatch to publish.

    :param scope: The CDKTF construct scope (stack instance)
    :param topic: The SNS topic to attach policy to
    :type topic: SnsTopic
    :param allowed_services: List of AWS service principals (default: common compliance services)
    :type allowed_services: list
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :returns: SNS Topic Policy resource
    :rtype: SnsTopicPolicy

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import notifications
        >>> 
        >>> # Allow Security Hub and Config to publish
        >>> policy = notifications.create_sns_topic_policy(
        ...     scope=self,
        ...     topic=topic,
        ...     allowed_services=['securityhub.amazonaws.com', 'config.amazonaws.com']
        ... )

    .. note::
       **Default Allowed Services**:
       - securityhub.amazonaws.com - Security Hub findings
       - config.amazonaws.com - Config compliance notifications
       - cloudwatch.amazonaws.com - CloudWatch alarms
       - events.amazonaws.com - EventBridge events
       - backup.amazonaws.com - Backup notifications
    """
    if allowed_services is None:
        allowed_services = [
            "securityhub.amazonaws.com",
            "config.amazonaws.com",
            "cloudwatch.amazonaws.com",
            "events.amazonaws.com",
            "backup.amazonaws.com"
        ]

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowAWSServicesPublish",
                "Effect": "Allow",
                "Principal": {
                    "Service": allowed_services
                },
                "Action": "SNS:Publish",
                "Resource": topic.arn
            }
        ]
    }

    topic_policy = SnsTopicPolicy(
        scope,
        resource_id,
        arn=topic.arn,
        policy=json.dumps(policy_document)
    )

    return topic_policy
