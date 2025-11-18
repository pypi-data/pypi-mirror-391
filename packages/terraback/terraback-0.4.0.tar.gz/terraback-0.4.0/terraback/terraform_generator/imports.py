import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from .filters import to_terraform_resource_name, strip_id_prefix


def flatten_azure_resource_properties(resource: Dict[str, Any], resource_type: str) -> Dict[str, Any]:
    """
    Transform Azure resource data to match the structure expected by templates.
    This flattens nested properties similar to how it's done during scanning.
    """
    if not resource or 'properties' not in resource:
        return resource
    
    # Create a copy to avoid mutating the original
    flattened = resource.copy()
    properties = resource.get('properties', {})
    
    # Apply resource-specific transformations based on scanning logic
    if resource_type == 'azure_key_vault':
        # From terraback/cli/azure/security/key_vaults.py:100-106
        if 'enabled_for_deployment' in properties:
            flattened['enabled_for_deployment'] = properties['enabled_for_deployment']
        if 'enabled_for_disk_encryption' in properties:
            flattened['enabled_for_disk_encryption'] = properties['enabled_for_disk_encryption']
        if 'enabled_for_template_deployment' in properties:
            flattened['enabled_for_template_deployment'] = properties['enabled_for_template_deployment']
        if 'enable_rbac_authorization' in properties:
            flattened['enable_rbac_authorization'] = properties['enable_rbac_authorization']
        if 'soft_delete_retention_in_days' in properties:
            flattened['soft_delete_retention_days'] = properties['soft_delete_retention_in_days']
        if 'enable_purge_protection' in properties:
            flattened['purge_protection_enabled'] = properties['enable_purge_protection']
        if 'public_network_access' in properties:
            flattened['public_network_access_enabled'] = properties['public_network_access'] != 'Disabled'
    
    elif resource_type == 'azure_storage_account':
        # From terraback/cli/azure/storage/storage_accounts.py property mappings
        # These are mapped in _format_template_attributes()
        if 'enable_https_traffic_only' in properties:
            flattened['https_traffic_only_enabled'] = properties['enable_https_traffic_only']
        if 'minimum_tls_version' in properties:
            flattened['min_tls_version'] = properties['minimum_tls_version']
        if 'allow_blob_public_access' in properties:
            flattened['allow_nested_items_to_be_public'] = properties['allow_blob_public_access']
        if 'access_tier' in properties:
            flattened['access_tier'] = properties['access_tier']
        if 'is_hns_enabled' in properties:
            flattened['is_hns_enabled'] = properties['is_hns_enabled']
        
        # Handle encryption settings
        if 'encryption' in properties and properties['encryption']:
            encryption = properties['encryption']
            if 'require_infrastructure_encryption' in encryption:
                flattened['infrastructure_encryption_enabled'] = encryption['require_infrastructure_encryption']
    
    elif resource_type in ['azure_virtual_machine', 'azure_linux_virtual_machine', 'azure_windows_virtual_machine']:
        # VM properties are handled differently in the scanning code but we can add common ones
        # Most VM properties are already at the top level or handled by complex nested logic
        # For now, focus on basic properties that might be nested
        pass
    
    # Add more resource types as needed based on their scanning logic
    
    return flattened


def detect_provider_from_resource_type(resource_type: str) -> str:
    """Detect cloud provider from resource type.

    Raises:
        ValueError: If the provider cannot be determined from ``resource_type``.
    """
    lower = resource_type.lower()
    if any(prefix in lower for prefix in ['aws_', 'amazon', 'ec2', 's3', 'iam', 'lambda', 'api_gateway', 'route53', 'cloudfront', 'elb', 'eip', 'elasticache', 'rds', 'vpc', 'subnet', 'security_group', 'internet_gateway', 'route_table', 'network_interface', 'volume', 'snapshot', 'ami', 'launch', 'autoscaling', 'sns', 'sqs', 'cloudwatch', 'acm', 'ecr', 'ecs', 'efs', 'secretsmanager', 'ssm']):
        return "aws"
    elif any(prefix in lower for prefix in ['azure_', 'azurerm_', 'microsoft']):
        return "azure"
    elif any(prefix in lower for prefix in ['gcp_', 'google_', 'compute']):
        return "gcp"
    else:
        raise ValueError(
            f"Unable to detect provider from resource type '{resource_type}'. Please specify the provider explicitly."
        )


def normalize_terraform_resource_type(resource_type: str, provider: Optional[str] = None) -> str:
    """
    Convert short resource type names to full Terraform resource type names.
    
    Args:
        resource_type: Short name like 'api_gateway_deployment' or full name like 'aws_api_gateway_deployment'
        provider: Optional provider override ('aws', 'azure', 'gcp')
    
    Returns:
        Full Terraform resource type like 'aws_api_gateway_deployment'
    """
    # If already has provider prefix, return as-is
    if any(resource_type.startswith(prefix) for prefix in ['aws_', 'azurerm_', 'google_']):
        return resource_type
    
    # Detect provider if not provided
    if not provider:
        provider = detect_provider_from_resource_type(resource_type)
    
    # AWS resource type mappings
    aws_mappings = {
        # API Gateway
        'api_gateway_deployment': 'aws_api_gateway_deployment',
        'api_gateway_method': 'aws_api_gateway_method',
        'api_gateway_resource': 'aws_api_gateway_resource',
        'api_gateway_rest_api': 'aws_api_gateway_rest_api',
        'api_gateway_stage': 'aws_api_gateway_stage',
        'api_gateway_integration': 'aws_api_gateway_integration',
        
        # Compute
        'ec2': 'aws_instance',
        'ec2_instance': 'aws_instance',
        'instance': 'aws_instance',
        'instances': 'aws_instance',
        'launch_configuration': 'aws_launch_configuration',
        'autoscaling_group': 'aws_autoscaling_group',
        'autoscaling_policy': 'aws_autoscaling_policy',
        'lambda_function': 'aws_lambda_function',
        'lambda_layer_version': 'aws_lambda_layer_version',
        'lambda_permission': 'aws_lambda_permission',
        
        # Storage
        's3_bucket': 'aws_s3_bucket',
        'bucket': 'aws_s3_bucket',
        'buckets': 'aws_s3_bucket',
        'ebs_volume': 'aws_ebs_volume',
        'volume': 'aws_ebs_volume',
        'volumes': 'aws_ebs_volume',
        'ebs_snapshot': 'aws_ebs_snapshot',
        'efs_file_system': 'aws_efs_file_system',
        'efs_mount_target': 'aws_efs_mount_target',
        'efs_access_point': 'aws_efs_access_point',
        
        # Networking
        'vpc': 'aws_vpc',
        'vpcs': 'aws_vpc',
        'subnet': 'aws_subnet',
        'subnets': 'aws_subnet',
        'security_group': 'aws_security_group',
        'security_groups': 'aws_security_group',
        'internet_gateway': 'aws_internet_gateway',
        'nat_gateway': 'aws_nat_gateway',
        'route_table': 'aws_route_table',
        'network_interface': 'aws_network_interface',
        'network_interfaces': 'aws_network_interface',
        'eip': 'aws_eip',
        'eips': 'aws_eip',
        'vpc_endpoint': 'aws_vpc_endpoint',
        
        # Load Balancing
        'classic_load_balancer': 'aws_elb',
        'elbv2_load_balancer': 'aws_lb',
        'elbv2_target_group': 'aws_lb_target_group',
        'elbv2_listener': 'aws_lb_listener',
        'elbv2_listener_rule': 'aws_lb_listener_rule',
        'elbv2_target_group_attachments': 'aws_lb_target_group_attachment',
        
        # Database
        'rds_instance': 'aws_db_instance',
        'rds_parameter_group': 'aws_db_parameter_group',
        'rds_subnet_group': 'aws_db_subnet_group',
        
        # Caching
        'elasticache_redis_cluster': 'aws_elasticache_cluster',
        'elasticache_memcached_cluster': 'aws_elasticache_cluster',
        'elasticache_replication_group': 'aws_elasticache_replication_group',
        'elasticache_parameter_group': 'aws_elasticache_parameter_group',
        'elasticache_subnet_group': 'aws_elasticache_subnet_group',
        
        # Security & Identity
        'iam_role': 'aws_iam_role',
        'iam_roles': 'aws_iam_role',
        'iam_policy': 'aws_iam_policy',
        'iam_policies': 'aws_iam_policy',
        'key_pair': 'aws_key_pair',
        'key_pairs': 'aws_key_pair',
        'acm_certificate': 'aws_acm_certificate',
        'secretsmanager_secret': 'aws_secretsmanager_secret',
        'secretsmanager_secret_version': 'aws_secretsmanager_secret_version',
        
        # DNS
        'route53_zone': 'aws_route53_zone',
        'route53_record': 'aws_route53_record',
        
        # CDN
        'cloudfront_distribution': 'aws_cloudfront_distribution',
        'cloudfront_cache_policy': 'aws_cloudfront_cache_policy',
        'cloudfront_origin_request_policy': 'aws_cloudfront_origin_request_policy',
        'cloudfront_origin_access_control': 'aws_cloudfront_origin_access_control',
        
        # Monitoring
        'cloudwatch_alarm': 'aws_cloudwatch_metric_alarm',
        'cloudwatch_dashboard': 'aws_cloudwatch_dashboard',
        'cloudwatch_log_group': 'aws_cloudwatch_log_group',
        
        # Messaging
        'sns_topic': 'aws_sns_topic',
        'sns_subscription': 'aws_sns_topic_subscription',
        'sqs_queue': 'aws_sqs_queue',
        
        # Management
        'ssm_parameter': 'aws_ssm_parameter',
        'ssm_document': 'aws_ssm_document',
        'ssm_maintenance_window': 'aws_ssm_maintenance_window',
        
        # Container
        'ecr_repository': 'aws_ecr_repository',
        'ecs_cluster': 'aws_ecs_cluster',
        'ecs_service': 'aws_ecs_service',
        'ecs_task_definition': 'aws_ecs_task_definition',
    }
    
    # Azure resource type mappings
    azure_mappings = {
        'azure_virtual_machine': 'azurerm_linux_virtual_machine',  # Default to Linux, template handles OS detection
        'azure_function_app': 'azurerm_linux_function_app',  # Default to Linux, template handles OS detection
        'azure_linux_function_app': 'azurerm_linux_function_app',
        'azure_windows_function_app': 'azurerm_windows_function_app',
        'azure_vmss': 'azurerm_linux_virtual_machine_scale_set',  # Default to Linux
        'azure_web_app': 'azurerm_linux_web_app',  # Default to Linux
        'azure_linux_web_app': 'azurerm_linux_web_app',
        'azure_windows_web_app': 'azurerm_windows_web_app',
        'azure_app_service_plan': 'azurerm_service_plan',  # Updated resource type
        'azure_managed_disk': 'azurerm_managed_disk',
        'azure_virtual_network': 'azurerm_virtual_network',
        'azure_subnet': 'azurerm_subnet',
        'azure_network_security_group': 'azurerm_network_security_group',
        'azure_network_interface': 'azurerm_network_interface',
        'azure_storage_account': 'azurerm_storage_account',
        'azure_resource_group': 'azurerm_resource_group',
        'azure_lb': 'azurerm_lb',

        # DNS
        'azure_dns_zone': 'azurerm_dns_zone',
        'azure_dns_a_record': 'azurerm_dns_a_record',
        'azure_dns_cname_record': 'azurerm_dns_cname_record',
        'azure_dns_txt_record': 'azurerm_dns_txt_record',
        'azure_dns_mx_record': 'azurerm_dns_mx_record',
        'azure_dns_ns_record': 'azurerm_dns_ns_record',
        'azure_dns_srv_record': 'azurerm_dns_srv_record',
        'azure_dns_ptr_record': 'azurerm_dns_ptr_record',

        # Service Bus
        'azure_servicebus_namespace': 'azurerm_servicebus_namespace',
        'azure_servicebus_queue': 'azurerm_servicebus_queue',
        'azure_servicebus_topic': 'azurerm_servicebus_topic',
        'azure_servicebus_subscription': 'azurerm_servicebus_subscription',

        # Event Hub
        'azure_eventhub_namespace': 'azurerm_eventhub_namespace',
        'azure_eventhub': 'azurerm_eventhub',
        'azure_eventhub_consumer_group': 'azurerm_eventhub_consumer_group',

        # Log Analytics
        'azure_log_analytics_workspace': 'azurerm_log_analytics_workspace',

        # Monitor
        'azure_monitor_action_group': 'azurerm_monitor_action_group',

        # Identity & Access
        'azure_role_assignment': 'azurerm_role_assignment',
        'azure_user_assigned_identity': 'azurerm_user_assigned_identity',

        # Compute & Web
        'azure_availability_set': 'azurerm_availability_set',
        'azure_image': 'azurerm_image',
        'azure_snapshot': 'azurerm_snapshot',
        'azure_kubernetes_cluster': 'azurerm_kubernetes_cluster',
        'azure_kubernetes_cluster_node_pool': 'azurerm_kubernetes_cluster_node_pool',
        'azure_container_registry': 'azurerm_container_registry',
        'azure_application_gateway': 'azurerm_application_gateway',

        # Networking
        'azure_public_ip': 'azurerm_public_ip',
        'azure_nat_gateway': 'azurerm_nat_gateway',
        'azure_route_table': 'azurerm_route_table',

        # Caching
        'azure_redis_cache': 'azurerm_redis_cache',

        # Monitoring
        'azure_monitor_metric_alert': 'azurerm_monitor_metric_alert',
        'azure_portal_dashboard': 'azurerm_portal_dashboard',

        # Identity & Security
        'azure_key_vault': 'azurerm_key_vault',
        'azure_key_vault_secret': 'azurerm_key_vault_secret',
        'azure_key_vault_key': 'azurerm_key_vault_key',
        'azure_key_vault_certificate': 'azurerm_key_vault_certificate',
        'azure_role_definition': 'azurerm_role_definition',
        'azure_ssh_key': 'azurerm_ssh_public_key',
        'azure_ssh_public_key': 'azurerm_ssh_public_key',

        # Automation
        'azure_automation_account': 'azurerm_automation_account',
        'azure_automation_runbook': 'azurerm_automation_runbook',

        # API Management
        'azure_api_management': 'azurerm_api_management',
        'azure_api_management_api': 'azurerm_api_management_api',

        # CDN & Storage
        'azure_cdn_profile': 'azurerm_cdn_profile',
        'azure_cdn_endpoint': 'azurerm_cdn_endpoint',
        'azure_storage_share': 'azurerm_storage_share',

        # Databases
        'azure_sql_server': 'azurerm_mssql_server',
        'azure_sql_database': 'azurerm_mssql_database',
        'azure_sql_elastic_pool': 'azurerm_mssql_elasticpool',

        # Short names
        'vm': 'azurerm_linux_virtual_machine',
        'vms': 'azurerm_linux_virtual_machine',
        'disk': 'azurerm_managed_disk',
        'disks': 'azurerm_managed_disk',
        'vnet': 'azurerm_virtual_network',
        'vnets': 'azurerm_virtual_network',
        'nsg': 'azurerm_network_security_group',
        'nsgs': 'azurerm_network_security_group',
    }
    
    # GCP resource type mappings
    gcp_mappings = {
        'gcp_instance': 'google_compute_instance',
        'gcp_disk': 'google_compute_disk',
        'gcp_network': 'google_compute_network',
        'gcp_subnet': 'google_compute_subnetwork',
        'gcp_firewall': 'google_compute_firewall',
        'gcp_bucket': 'google_storage_bucket',
        'gcp_backend_service': 'google_compute_backend_service',
        'gcp_url_map': 'google_compute_url_map',
        'gcp_target_https_proxy': 'google_compute_target_https_proxy',
        'gcp_global_forwarding_rule': 'google_compute_global_forwarding_rule',
        'gcp_gke_cluster': 'google_container_cluster',
        'gcp_gke_node_pool': 'google_container_node_pool',
        'gcp_pubsub_topic': 'google_pubsub_topic',
        'gcp_pubsub_subscription': 'google_pubsub_subscription',
        'gcp_secret': 'google_secret_manager_secret',
        'gcp_sql_instance': 'google_sql_database_instance',
        'gcp_sql_database': 'google_sql_database',
        'gcp_cloud_run_service': 'google_cloud_run_service',
        'gcp_memorystore_redis': 'google_redis_instance',
        'gcp_memorystore_memcached': 'google_memcache_instance',
        'gcp_backend_buckets': 'google_compute_backend_bucket',
        'gcp_api_gateway_api': 'google_api_gateway_api',
        'gcp_certificate': 'google_certificate_manager_certificate',
        'gcp_certificate_map': 'google_certificate_manager_certificate_map',
        'gcp_certificate_manager_certificate': 'google_certificate_manager_certificate',
        'gcp_certificate_manager_certificate_map': 'google_certificate_manager_certificate_map',
        'gcp_cloud_function': 'google_cloudfunctions_function',
        'gcp_cloudfunctions_function': 'google_cloudfunctions_function',
        'gcp_cloud_tasks_queue': 'google_cloud_tasks_queue',
        'gcp_container_registry': 'google_container_registry',
        'gcp_container_registries': 'google_container_registry',
        'gcp_dns_managed_zones': 'google_dns_managed_zone',
        'gcp_eventarc_trigger': 'google_eventarc_trigger',
        'gcp_firestore_database': 'google_firestore_database',
        'gcp_health_check': 'google_compute_health_check',
        'gcp_image': 'google_compute_image',
        'gcp_instance_group': 'google_compute_instance_group',
        'gcp_instance_template': 'google_compute_instance_template',
        'gcp_kms_crypto_key': 'google_kms_crypto_key',
        'gcp_kms_key_ring': 'google_kms_key_ring',
        'gcp_monitoring_alert_policies': 'google_monitoring_alert_policy',
        'gcp_router': 'google_compute_router',
        'gcp_service_account': 'google_service_account',
        'gcp_service_accounts': 'google_service_account',
        'gcp_snapshot': 'google_compute_snapshot',
        'gcp_spanner_instance': 'google_spanner_instance',
        'gcp_vpn_gateway': 'google_compute_vpn_gateway',
        'gcp_workflows_workflow': 'google_workflows_workflow',
        'gcp_workflows': 'google_workflows_workflow',
        'gcp_bucket_iam_binding': 'google_storage_bucket_iam_binding',
        'gcp_bigtable_instance': 'google_bigtable_instance',
        'gcp_binary_authorization_policy': 'google_binary_authorization_policy',
        'gcp_certificate_authority': 'google_privateca_certificate_authority',
        'gcp_iam_roles': 'google_project_iam_custom_role',
        
        # Short names for GCP
        'instance': 'google_compute_instance',
        'disk': 'google_compute_disk',
        'network': 'google_compute_network',
        'firewall': 'google_compute_firewall',
        'bucket': 'google_storage_bucket',
    }
    
    # Apply mappings based on provider
    if provider == "aws":
        return aws_mappings.get(resource_type, f"aws_{resource_type}")
    elif provider == "azure":
        stripped = resource_type[6:] if resource_type.startswith("azure_") else resource_type
        return azure_mappings.get(resource_type, f"azurerm_{stripped}")
    elif provider == "gcp":
        return gcp_mappings.get(resource_type, f"google_{resource_type}")
    else:
        # Default to AWS if provider detection fails
        return aws_mappings.get(resource_type, f"aws_{resource_type}")


def derive_resource_name(resource_type: str, resource: Dict[str, Any], remote_id: str) -> str:
    """Generate a Terraform-safe name based on provider and resource info."""
    provider = detect_provider_from_resource_type(resource_type)

    # Prefer precomputed sanitized names if available
    if isinstance(resource, dict):
        pre_sanitized = resource.get("name_sanitized") or resource.get("domain_sanitized")
        if pre_sanitized:
            # Use the same name that .tf templates use, preserving case
            return str(pre_sanitized)

    base = str(remote_id)

    if provider == "aws":
        normalized_type = normalize_terraform_resource_type(resource_type, provider)

        if normalized_type == "aws_route53_record":
            # remote_id format: ZONEID_name_type[_setidentifier]
            # Include the zone identifier in the sanitized name
            if "_" in base:
                zone_id, rest = base.split("_", 1)
                zone_id = to_terraform_resource_name(zone_id)
                base = f"{zone_id}_{rest}"

        elif normalized_type == "aws_api_gateway_deployment":
            # remote_id format: restApiId/deploymentId
            if "/" in base:
                api_id, deploy_id = base.split("/", 1)
                base = f"{api_id}_deployment_{deploy_id}"
            else:
                base = strip_id_prefix(base)

        elif normalized_type == "aws_acm_certificate":
            domain = resource.get("DomainName") or resource.get("domain_name")
            if domain:
                base = f"certificate_{domain}"
            else:
                base = f"certificate_{strip_id_prefix(base)}"

        else:
            base = strip_id_prefix(base)

    elif provider in ("azure", "gcp"):
        base = resource.get("name") or base

    if "/" in base:
        base = base.replace("/", "_")

    return to_terraform_resource_name(base)


def generate_imports_file(
    resource_type: str,
    resources: List[Dict[str, Any]],
    remote_resource_id_key: str,
    output_dir: Path,
    composite_keys: Optional[List[str]] = None,
    provider: Optional[str] = None,
    provider_metadata: Optional[Dict[str, Any]] = None,
):
    """
    Generates a .json file containing the necessary data for terraform import commands.

    Args:
        resource_type: The resource type (can be short name like 'api_gateway_deployment' 
                      or full name like 'aws_api_gateway_deployment').
        resources: The list of resource dictionaries from the cloud provider API.
        remote_resource_id_key: The key in the resource dict that holds the unique ID.
        output_dir: The directory to save the file in.
        composite_keys (optional): A list of keys to join with '/' to form a composite ID,
                                   required for some resources like API Gateway methods.
        provider (optional): Cloud provider ('aws', 'azure', 'gcp'). Auto-detected if not provided.
        provider_metadata (optional): Additional metadata (e.g. account ID and region)
            associated with the scanned resources.
    """
    # Normalize the resource type to full Terraform resource type
    terraform_resource_type = normalize_terraform_resource_type(resource_type, provider)
    
    import_data = []
    for resource in resources:
        # Special handling for Lambda permissions
        if resource_type == 'lambda_permission' or terraform_resource_type == 'aws_lambda_permission':
            # Skip if no valid statement_id
            if not resource.get('statement_id'):
                print(f"Warning: Lambda permission without statement_id. Skipping.")
                continue
                
            # Build the import ID with qualifier if present
            function_name = resource.get('function_name', '')
            statement_id = resource.get('statement_id', '')
            qualifier = resource.get('qualifier')
            
            if qualifier:
                remote_id = f"{function_name}:{qualifier}/{statement_id}"
            else:
                remote_id = f"{function_name}/{statement_id}"
                
        elif composite_keys:
            # Build the ID from multiple keys, e.g., "api_id/resource_id/method".
            # This is necessary for many API Gateway resources.
            try:
                remote_id = "/".join([str(resource[key]) for key in composite_keys])
            except KeyError as e:
                print(f"Warning: Missing key {e} when building composite ID for a {terraform_resource_type}. Skipping.")
                continue
        else:
            remote_id = resource.get(remote_resource_id_key)

        if not remote_id:
            print(f"Warning: Could not determine remote ID for a {terraform_resource_type} using key '{remote_resource_id_key}'. Skipping.")
            continue

        # Create a sanitized, unique name for the resource in the Terraform state
        sanitized_name = derive_resource_name(resource_type, resource, remote_id)
        
        # Transform resource data to match template expectations (flatten Azure properties)
        processed_resource_data = flatten_azure_resource_properties(resource, resource_type)
        
        entry = {
            "resource_type": terraform_resource_type,  # Now uses full Terraform resource type
            "resource_name": sanitized_name,
            "remote_id": remote_id,
            "resource_data": processed_resource_data,
        }
        # Store the original scanned resource for later use by helper commands
        entry["scanned_data"] = resource
        if provider_metadata is not None:
            entry["provider_metadata"] = provider_metadata

        import_data.append(entry)
    
    # Use AWS-style naming: strip provider prefix for consistency with .tf files
    from .writer import get_terraform_filename
    tf_filename = get_terraform_filename(resource_type)
    base_name = tf_filename.replace('.tf', '')  # container_registry from container_registry.tf
    import_file = output_dir / f"{base_name}_import.json"
    
    try:
        with open(import_file, "w", encoding="utf-8") as f:
            # Use default=str so datetime and other objects are serialised
            # rather than causing a TypeError when dumps encounters them.
            json.dump(import_data, f, indent=2, default=str)
        print(f"Generated import file: {import_file} with {len(import_data)} resources")
    except IOError as e:
        print(f"Error writing import file {import_file}: {e}")


def read_import_file(import_file: Path) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Read and validate an import file.

    Returns:
        A tuple ``(entries, error)`` where ``entries`` is the list of import
        definitions and ``error`` contains any non JSON-decode related problem.

    Raises:
        ValueError: If the file contains invalid JSON.
    """

    try:
        with open(import_file, "r") as f:
            import_data = json.load(f)
    except json.JSONDecodeError as e:
        # Surface JSON errors to the caller so the filename can be reported
        raise ValueError(f"Invalid JSON: {e}") from e
    except IOError as e:
        return [], str(e)

    # Ensure all entries have proper resource types
    normalized_data: List[Dict[str, Any]] = []
    for entry in import_data:
        if isinstance(entry, dict):
            resource_type = entry.get("resource_type", "")
            normalized_type = normalize_terraform_resource_type(resource_type)

            normalized_entry = dict(entry)
            normalized_entry["resource_type"] = normalized_type
            # Preserve any scanned resource information for downstream helpers
            if "scanned_data" in entry:
                normalized_entry["scanned_data"] = entry["scanned_data"]
            normalized_data.append(normalized_entry)
        else:
            normalized_data.append(entry)

    return normalized_data, None


def validate_import_file(import_file: Path) -> List[str]:
    """
    Validate an import file for common issues.
    
    Returns:
        List of validation errors.
    """
    errors = []
    
    try:
        import_data, error = read_import_file(import_file)
        if error:
            errors.append(f"Failed to read file: {error}")
            return errors
    
        for i, entry in enumerate(import_data):
            if not isinstance(entry, dict):
                errors.append(f"Entry {i}: Not a dictionary")
                continue
            
            # Check required fields
            required_fields = ['resource_type', 'resource_name', 'remote_id']
            for field in required_fields:
                if field not in entry:
                    errors.append(f"Entry {i}: Missing required field '{field}'")
                elif not entry[field]:
                    errors.append(f"Entry {i}: Empty value for field '{field}'")
            
            # Validate resource type format
            resource_type = entry.get('resource_type', '')
            if resource_type and not any(resource_type.startswith(p) for p in ['aws_', 'azurerm_', 'google_']):
                errors.append(f"Entry {i}: Resource type '{resource_type}' should have provider prefix")
            
            # Validate resource name format (Terraform identifier rules)
            resource_name = entry.get('resource_name', '')
            if resource_name and not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', resource_name):
                errors.append(f"Entry {i}: Invalid resource name '{resource_name}' (must match Terraform identifier rules)")
    
    except Exception as e:
        errors.append(f"Failed to validate file: {e}")
    
    return errors
