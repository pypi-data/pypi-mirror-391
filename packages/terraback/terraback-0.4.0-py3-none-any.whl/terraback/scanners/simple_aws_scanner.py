"""Simplified AWS scanner with declarative configuration."""
from typing import Dict, Any, Optional, List, Generator
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError

from terraback.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ResourceConfig:
    """Configuration for a resource type."""
    service: str                    # AWS service name (ec2, s3, etc.)
    operation: str                  # API operation (describe_instances, list_buckets)
    result_key: Optional[str]       # Key in response containing resources
    id_field: str                   # Field containing resource ID
    terraform_type: str             # Terraform resource type
    filter_prefixes: List[str] = None  # Prefixes to filter out (e.g., ['AWS-', 'default.'])
    
    def __post_init__(self):
        if self.filter_prefixes is None:
            self.filter_prefixes = []


# Simple configuration for all AWS resources
AWS_RESOURCES = {
    # EC2
    'ec2_instances': ResourceConfig(
        service='ec2',
        operation='describe_instances',
        result_key='Reservations',  # Special handling needed
        id_field='InstanceId',
        terraform_type='aws_instance'
    ),
    'ec2_security_groups': ResourceConfig(
        service='ec2',
        operation='describe_security_groups',
        result_key='SecurityGroups',
        id_field='GroupId',
        terraform_type='aws_security_group',
        filter_prefixes=['default']
    ),
    'ec2_vpcs': ResourceConfig(
        service='ec2',
        operation='describe_vpcs',
        result_key='Vpcs',
        id_field='VpcId',
        terraform_type='aws_vpc'
    ),
    'ec2_subnets': ResourceConfig(
        service='ec2',
        operation='describe_subnets',
        result_key='Subnets',
        id_field='SubnetId',
        terraform_type='aws_subnet'
    ),
    
    # S3
    's3_buckets': ResourceConfig(
        service='s3',
        operation='list_buckets',
        result_key='Buckets',
        id_field='Name',
        terraform_type='aws_s3_bucket'
    ),
    
    # IAM
    'iam_roles': ResourceConfig(
        service='iam',
        operation='list_roles',
        result_key='Roles',
        id_field='RoleName',
        terraform_type='aws_iam_role',
        filter_prefixes=['AWS']
    ),
    
    # RDS
    'rds_instances': ResourceConfig(
        service='rds',
        operation='describe_db_instances',
        result_key='DBInstances',
        id_field='DBInstanceIdentifier',
        terraform_type='aws_db_instance'
    ),
    
    # Lambda
    'lambda_functions': ResourceConfig(
        service='lambda',
        operation='list_functions',
        result_key='Functions',
        id_field='FunctionName',
        terraform_type='aws_lambda_function'
    ),
    
    # Add more resources as needed...
}


class SimpleAWSScanner:
    """Simple AWS scanner that uses configuration instead of inheritance."""
    
    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None):
        self.profile = profile
        self.region = region or 'us-east-1'
        self.session = boto3.Session(profile_name=profile, region_name=region)
    
    def scan_resource(self, resource_name: str) -> List[Dict[str, Any]]:
        """Scan a specific resource type."""
        if resource_name not in AWS_RESOURCES:
            raise ValueError(f"Unknown resource type: {resource_name}")
        
        config = AWS_RESOURCES[resource_name]
        client = self.session.client(config.service)
        
        try:
            # Special handling for different resource types
            if resource_name == 'ec2_instances':
                return self._scan_ec2_instances(client, config)
            else:
                return self._scan_generic(client, config)
        except ClientError as e:
            logger.error(f"Failed to scan {resource_name}: {e}")
            return []
    
    def _scan_generic(self, client, config: ResourceConfig) -> List[Dict[str, Any]]:
        """Generic scanning for most resources."""
        resources = []
        
        try:
            # Call the API operation
            operation = getattr(client, config.operation)
            
            # Handle pagination
            if hasattr(client, 'get_paginator') and client.can_paginate(config.operation):
                paginator = client.get_paginator(config.operation)
                for page in paginator.paginate():
                    items = page.get(config.result_key, [])
                    resources.extend(self._process_resources(items, config))
            else:
                response = operation()
                items = response.get(config.result_key, [])
                resources.extend(self._process_resources(items, config))
                
        except Exception as e:
            logger.error(f"Error scanning {config.terraform_type}: {e}")
        
        return resources
    
    def _scan_ec2_instances(self, client, config: ResourceConfig) -> List[Dict[str, Any]]:
        """Special handling for EC2 instances (nested in reservations)."""
        resources = []
        
        try:
            paginator = client.get_paginator('describe_instances')
            for page in paginator.paginate():
                for reservation in page.get('Reservations', []):
                    instances = reservation.get('Instances', [])
                    resources.extend(self._process_resources(instances, config))
        except Exception as e:
            logger.error(f"Error scanning EC2 instances: {e}")
        
        return resources
    
    def _process_resources(self, items: List[Dict], config: ResourceConfig) -> List[Dict[str, Any]]:
        """Process and enrich resources."""
        processed = []
        
        for item in items:
            # Extract ID
            resource_id = item.get(config.id_field, '')
            if not resource_id:
                continue
            
            # Filter out unwanted resources
            if config.filter_prefixes:
                if any(resource_id.startswith(prefix) for prefix in config.filter_prefixes):
                    logger.debug(f"Filtered out {config.terraform_type}: {resource_id}")
                    continue
            
            # Enrich resource
            enriched = {
                'id': resource_id,
                'name_sanitized': self._sanitize_name(resource_id),
                'terraform_type': config.terraform_type,
                'import_id': resource_id,
                'raw': item
            }
            
            # Extract tags
            tags = self._extract_tags(item)
            if tags:
                enriched['tags_formatted'] = tags
            
            processed.append(enriched)
        
        return processed
    
    def _extract_tags(self, resource: Dict[str, Any]) -> Dict[str, str]:
        """Extract tags from various formats."""
        if 'Tags' in resource:
            if isinstance(resource['Tags'], list):
                return {tag['Key']: tag['Value'] for tag in resource['Tags'] if 'Key' in tag}
            elif isinstance(resource['Tags'], dict):
                return resource['Tags']
        return {}
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize resource name for Terraform."""
        import re
        # Remove invalid characters
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        # Ensure starts with letter
        if name and not name[0].isalpha():
            name = 'r_' + name
        return name[:63]  # Limit length


def scan_all_resources(profile: Optional[str] = None, region: Optional[str] = None) -> Dict[str, List[Dict]]:
    """Scan all configured AWS resources."""
    scanner = SimpleAWSScanner(profile, region)
    results = {}
    
    for resource_name in AWS_RESOURCES:
        logger.info(f"Scanning {resource_name}...")
        results[resource_name] = scanner.scan_resource(resource_name)
    
    return results