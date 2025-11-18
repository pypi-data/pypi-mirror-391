"""Required fields for stub generation across all cloud providers."""

def _parse_route53_record_id(record_id: str):
    """Extract zone ID, record name, and type from composite import ID."""
    if not isinstance(record_id, str):
        return None, None, None
    parts = record_id.split("_")
    if len(parts) < 3:
        return None, None, None
    zone_id = parts[0]
    record_type = parts[-1]
    record_name = "_".join(parts[1:-1])
    return zone_id, record_name.rstrip(".") or None, record_type

def _parse_sns_subscription_id(subscription_arn: str):
    """Return the topic ARN portion from an SNS subscription ARN."""
    if not isinstance(subscription_arn, str):
        return None
    parts = subscription_arn.split(":")
    if len(parts) < 7:
        return None
    return ":".join(parts[:-1])

def get_scanned_value(entry, field):
    """Return value from scanned or resource data if available."""
    data = entry.get("scanned_data") or entry.get("resource_data")
    if isinstance(data, dict):
        if field in data:
            return data[field]
        # allow case-insensitive lookup for convenience
        for k, v in data.items():
            if isinstance(k, str) and k.lower() == field.lower():
                return v
    return None

# AWS Required Fields
AWS_REQUIRED_FIELDS = {
    'aws_api_gateway_deployment': {
        'rest_api_id': lambda r: get_scanned_value(r, 'restApiId')
        or get_scanned_value(r, 'rest_api_id')
        or (r['id'].split('/')[0] if '/' in r['id'] else None)
    },
    'aws_api_gateway_method': {
        'rest_api_id': lambda r: get_scanned_value(r, 'rest_api_id')
        or get_scanned_value(r, 'restApiId')
        or (r['id'].split('/')[0] if '/' in r['id'] else None),
        'resource_id': lambda r: get_scanned_value(r, 'resource_id')
        or (r['id'].split('/')[1] if '/' in r['id'] else None),
        'http_method': lambda r: get_scanned_value(r, 'http_method')
        or (r['id'].split('/')[2] if '/' in r['id'] else None),
        'authorization': lambda r: get_scanned_value(r, 'authorizationType')
        or get_scanned_value(r, 'authorization')
        or 'NONE'
    },
    'aws_api_gateway_resource': {
        'rest_api_id': lambda r: get_scanned_value(r, 'restApiId')
        or get_scanned_value(r, 'rest_api_id')
        or (r['id'].split('/')[0] if '/' in r['id'] else None),
        'parent_id': lambda r: get_scanned_value(r, 'parentId')
        or get_scanned_value(r, 'parent_id'),
        'path_part': lambda r: get_scanned_value(r, 'pathPart')
        or get_scanned_value(r, 'path_part')
    },
    'aws_api_gateway_rest_api': {
        'name': lambda r: get_scanned_value(r, 'name')
        or r.get('name')
        or r['id']
    },
    'aws_route53_record': {
        'zone_id': lambda r: get_scanned_value(r, 'ZoneId')
        or _parse_route53_record_id(r.get('id', ''))[0],
        'name': lambda r: (
            get_scanned_value(r, 'Name')
            or _parse_route53_record_id(r.get('id', ''))[1]
        ).rstrip('.') if (
            get_scanned_value(r, 'Name')
            or _parse_route53_record_id(r.get('id', ''))[1]
        ) else None,
        'type': lambda r: get_scanned_value(r, 'Type')
        or _parse_route53_record_id(r.get('id', ''))[2],
        'records': lambda r: None
        if get_scanned_value(r, 'AliasTarget')
        else [
            rec.get('Value') if isinstance(rec, dict) else rec
            for rec in (get_scanned_value(r, 'ResourceRecords') or [])
        ] if get_scanned_value(r, 'ResourceRecords') else None,
        'ttl': lambda r: None
        if get_scanned_value(r, 'AliasTarget')
        else get_scanned_value(r, 'TTL'),
        'alias': lambda r: (
            {
                'name': get_scanned_value(r, 'AliasTarget').get('DNSName'),
                'zone_id': get_scanned_value(r, 'AliasTarget').get('HostedZoneId'),
                'evaluate_target_health': bool(
                    get_scanned_value(r, 'AliasTarget').get('EvaluateTargetHealth', False)
                ),
            }
            if get_scanned_value(r, 'AliasTarget')
            else None
        ),
    },
    'aws_route53_zone': {
        'name': lambda r: get_scanned_value(r, 'Name')
    },
    'aws_route_table': {
        'vpc_id': lambda r: get_scanned_value(r, 'VpcId')
    },
    'aws_secretsmanager_secret_version': {
        # Use the ARN portion of the composite ID when available so the
        # placeholder matches the value populated by `terraform import`.
        'secret_id': (
            lambda r: get_scanned_value(r, 'SecretArn')
            or get_scanned_value(r, 'SecretId')
            or (r['id'].split('|')[0] if '|' in r['id'] else r['name'].rsplit('_', 2)[0] if '_' in r['name'] else None)
        )
    },
    'aws_sns_topic_subscription': {
        'topic_arn': lambda r: get_scanned_value(r, 'TopicArn')
        or _parse_sns_subscription_id(r.get('id', '')),
        'protocol': lambda r: get_scanned_value(r, 'Protocol'),
        'endpoint': lambda r: get_scanned_value(r, 'Endpoint')
    },
    'aws_acm_certificate': {
        'domain_name': lambda r: get_scanned_value(r, 'DomainName')
    },
    'aws_instance': {
        'ami': lambda r: get_scanned_value(r, 'ImageId'),
        'instance_type': lambda r: get_scanned_value(r, 'InstanceType')
    },
    'aws_security_group': {
        'name': lambda r: get_scanned_value(r, 'GroupName')
        or r.get('name')
    },
    'aws_subnet': {
        'vpc_id': lambda r: get_scanned_value(r, 'VpcId'),
        'cidr_block': lambda r: get_scanned_value(r, 'CidrBlock')
    },
    'aws_vpc': {
        'cidr_block': lambda r: get_scanned_value(r, 'CidrBlock')
    },
    'aws_key_pair': {
        'key_name': lambda r: get_scanned_value(r, 'KeyName')
        or r.get('name'),
        'public_key': lambda r: get_scanned_value(r, 'KeyMaterial')
        or get_scanned_value(r, 'public_key')
        or 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... (placeholder - replace with actual public key)'
    },
    'aws_network_interface': {
        'subnet_id': lambda r: get_scanned_value(r, 'SubnetId')
        or get_scanned_value(r, 'subnet_id')
    },
    'aws_db_subnet_group': {
        'name': lambda r: get_scanned_value(r, 'DBSubnetGroupName')
        or r.get('name'),
        'subnet_ids': lambda r: [
            subnet.get('SubnetIdentifier') if isinstance(subnet, dict) else subnet
            for subnet in (get_scanned_value(r, 'Subnets') or [])
        ] if get_scanned_value(r, 'Subnets') else []
    },
    'aws_api_gateway_integration': {
        'rest_api_id': lambda r: get_scanned_value(r, 'rest_api_id')
        or r.get('rest_api_id'),
        'resource_id': lambda r: get_scanned_value(r, 'resource_id')
        or r.get('resource_id'),
        'http_method': lambda r: get_scanned_value(r, 'http_method')
        or r.get('http_method'),
        'type': lambda r: get_scanned_value(r, 'type')
        or r.get('type')
        or 'MOCK'
    },
    'aws_lambda_permission': {
        'function_name': lambda r: get_scanned_value(r, 'function_name')
        or r.get('function_name'),
        'principal': lambda r: get_scanned_value(r, 'principal')
        or 'apigateway.amazonaws.com',
        'action': lambda r: get_scanned_value(r, 'action')
        or 'lambda:InvokeFunction'
    }
}

# Azure Required Fields
AZURE_REQUIRED_FIELDS = {
    'azurerm_resource_group': {
        'location': lambda r: r.get('scanned_data', {}).get('location') or 'eastus',
        'name': lambda r: r.get('name')
    },
    'azurerm_virtual_network': {
        'name': lambda r: r.get('name'),
        'location': lambda r: r.get('scanned_data', {}).get('location'),
        'resource_group_name': lambda r: r.get('scanned_data', {}).get('resource_group_name')
        or (r.get('id', '').split('/')[4] if len(r.get('id', '').split('/')) > 4 else None),
        'address_space': lambda r: r.get('scanned_data', {}).get('properties', {}).get('addressSpace', {}).get('addressPrefixes', ['10.0.0.0/16'])
    },
    'azurerm_subnet': {
        'name': lambda r: r.get('name'),
        'resource_group_name': lambda r: r.get('scanned_data', {}).get('resource_group_name')
        or (r.get('id', '').split('/')[4] if len(r.get('id', '').split('/')) > 4 else None),
        'virtual_network_name': lambda r: r.get('scanned_data', {}).get('virtual_network_name')
        or (r.get('id', '').split('/')[8] if len(r.get('id', '').split('/')) > 8 else None),
        'address_prefixes': lambda r: r.get('scanned_data', {}).get('properties', {}).get('addressPrefixes', ['10.0.1.0/24'])
    },
    'azurerm_storage_account': {
        'name': lambda r: r.get('name'),
        'resource_group_name': lambda r: r.get('scanned_data', {}).get('resource_group_name')
        or (r.get('id', '').split('/')[4] if len(r.get('id', '').split('/')) > 4 else None),
        'location': lambda r: r.get('scanned_data', {}).get('location'),
        'account_tier': lambda r: r.get('scanned_data', {}).get('sku', {}).get('tier', 'Standard'),
        'account_replication_type': lambda r: r.get('scanned_data', {}).get('sku', {}).get('name', 'LRS').replace('Standard_', '').replace('Premium_', '')
    },
    'azurerm_network_security_group': {
        'name': lambda r: r.get('name'),
        'location': lambda r: r.get('scanned_data', {}).get('location'),
        'resource_group_name': lambda r: r.get('scanned_data', {}).get('resource_group_name')
        or (r.get('id', '').split('/')[4] if len(r.get('id', '').split('/')) > 4 else None)
    },
    'azurerm_virtual_machine': {
        'name': lambda r: r.get('name'),
        'location': lambda r: get_scanned_value(r, 'location'),
        'resource_group_name': lambda r: get_scanned_value(r, 'resource_group_name')
        or (r.get('id', '').split('/')[4] if len(r.get('id', '').split('/')) > 4 else None),
        'size': lambda r: r.get('scanned_data', {}).get('properties', {}).get('hardwareProfile', {}).get('vmSize', 'Standard_B2s'),
        'admin_username': lambda r: 'adminuser'
    },
    'azurerm_linux_virtual_machine': {
        'name': lambda r: r.get('name'),
        'location': lambda r: r.get('scanned_data', {}).get('location'),
        'resource_group_name': lambda r: r.get('scanned_data', {}).get('resource_group_name')
        or (r.get('id', '').split('/')[4] if len(r.get('id', '').split('/')) > 4 else None),
        'size': lambda r: r.get('scanned_data', {}).get('properties', {}).get('hardwareProfile', {}).get('vmSize', 'Standard_B2s'),
        'admin_username': lambda r: 'adminuser',
        'disable_password_authentication': lambda r: True
    },
    'azurerm_windows_virtual_machine': {
        'name': lambda r: r.get('name'),
        'location': lambda r: r.get('scanned_data', {}).get('location'),
        'resource_group_name': lambda r: r.get('scanned_data', {}).get('resource_group_name')
        or (r.get('id', '').split('/')[4] if len(r.get('id', '').split('/')) > 4 else None),
        'size': lambda r: r.get('scanned_data', {}).get('properties', {}).get('hardwareProfile', {}).get('vmSize', 'Standard_B2s'),
        'admin_username': lambda r: 'adminuser',
        'admin_password': lambda r: 'ChangeMe123!'
    }
}

# GCP Required Fields
GCP_REQUIRED_FIELDS = {
    'google_compute_network': {
        'name': lambda r: r.get('name'),
        'auto_create_subnetworks': lambda r: r.get('scanned_data', {}).get('autoCreateSubnetworks', False)
    },
    'google_compute_subnetwork': {
        'name': lambda r: r.get('name'),
        'network': lambda r: r.get('scanned_data', {}).get('network')
        or (r.get('scanned_data', {}).get('network_link', '').split('/')[-1] if r.get('scanned_data', {}).get('network_link') else None),
        'ip_cidr_range': lambda r: r.get('scanned_data', {}).get('ipCidrRange', '10.0.0.0/24'),
        'region': lambda r: r.get('scanned_data', {}).get('region')
        or (r.get('id', '').split('/')[3] if len(r.get('id', '').split('/')) > 3 and r.get('id', '').split('/')[2] == 'regions' else None)
    },
    'google_compute_instance': {
        'name': lambda r: r.get('name'),
        'machine_type': lambda r: r.get('scanned_data', {}).get('machineType', '').split('/')[-1]
        or 'e2-micro',
        'zone': lambda r: r.get('scanned_data', {}).get('zone', '').split('/')[-1]
        or (r.get('id', '').split('/')[3] if len(r.get('id', '').split('/')) > 3 and r.get('id', '').split('/')[2] == 'zones' else None),
        'boot_disk': lambda r: {'initialize_params': {'image': 'debian-cloud/debian-11'}}
    },
    'google_storage_bucket': {
        'name': lambda r: r.get('name'),
        'location': lambda r: r.get('scanned_data', {}).get('location', 'US')
    },
    'google_compute_firewall': {
        'name': lambda r: r.get('name'),
        'network': lambda r: r.get('scanned_data', {}).get('network', '').split('/')[-1]
        or 'default'
    },
    'google_sql_database_instance': {
        'name': lambda r: r.get('name'),
        'database_version': lambda r: r.get('scanned_data', {}).get('databaseVersion', 'MYSQL_8_0'),
        'settings': lambda r: {'tier': r.get('scanned_data', {}).get('settings', {}).get('tier', 'db-f1-micro')}
    },
    'google_container_cluster': {
        'name': lambda r: r.get('name'),
        'location': lambda r: r.get('scanned_data', {}).get('location')
        or r.get('scanned_data', {}).get('zone')
    },
    'google_pubsub_topic': {
        'name': lambda r: r.get('name')
    },
    'google_pubsub_subscription': {
        'name': lambda r: r.get('name'),
        'topic': lambda r: r.get('scanned_data', {}).get('topic', '').split('/')[-1]
        or None
    }
}

def get_required_fields(resource_type: str) -> dict:
    """Get required fields for a resource type across all providers."""
    # Check AWS
    if resource_type in AWS_REQUIRED_FIELDS:
        return AWS_REQUIRED_FIELDS[resource_type]
    
    # Check Azure
    if resource_type in AZURE_REQUIRED_FIELDS:
        return AZURE_REQUIRED_FIELDS[resource_type]
    
    # Check GCP
    if resource_type in GCP_REQUIRED_FIELDS:
        return GCP_REQUIRED_FIELDS[resource_type]
    
    return {}