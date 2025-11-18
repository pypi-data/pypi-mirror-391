"""
Naming utilities for AWS resources.

This module provides functions to convert strings into valid names
for AWS resources like S3 buckets, S3 keys, and database identifiers.
"""


def properize_string(string: str) -> str:
    """
    Convert a string to a valid AWS resource name.

    Replaces invalid characters with hyphens and converts to lowercase.
    Can be used for S3 bucket names, key names, and other AWS resources.

    :param string: Input string to convert
    :type string: str
    :returns: Properized string suitable for AWS resource names
    :rtype: str

    Example:
        >>> properize_string("My App_Name.v1")
        'my-app-name-v1'
        
    Note:
        - For S3 bucket names: AWS requires max 63 characters, use [:63] if needed
        - For S3 key names: AWS allows up to 1024 characters
    """
    return (
        string.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace(".", "-")
        .replace(":", "-")
        .replace("/", "-")
        .replace("\\", "-")
    )


def clean_hyphens(string: str) -> str:
    """
    Clean hyphens and spaces from string for database naming.

    Converts hyphens and spaces to underscores and makes lowercase
    for database compatibility.

    :param string: Input string to clean
    :type string: str
    :returns: Cleaned string suitable for database names
    :rtype: str

    Example:
        >>> clean_hyphens("my-app name")
        'my_app_name'
    """
    return string.replace("-", "_").replace(" ", "_").lower()
