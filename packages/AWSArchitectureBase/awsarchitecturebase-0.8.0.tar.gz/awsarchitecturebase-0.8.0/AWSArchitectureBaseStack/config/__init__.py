"""
AWS Config Module
=================

Provides configuration compliance monitoring and resource tracking.

AWS Config:
- Records resource configuration changes continuously
- Evaluates resource compliance against rules
- Maintains configuration history and snapshots
- Enables automated compliance reporting
- Tracks configuration drift and changes
"""

from .recorder import create_config_recorder, create_delivery_channel, enable_config_recorder
from .rules import create_config_rule, enable_ftr_compliance_rules
from .iam_role import create_config_iam_role
from .resources import create_config_resources

__all__ = [
    "create_config_recorder",
    "create_delivery_channel",
    "enable_config_recorder",
    "create_config_rule",
    "enable_ftr_compliance_rules",
    "create_config_iam_role",
    "create_config_resources",
]
