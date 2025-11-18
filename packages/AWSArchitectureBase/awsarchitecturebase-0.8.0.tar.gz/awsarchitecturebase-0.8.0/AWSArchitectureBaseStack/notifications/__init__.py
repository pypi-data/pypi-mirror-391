"""
AWS Notifications Module
=========================

Provides SNS topics and email subscriptions for compliance alerts.

AWS SNS (Simple Notification Service):
- Pub/sub messaging for compliance findings
- Email, SMS, Lambda, SQS subscriptions
- Integration with Security Hub, Config, CloudWatch
- Event-driven notifications
"""

from .topics import create_sns_topic
from .subscriptions import create_email_subscription, create_sms_subscription
from .resources import create_notification_resources

__all__ = [
    "create_sns_topic",
    "create_email_subscription",
    "create_sms_subscription",
    "create_notification_resources",
]
