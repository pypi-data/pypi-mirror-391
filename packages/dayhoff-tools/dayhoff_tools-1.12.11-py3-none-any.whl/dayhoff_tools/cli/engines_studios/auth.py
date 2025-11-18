"""AWS authentication and identity helpers."""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def get_aws_username() -> str:
    """Get username from AWS STS caller identity.
    
    Parses username from the AWS SSO assumed role ARN.
    This works even when running as root in containers where $USER is empty.
    
    Returns:
        Username from AWS identity
        
    Raises:
        RuntimeError: If not authenticated to AWS
    """
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        
        # Parse username from assumed role ARN
        # Format: arn:aws:sts::123456789012:assumed-role/AWSReservedSSO_DeveloperAccess_xxxx/username
        arn = identity["Arn"]
        
        if "assumed-role" in arn:
            # SSO auth - username is last component
            username = arn.split("/")[-1]
            return username
        else:
            # Other auth methods - use last part of UserId
            return identity["UserId"].split(":")[-1]
            
    except (NoCredentialsError, ClientError) as e:
        raise RuntimeError(
            "Not authenticated to AWS. "
            "Run: dh aws login --profile <profile-name>"
        ) from e

