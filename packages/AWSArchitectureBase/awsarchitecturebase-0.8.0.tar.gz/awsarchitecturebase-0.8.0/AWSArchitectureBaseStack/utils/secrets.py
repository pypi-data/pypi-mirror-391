"""
Secret management utilities.

This module provides functions for parsing and managing secrets
from environment variables and other sources.
"""

import json
import os
from typing import Dict, Optional


def parse_secrets_from_env(env_var_name: str) -> Optional[Dict]:
    """
    Parse secrets from a JSON-formatted environment variable.

    Reads an environment variable containing a JSON string and parses it
    into a Python dictionary. Returns None if the variable doesn't exist
    or contains invalid JSON.

    :param env_var_name: Name of the environment variable to read
    :type env_var_name: str
    :returns: Dictionary of parsed secrets, or None if parsing fails
    :rtype: Optional[Dict]

    """
    secret_json = os.environ.get(env_var_name)
    
    if not secret_json:
        return None
    
    try:
        return json.loads(secret_json)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse {env_var_name} as JSON: {e}")
        return None
