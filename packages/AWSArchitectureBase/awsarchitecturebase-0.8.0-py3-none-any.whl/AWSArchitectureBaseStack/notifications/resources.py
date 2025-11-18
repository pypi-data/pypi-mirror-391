"""
AWS Notifications Resources Orchestrator
==========================================

Orchestrates the creation of SNS topics and subscriptions for compliance alerts.
"""

from .topics import create_sns_topic, create_sns_topic_policy
from .subscriptions import create_email_subscription, create_sms_subscription, create_lambda_subscription


def create_notification_resources(
    scope,
    topic_name: str,
    enable_notifications: bool = False,  # Safe default: disabled
    display_name: str = None,
    enable_encryption: bool = True,
    kms_master_key_id: str = None,
    email_subscriptions: list = None,
    sms_subscriptions: list = None,
    lambda_subscriptions: list = None,
    allowed_services: list = None,
    tags: dict = None
):
    """
    Create all notification resources with proper orchestration.

    Manages SNS topic creation, policy attachment, and subscriptions.

    :param scope: The CDKTF construct scope (stack instance)
    :param topic_name: Name for the SNS topic
    :type topic_name: str
    :param enable_notifications: Enable notification subscriptions (default: False for safety)
    :type enable_notifications: bool
    :param display_name: Display name for email subscriptions
    :type display_name: str
    :param enable_encryption: Enable server-side encryption (default: True)
    :type enable_encryption: bool
    :param kms_master_key_id: KMS key ID for encryption
    :type kms_master_key_id: str
    :param email_subscriptions: List of email subscription configurations
    :type email_subscriptions: list of dict
    :param sms_subscriptions: List of SMS subscription configurations
    :type sms_subscriptions: list of dict
    :param lambda_subscriptions: List of Lambda subscription configurations
    :type lambda_subscriptions: list of dict
    :param allowed_services: AWS services allowed to publish (default: common compliance services)
    :type allowed_services: list
    :param tags: Resource tags
    :type tags: dict
    :returns: Dictionary with created resources
    :rtype: dict

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import notifications
        >>> 
        >>> # SNS topic only (no subscriptions)
        >>> resources = notifications.create_notification_resources(
        ...     scope=self,
        ...     topic_name="ftr-compliance-alerts"
        ... )
        >>> 
        >>> # SNS topic with email subscriptions
        >>> resources = notifications.create_notification_resources(
        ...     scope=self,
        ...     topic_name="ftr-compliance-alerts",
        ...     enable_notifications=True,
        ...     email_subscriptions=[
        ...         {'email': 'security@example.com'},
        ...         {'email': 'compliance@example.com', 'filter_policy': {'severity': ['CRITICAL']}}
        ...     ]
        ... )
        >>> 
        >>> # Complete notification setup
        >>> resources = notifications.create_notification_resources(
        ...     scope=self,
        ...     topic_name="ftr-compliance-alerts",
        ...     enable_notifications=True,
        ...     email_subscriptions=[{'email': 'security@example.com'}],
        ...     sms_subscriptions=[{'phone_number': '+12345678900', 'filter_policy': {'severity': ['CRITICAL']}}],
        ...     lambda_subscriptions=[{'lambda_function_arn': lambda_func.arn}]
        ... )

    .. note::
       **Safe Defaults**:
       - enable_notifications=False (create topic but no subscriptions)
       - enable_encryption=True (encrypt messages at rest)
       
       **Subscription Format**:
       - Email: {'email': 'user@example.com', 'filter_policy': {...}}
       - SMS: {'phone_number': '+1234567890', 'filter_policy': {...}}
       - Lambda: {'lambda_function_arn': 'arn:...', 'filter_policy': {...}}
       
       **Cost Estimates**:
       - Topic: Free
       - Email: First 1,000 free, then $2 per 100,000
       - SMS: $0.00645 per message (US)
       - Lambda: No SNS cost, standard Lambda pricing
       
       **Integration**:
       Topic ARN can be used with:
       - Security Hub (findings)
       - AWS Config (compliance notifications)
       - CloudWatch (alarms)
       - EventBridge (events)
       - AWS Backup (backup notifications)
    """
    resources = {}

    # Create SNS topic
    topic = create_sns_topic(
        scope=scope,
        topic_name=topic_name,
        display_name=display_name,
        enable_encryption=enable_encryption,
        kms_master_key_id=kms_master_key_id,
        tags=tags
    )
    resources['topic'] = topic

    # Create topic policy to allow AWS services to publish
    topic_policy = create_sns_topic_policy(
        scope=scope,
        topic=topic,
        allowed_services=allowed_services
    )
    resources['topic_policy'] = topic_policy

    # Create subscriptions if enabled
    if enable_notifications:
        subscriptions = []

        # Email subscriptions
        if email_subscriptions:
            for idx, email_config in enumerate(email_subscriptions):
                subscription = create_email_subscription(
                    scope=scope,
                    topic_arn=topic.arn,
                    email=email_config['email'],
                    resource_id=f"email_subscription_{idx}",
                    filter_policy=email_config.get('filter_policy')
                )
                subscriptions.append(subscription)

        # SMS subscriptions
        if sms_subscriptions:
            for idx, sms_config in enumerate(sms_subscriptions):
                subscription = create_sms_subscription(
                    scope=scope,
                    topic_arn=topic.arn,
                    phone_number=sms_config['phone_number'],
                    resource_id=f"sms_subscription_{idx}",
                    filter_policy=sms_config.get('filter_policy')
                )
                subscriptions.append(subscription)

        # Lambda subscriptions
        if lambda_subscriptions:
            for idx, lambda_config in enumerate(lambda_subscriptions):
                subscription = create_lambda_subscription(
                    scope=scope,
                    topic_arn=topic.arn,
                    lambda_function_arn=lambda_config['lambda_function_arn'],
                    resource_id=f"lambda_subscription_{idx}",
                    filter_policy=lambda_config.get('filter_policy')
                )
                subscriptions.append(subscription)

        resources['subscriptions'] = subscriptions

    return resources
