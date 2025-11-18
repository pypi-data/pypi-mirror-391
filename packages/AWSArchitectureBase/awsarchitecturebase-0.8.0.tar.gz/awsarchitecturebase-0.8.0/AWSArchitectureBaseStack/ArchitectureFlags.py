from enum import Enum

class ArchitectureFlags(Enum):
    """
    Architecture configuration flags for optional components.

    **Skip Flags (disable features):**
    
    :param SKIP_DATABASE: Skip database creation
    :param SKIP_DOMAIN: Skip domain and DNS configuration
    :param SKIP_DEFAULT_POST_APPLY_SCRIPTS: Skip default post-apply scripts
    :param SKIP_SSL_CERT: Skip SSL certificate creation
    
    **Enable Flags (opt-in FTR compliance services):**
    
    :param ENABLE_SECURITY_HUB: Enable AWS Security Hub with FTR compliance standards
    :param ENABLE_CONFIG: Enable AWS Config for compliance monitoring
    :param ENABLE_BACKUP: Enable AWS Backup for centralized backup management
    :param ENABLE_INSPECTOR: Enable AWS Inspector for vulnerability assessments
    :param ENABLE_SYSTEMS_MANAGER: Enable AWS Systems Manager for patch management
    :param ENABLE_CLOUDTRAIL: Enable AWS CloudTrail for enhanced logging
    :param ENABLE_GUARDDUTY: Enable AWS GuardDuty for threat detection
    :param ENABLE_ACCESS_ANALYZER: Enable AWS IAM Access Analyzer (CIS v3.0.0 Control 1.20)
    :param ENABLE_NOTIFICATIONS: Enable AWS SNS/SES for compliance notifications
    :param ENABLE_ALL_FTR_COMPLIANCE: Enable all FTR compliance services at once
    """

    # Skip flags
    SKIP_DATABASE = "skip_database"
    SKIP_DOMAIN = "skip_domain"
    SKIP_DEFAULT_POST_APPLY_SCRIPTS = "skip_default_post_apply_scripts"
    SKIP_SSL_CERT = "skip_ssl_cert"
    
    # FTR Compliance enable flags
    ENABLE_SECURITY_HUB = "enable_security_hub"
    ENABLE_CONFIG = "enable_config"
    ENABLE_BACKUP = "enable_backup"
    ENABLE_INSPECTOR = "enable_inspector"
    ENABLE_SYSTEMS_MANAGER = "enable_systems_manager"
    ENABLE_CLOUDTRAIL = "enable_cloudtrail"
    ENABLE_GUARDDUTY = "enable_guardduty"
    ENABLE_ACCESS_ANALYZER = "enable_access_analyzer"
    ENABLE_NOTIFICATIONS = "enable_notifications"
    ENABLE_ALL_FTR_COMPLIANCE = "enable_all_ftr_compliance"