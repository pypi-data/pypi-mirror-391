"""Unified scanner for AWS, Azure, and GCP with simple configuration."""
from typing import Dict, Any, List, Optional, Protocol, Tuple
from dataclasses import dataclass
from abc import abstractmethod
import concurrent.futures
from pathlib import Path

from terraback.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ResourceSpec:
    """Universal resource specification for any cloud provider."""
    # Resource identification
    terraform_type: str
    
    # API details (provider-specific)
    api_group: str          # AWS: service, Azure: resource_provider, GCP: service
    list_operation: str     # AWS: describe_*, Azure: list, GCP: list
    list_path: str          # Response path to resources
    id_field: str           # Field containing resource ID
    
    # Import format
    import_id_format: str = "{id}"  # Can include {subscription_id}, {project}, etc.
    
    # Filtering
    exclude_patterns: List[str] = None
    include_only_patterns: List[str] = None
    
    # Template requirements
    required_fields: List[str] = None
    
    # Provider-specific options
    extra_params: Dict[str, Any] = None


# Unified resource specifications for all providers
RESOURCE_SPECS = {
    # ========== AWS Resources ==========
    'aws_vpc': ResourceSpec(
        terraform_type='aws_vpc',
        api_group='ec2',
        list_operation='describe_vpcs',
        list_path='Vpcs',
        id_field='VpcId',
        required_fields=['CidrBlock', 'EnableDnsHostnames', 'EnableDnsSupport']
    ),
    
    'aws_instance': ResourceSpec(
        terraform_type='aws_instance',
        api_group='ec2',
        list_operation='describe_instances',
        list_path='Reservations[].Instances[]',  # Nested path
        id_field='InstanceId',
        required_fields=['InstanceType', 'ImageId', 'SubnetId']
    ),
    
    'aws_s3_bucket': ResourceSpec(
        terraform_type='aws_s3_bucket',
        api_group='s3',
        list_operation='list_buckets',
        list_path='Buckets',
        id_field='Name',
        required_fields=['Name']
    ),
    
    # ========== Azure Resources ==========
    'azurerm_virtual_network': ResourceSpec(
        terraform_type='azurerm_virtual_network',
        api_group='network',
        list_operation='virtual_networks.list_all',
        list_path='value',
        id_field='id',
        import_id_format="{id}",
        required_fields=['name', 'location', 'address_space']
    ),
    
    'azurerm_virtual_machine': ResourceSpec(
        terraform_type='azurerm_virtual_machine',
        api_group='compute',
        list_operation='virtual_machines.list_all',
        list_path='value',
        id_field='id',
        required_fields=['name', 'location', 'vm_size']
    ),
    
    'azurerm_storage_account': ResourceSpec(
        terraform_type='azurerm_storage_account',
        api_group='storage',
        list_operation='storage_accounts.list',
        list_path='value',
        id_field='id',
        required_fields=['name', 'location', 'account_tier', 'account_replication_type']
    ),
    
    'azurerm_resource_group': ResourceSpec(
        terraform_type='azurerm_resource_group',
        api_group='resources',
        list_operation='resource_groups.list',
        list_path='value',
        id_field='id',
        import_id_format="{name}",  # RGs use name for import
        required_fields=['name', 'location']
    ),
    
    # ========== GCP Resources ==========
    'google_compute_network': ResourceSpec(
        terraform_type='google_compute_network',
        api_group='compute',
        list_operation='networks.list',
        list_path='items',
        id_field='selfLink',
        import_id_format="{project}/{name}",
        required_fields=['name', 'auto_create_subnetworks']
    ),
    
    'google_compute_instance': ResourceSpec(
        terraform_type='google_compute_instance',
        api_group='compute',
        list_operation='instances.list',
        list_path='items',
        id_field='selfLink',
        import_id_format="{project}/{zone}/{name}",
        required_fields=['name', 'machine_type', 'zone']
    ),
    
    'google_storage_bucket': ResourceSpec(
        terraform_type='google_storage_bucket',
        api_group='storage',
        list_operation='buckets.list',
        list_path='items',
        id_field='id',
        import_id_format="{name}",
        required_fields=['name', 'location']
    ),
    
    'google_project': ResourceSpec(
        terraform_type='google_project',
        api_group='cloudresourcemanager',
        list_operation='projects.list',
        list_path='projects',
        id_field='projectId',
        required_fields=['name', 'project_id']
    ),
}


class CloudProvider(Protocol):
    """Protocol for cloud provider implementations."""
    
    @abstractmethod
    def list_resources(self, spec: ResourceSpec) -> List[Dict[str, Any]]:
        """List resources from the cloud provider."""
        pass
    
    @abstractmethod
    def get_import_id(self, resource: Dict[str, Any], spec: ResourceSpec) -> str:
        """Generate import ID for a resource."""
        pass


class AWSProvider:
    """AWS provider implementation."""
    
    def __init__(self, profile: Optional[str] = None, region: str = 'us-east-1'):
        import boto3
        self.session = boto3.Session(profile_name=profile, region_name=region)
        self.region = region
        self.clients = {}
    
    def get_client(self, service: str):
        if service not in self.clients:
            self.clients[service] = self.session.client(service)
        return self.clients[service]
    
    def list_resources(self, spec: ResourceSpec) -> List[Dict[str, Any]]:
        """List AWS resources."""
        client = self.get_client(spec.api_group)
        resources = []
        
        try:
            # Handle nested paths like 'Reservations[].Instances[]'
            if '[]' in spec.list_path:
                # Special handling for nested resources
                if spec.terraform_type == 'aws_instance':
                    response = client.describe_instances()
                    for reservation in response.get('Reservations', []):
                        resources.extend(reservation.get('Instances', []))
            else:
                # Standard listing
                operation = getattr(client, spec.list_operation)
                response = operation(**(spec.extra_params or {}))
                resources = response.get(spec.list_path, [])
                
        except Exception as e:
            logger.error(f"AWS list error for {spec.terraform_type}: {e}")
        
        return resources
    
    def get_import_id(self, resource: Dict[str, Any], spec: ResourceSpec) -> str:
        """Generate AWS import ID."""
        resource_id = resource.get(spec.id_field, '')
        return spec.import_id_format.format(
            id=resource_id,
            region=self.region
        )


class AzureProvider:
    """Azure provider implementation."""
    
    def __init__(self, subscription_id: Optional[str] = None):
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.resource import ResourceManagementClient
        from azure.mgmt.network import NetworkManagementClient
        from azure.mgmt.compute import ComputeManagementClient
        from azure.mgmt.storage import StorageManagementClient
        
        self.credential = DefaultAzureCredential()
        self.subscription_id = subscription_id
        
        # Initialize clients
        self.clients = {
            'resources': ResourceManagementClient(self.credential, subscription_id),
            'network': NetworkManagementClient(self.credential, subscription_id),
            'compute': ComputeManagementClient(self.credential, subscription_id),
            'storage': StorageManagementClient(self.credential, subscription_id),
        }
    
    def list_resources(self, spec: ResourceSpec) -> List[Dict[str, Any]]:
        """List Azure resources."""
        resources = []
        
        try:
            # Get the appropriate client
            client = self.clients[spec.api_group]
            
            # Parse operation (e.g., 'virtual_networks.list_all')
            parts = spec.list_operation.split('.')
            operation = getattr(getattr(client, parts[0]), parts[1])
            
            # List resources
            for resource in operation():
                # Convert to dict
                resource_dict = resource.as_dict() if hasattr(resource, 'as_dict') else resource.__dict__
                resources.append(resource_dict)
                
        except Exception as e:
            logger.error(f"Azure list error for {spec.terraform_type}: {e}")
        
        return resources
    
    def get_import_id(self, resource: Dict[str, Any], spec: ResourceSpec) -> str:
        """Generate Azure import ID."""
        if spec.import_id_format == "{name}":
            return resource.get('name', '')
        return resource.get(spec.id_field, '')


class GCPProvider:
    """GCP provider implementation."""
    
    def __init__(self, project: str, credentials_path: Optional[str] = None):
        from google.cloud import compute_v1, storage, resourcemanager_v3
        
        self.project = project
        self.credentials_path = credentials_path
        
        # Initialize clients
        self.clients = {
            'compute': compute_v1,
            'storage': storage.Client(project=project),
            'cloudresourcemanager': resourcemanager_v3.ProjectsClient(),
        }
    
    def list_resources(self, spec: ResourceSpec) -> List[Dict[str, Any]]:
        """List GCP resources."""
        resources = []
        
        try:
            if spec.api_group == 'compute':
                # Handle compute resources
                if 'network' in spec.terraform_type:
                    client = self.clients['compute'].NetworksClient()
                    for network in client.list(project=self.project):
                        resources.append(self._to_dict(network))
                elif 'instance' in spec.terraform_type:
                    client = self.clients['compute'].InstancesClient()
                    # Need to list by zone
                    zones_client = self.clients['compute'].ZonesClient()
                    for zone in zones_client.list(project=self.project):
                        for instance in client.list(project=self.project, zone=zone.name):
                            resources.append(self._to_dict(instance))
                            
            elif spec.api_group == 'storage':
                # Handle storage resources
                for bucket in self.clients['storage'].list_buckets():
                    resources.append({
                        'id': bucket.id,
                        'name': bucket.name,
                        'location': bucket.location,
                        'storage_class': bucket.storage_class,
                    })
                    
        except Exception as e:
            logger.error(f"GCP list error for {spec.terraform_type}: {e}")
        
        return resources
    
    def _to_dict(self, resource) -> Dict[str, Any]:
        """Convert GCP resource to dict."""
        # Simple conversion - enhance as needed
        return {k: v for k, v in resource.__dict__.items() if not k.startswith('_')}
    
    def get_import_id(self, resource: Dict[str, Any], spec: ResourceSpec) -> str:
        """Generate GCP import ID."""
        return spec.import_id_format.format(
            project=self.project,
            zone=resource.get('zone', '').split('/')[-1] if 'zone' in resource else '',
            name=resource.get('name', ''),
            id=resource.get(spec.id_field, '')
        )


class UnifiedScanner:
    """Unified scanner for all cloud providers."""
    
    def __init__(self, provider: CloudProvider):
        self.provider = provider
    
    def scan_resource(self, resource_type: str) -> List[Dict[str, Any]]:
        """Scan a specific resource type."""
        if resource_type not in RESOURCE_SPECS:
            raise ValueError(f"Unknown resource type: {resource_type}")
        
        spec = RESOURCE_SPECS[resource_type]
        
        # List resources
        raw_resources = self.provider.list_resources(spec)
        
        # Process resources
        processed = []
        for raw in raw_resources:
            resource = self._process_resource(raw, spec)
            if resource:
                processed.append(resource)
        
        return processed
    
    def scan_multiple(self, resource_types: List[str], parallel: int = 5) -> Dict[str, List[Dict]]:
        """Scan multiple resource types in parallel."""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
            future_to_type = {
                executor.submit(self.scan_resource, rt): rt 
                for rt in resource_types
            }
            
            for future in concurrent.futures.as_completed(future_to_type):
                resource_type = future_to_type[future]
                try:
                    resources = future.result()
                    if resources:
                        results[resource_type] = resources
                        logger.info(f"Found {len(resources)} {resource_type} resources")
                except Exception as e:
                    logger.error(f"Failed to scan {resource_type}: {e}")
        
        return results
    
    def _process_resource(self, raw: Dict[str, Any], spec: ResourceSpec) -> Optional[Dict[str, Any]]:
        """Process a resource for Terraform."""
        # Extract ID
        resource_id = raw.get(spec.id_field)
        if not resource_id:
            return None
        
        # Apply filters
        if spec.exclude_patterns:
            for pattern in spec.exclude_patterns:
                if pattern in str(resource_id):
                    return None
        
        # Build processed resource
        return {
            'id': resource_id,
            'terraform_type': spec.terraform_type,
            'import_id': self.provider.get_import_id(raw, spec),
            'name_sanitized': self._sanitize_name(resource_id),
            'raw': raw,
            'required_fields': {
                field: raw.get(field) 
                for field in (spec.required_fields or [])
                if field in raw
            }
        }
    
    def _sanitize_name(self, name: str) -> str:
        """Create valid Terraform resource name."""
        import re
        name = str(name).split('/')[-1]  # Get last part if path
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        if name and not name[0].isalpha():
            name = 'resource_' + name
        return name[:63]


# Convenience functions
def scan_aws(profile: Optional[str] = None, region: str = 'us-east-1', 
             resources: List[str] = None) -> Dict[str, List[Dict]]:
    """Scan AWS resources."""
    provider = AWSProvider(profile, region)
    scanner = UnifiedScanner(provider)
    
    if resources is None:
        resources = [k for k in RESOURCE_SPECS.keys() if k.startswith('aws_')]
    
    return scanner.scan_multiple(resources)


def scan_azure(subscription_id: str, resources: List[str] = None) -> Dict[str, List[Dict]]:
    """Scan Azure resources."""
    provider = AzureProvider(subscription_id)
    scanner = UnifiedScanner(provider)
    
    if resources is None:
        resources = [k for k in RESOURCE_SPECS.keys() if k.startswith('azurerm_')]
    
    return scanner.scan_multiple(resources)


def scan_gcp(project: str, resources: List[str] = None) -> Dict[str, List[Dict]]:
    """Scan GCP resources."""
    provider = GCPProvider(project)
    scanner = UnifiedScanner(provider)
    
    if resources is None:
        resources = [k for k in RESOURCE_SPECS.keys() if k.startswith('google_')]
    
    return scanner.scan_multiple(resources)