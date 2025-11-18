"""
AWS SNS Subscriptions Configuration
====================================

Functions for creating SNS subscriptions (email, SMS, etc.).
"""

from cdktf_cdktf_provider_aws.sns_topic_subscription import SnsTopicSubscription


def create_email_subscription(
    scope,
    topic_arn: str,
    email: str,
    resource_id: str = "email_subscription",
    filter_policy: dict = None
):
    """
    Create an email subscription for SNS topic.

    Subscribes an email address to receive compliance notifications.

    :param scope: The CDKTF construct scope (stack instance)
    :param topic_arn: ARN of the SNS topic
    :type topic_arn: str
    :param email: Email address to subscribe
    :type email: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param filter_policy: Message filtering policy (optional)
    :type filter_policy: dict
    :returns: SNS Topic Subscription resource
    :rtype: SnsTopicSubscription

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import notifications
        >>> 
        >>> # Basic email subscription
        >>> subscription = notifications.create_email_subscription(
        ...     scope=self,
        ...     topic_arn=topic.arn,
        ...     email="security@example.com"
        ... )
        >>> 
        >>> # Email subscription with filter for critical findings only
        >>> subscription = notifications.create_email_subscription(
        ...     scope=self,
        ...     topic_arn=topic.arn,
        ...     email="security@example.com",
        ...     filter_policy={
        ...         "severity": ["CRITICAL", "HIGH"]
        ...     }
        ... )

    .. note::
       **Subscription Confirmation**:
       Email subscriptions require confirmation via email link.
       User must click confirmation link before receiving notifications.
       
       **Filter Policy**:
       Use filter_policy to reduce noise by filtering messages.
       Filters based on message attributes (severity, service, etc.).
       
       **Cost**: First 1,000 emails free, then $2 per 100,000 notifications.
    """
    import json

    subscription = SnsTopicSubscription(
        scope,
        resource_id,
        topic_arn=topic_arn,
        protocol="email",
        endpoint=email,
        filter_policy=json.dumps(filter_policy) if filter_policy else None
    )

    return subscription


def create_sms_subscription(
    scope,
    topic_arn: str,
    phone_number: str,
    resource_id: str = "sms_subscription",
    filter_policy: dict = None
):
    """
    Create an SMS subscription for SNS topic.

    Subscribes a phone number to receive compliance notifications via SMS.

    :param scope: The CDKTF construct scope (stack instance)
    :param topic_arn: ARN of the SNS topic
    :type topic_arn: str
    :param phone_number: Phone number in E.164 format (e.g., +1234567890)
    :type phone_number: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param filter_policy: Message filtering policy (optional)
    :type filter_policy: dict
    :returns: SNS Topic Subscription resource
    :rtype: SnsTopicSubscription

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import notifications
        >>> 
        >>> # SMS subscription for critical alerts
        >>> subscription = notifications.create_sms_subscription(
        ...     scope=self,
        ...     topic_arn=topic.arn,
        ...     phone_number="+12345678900",
        ...     filter_policy={
        ...         "severity": ["CRITICAL"]
        ...     }
        ... )

    .. note::
       **Phone Number Format**: Must be in E.164 format (+[country code][number])
       
       **SMS Limits**:
       - Default limit: 1 SMS per second
       - Request limit increase via AWS Support
       
       **Cost**: $0.00645 per SMS (US pricing)
       
       **Best Practice**: Use SMS only for critical alerts to control costs.
    """
    import json

    subscription = SnsTopicSubscription(
        scope,
        resource_id,
        topic_arn=topic_arn,
        protocol="sms",
        endpoint=phone_number,
        filter_policy=json.dumps(filter_policy) if filter_policy else None
    )

    return subscription


def create_lambda_subscription(
    scope,
    topic_arn: str,
    lambda_function_arn: str,
    resource_id: str = "lambda_subscription",
    filter_policy: dict = None
):
    """
    Create a Lambda subscription for SNS topic.

    Subscribes a Lambda function to process compliance notifications.

    :param scope: The CDKTF construct scope (stack instance)
    :param topic_arn: ARN of the SNS topic
    :type topic_arn: str
    :param lambda_function_arn: ARN of the Lambda function
    :type lambda_function_arn: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param filter_policy: Message filtering policy (optional)
    :type filter_policy: dict
    :returns: SNS Topic Subscription resource
    :rtype: SnsTopicSubscription

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import notifications
        >>> 
        >>> # Lambda subscription for automated remediation
        >>> subscription = notifications.create_lambda_subscription(
        ...     scope=self,
        ...     topic_arn=topic.arn,
        ...     lambda_function_arn=lambda_func.arn
        ... )

    .. note::
       **Lambda Permission**: Ensure Lambda has permission to be invoked by SNS.
       
       **Use Cases**:
       - Automated remediation of compliance findings
       - Custom notification formatting
       - Integration with ticketing systems
       - Aggregation and analysis
       
       **Cost**: No additional SNS cost. Standard Lambda pricing applies.
    """
    import json

    subscription = SnsTopicSubscription(
        scope,
        resource_id,
        topic_arn=topic_arn,
        protocol="lambda",
        endpoint=lambda_function_arn,
        filter_policy=json.dumps(filter_policy) if filter_policy else None
    )

    return subscription
