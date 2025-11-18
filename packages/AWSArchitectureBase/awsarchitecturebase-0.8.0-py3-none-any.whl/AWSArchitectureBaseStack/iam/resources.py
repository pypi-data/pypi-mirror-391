"""
IAM Resources orchestration.

This module provides high-level functions to create complete IAM infrastructure
following AWS best practices and security guidelines.
"""

from . import user, policy


def create_iam_resources(
    scope,
    project_name: str,
    environment: str,
    iam_users: list = None
):
    """
    Create complete IAM infrastructure with best practices.
    
    This orchestration function creates:
    - IAM users with programmatic access (access keys)
    - IAM policies attached to users
    - Proper naming conventions and tagging

    :param scope: The CDKTF construct scope (stack instance)
    :param project_name: Project name for naming
    :param environment: Environment (dev, staging, prod)
    :param iam_users: List of dicts with IAM user configurations
                      [{'name': 'app-user', 'resource_id': 'app_user', 'policies': ['path/to/policy.json']}]
    :returns: Dictionary with created IAM resources
    :rtype: dict
    
    """
    resources = {}
    
    if not iam_users:
        return resources
    
    resources['users'] = []
    
    for user_config in iam_users:
        # Create IAM user with access key
        iam_user, access_key = user.create_iam_user_with_key(
            scope=scope,
            user_name=user_config['name'],
            resource_id=user_config['resource_id']
        )
        
        user_resource = {
            'name': user_config['name'],
            'resource_id': user_config['resource_id'],
            'user': iam_user,
            'access_key': access_key,
            'policies': []
        }
        
        # Attach policies if specified
        if 'policies' in user_config:
            for policy_config in user_config['policies']:
                iam_policy = policy.create_iam_policy_from_file(
                    scope=scope,
                    file_path=policy_config['file'],
                    user_name=iam_user.name,
                    policy_type=policy_config['type'],
                    project_name=project_name,
                    environment=environment
                )
                user_resource['policies'].append({
                    'type': policy_config['type'],
                    'policy': iam_policy
                })
        
        resources['users'].append(user_resource)
    
    return resources
