"""Unit tests for Azure AKS Clusters module."""

import pytest
from unittest.mock import Mock, patch, call
from pathlib import Path

from terraback.cli.azure.container.aks_clusters import (
    scan_aks_clusters,
    scan_aks_node_pools,
    _format_default_node_pool,
    _format_identity,
    _format_network_profile,
    _format_addon_profiles,
    _format_auto_scaler_profile,
    _format_azure_ad_profile,
    _get_node_pools_for_cluster,
    _format_node_pool_properties
)


class TestScanAKSClusters:
    """Test AKS cluster scanning."""
    
    @patch('terraback.cli.azure.container.aks_clusters.get_azure_client')
    @patch('terraback.cli.azure.container.aks_clusters.generate_tf')
    @patch('terraback.cli.azure.container.aks_clusters.generate_imports_file')
    def test_scan_aks_clusters_success(self, mock_imports, mock_generate, mock_client):
        """Test successful scanning of AKS clusters."""
        # Mock Azure client and clusters
        mock_aks_client = Mock()
        mock_client.return_value = mock_aks_client
        
        # Mock default node pool
        mock_node_pool = Mock(
            name="nodepool1",
            count=3,
            vm_size="Standard_D2_v2",
            os_disk_size_gb=128,
            vnet_subnet_id="/subscriptions/123/subnet1",
            max_pods=30,
            os_type="Linux",
            enable_auto_scaling=True,
            min_count=1,
            max_count=5,
            availability_zones=["1", "2"],
            enable_node_public_ip=False,
            node_labels={"env": "prod"},
            node_taints=[]
        )
        
        mock_cluster = Mock()
        mock_cluster.name = "test-aks"
        mock_cluster.id = "/subscriptions/123/resourceGroups/test-rg/providers/Microsoft.ContainerService/managedClusters/test-aks"
        mock_cluster.location = "eastus"
        mock_cluster.tags = {"env": "test"}
        mock_cluster.agent_pool_profiles = [mock_node_pool]
        
        # Mock identity
        mock_cluster.identity = Mock(
            type="SystemAssigned",
            principal_id="123-456",
            tenant_id="789-012"
        )
        mock_cluster.service_principal_profile = None
        
        # Mock network profile
        mock_cluster.network_profile = Mock(
            network_plugin="azure",
            network_policy="calico",
            dns_service_ip="10.0.0.10",
            docker_bridge_cidr="172.17.0.1/16",
            pod_cidr=None,
            service_cidr="10.0.0.0/16",
            load_balancer_sku="standard",
            outbound_type="loadBalancer"
        )
        
        # Mock addon profiles
        mock_cluster.addon_profiles = {
            "httpApplicationRouting": Mock(enabled=False),
            "omsagent": Mock(enabled=True, config={"logAnalyticsWorkspaceResourceID": "/subscriptions/123/workspace"})
        }
        
        # Mock auto scaler profile
        mock_cluster.auto_scaler_profile = Mock(
            balance_similar_node_groups="true",
            expander="random",
            max_graceful_termination_sec="600",
            max_node_provision_time="15m",
            ok_total_unready_count="3",
            max_total_unready_percentage="45",
            new_pod_scale_up_delay="0s",
            scale_down_delay_after_add="10m",
            scale_down_delay_after_delete="10s",
            scale_down_delay_after_failure="3m",
            scale_down_unneeded_time="10m",
            scale_down_unready_time="20m",
            scale_down_utilization_threshold="0.5",
            skip_nodes_with_local_storage="true",
            skip_nodes_with_system_pods="true"
        )
        
        # Mock Azure AD profile
        mock_cluster.aad_profile = Mock(
            managed=True,
            admin_group_object_i_ds=["group1", "group2"],
            tenant_id="tenant123"
        )
        
        mock_aks_client.managed_clusters.list.return_value = [mock_cluster]
        
        # Run scan
        output_dir = Path("test_output")
        result = scan_aks_clusters(output_dir, "sub123")
        
        # Verify results
        assert len(result) == 1
        assert result[0]['name'] == "test-aks"
        assert result[0]['resource_group_name'] == "test-rg"
        assert result[0]['default_node_pool_formatted']['name'] == "nodepool1"
        assert result[0]['identity_formatted']['type'] == "SystemAssigned"
        assert result[0]['network_profile_formatted']['network_plugin'] == "azure"
        assert result[0]['addon_profiles_formatted']['omsagent']['enabled'] == True
        assert result[0]['auto_scaler_profile_formatted']['expander'] == "random"
        assert result[0]['azure_active_directory_role_based_access_control_formatted']['managed'] == True
        
        # Verify file generation was called
        mock_generate.assert_called_once()
        mock_imports.assert_called_once()
    
    @patch('terraback.cli.azure.container.aks_clusters.get_azure_client')
    def test_scan_aks_clusters_with_service_principal(self, mock_client):
        """Test scanning AKS cluster with service principal."""
        mock_aks_client = Mock()
        mock_client.return_value = mock_aks_client
        
        mock_cluster = Mock()
        mock_cluster.name = "test-aks-sp"
        mock_cluster.id = "/subscriptions/123/resourceGroups/test-rg/providers/Microsoft.ContainerService/managedClusters/test-aks-sp"
        mock_cluster.location = "eastus"
        mock_cluster.tags = {}
        mock_cluster.agent_pool_profiles = [Mock(name="default")]
        
        # Mock service principal
        mock_cluster.service_principal_profile = Mock(
            client_id="sp-client-id"
        )
        mock_cluster.identity = None
        
        # Minimal other properties
        mock_cluster.network_profile = None
        mock_cluster.addon_profiles = None
        mock_cluster.auto_scaler_profile = None
        mock_cluster.aad_profile = None
        
        mock_aks_client.managed_clusters.list.return_value = [mock_cluster]
        
        result = scan_aks_clusters(Path("test_output"), "sub123")
        
        assert len(result) == 1
        assert result[0]['service_principal_formatted']['client_id'] == "sp-client-id"
        assert result[0]['service_principal_formatted']['client_secret'] == "REDACTED"


class TestScanAKSNodePools:
    """Test AKS node pool scanning."""
    
    @patch('terraback.cli.azure.container.aks_clusters.scan_aks_clusters')
    @patch('terraback.cli.azure.container.aks_clusters.get_azure_client')
    @patch('terraback.cli.azure.container.aks_clusters.generate_tf')
    @patch('terraback.cli.azure.container.aks_clusters.generate_imports_file')
    def test_scan_aks_node_pools_success(self, mock_imports, mock_generate, mock_client, mock_scan_clusters):
        """Test successful scanning of AKS node pools."""
        # Mock clusters from scan
        mock_scan_clusters.return_value = [
            {
                'id': '/subscriptions/123/resourceGroups/test-rg/providers/Microsoft.ContainerService/managedClusters/test-aks',
                'name': 'test-aks',
                'resource_group_name': 'test-rg',
                'default_node_pool_formatted': {'name': 'nodepool1'}
            }
        ]
        
        # Mock Azure client
        mock_aks_client = Mock()
        mock_client.return_value = mock_aks_client
        
        # Mock additional node pools
        mock_pool1 = Mock(
            name="nodepool1",  # Default pool - should be skipped
            count=3,
            vm_size="Standard_D2_v2"
        )
        mock_pool2 = Mock(
            name="nodepool2",  # Additional pool
            count=2,
            vm_size="Standard_D4_v2",
            os_disk_size_gb=256,
            vnet_subnet_id="/subscriptions/123/subnet2",
            max_pods=50,
            os_type="Linux",
            enable_auto_scaling=True,
            min_count=2,
            max_count=10,
            availability_zones=["1", "2", "3"],
            enable_node_public_ip=True,
            node_labels={"workload": "gpu"},
            node_taints=["gpu=true:NoSchedule"],
            mode="User",
            orchestrator_version="1.21.2"
        )
        
        mock_aks_client.agent_pools.list.return_value = [mock_pool1, mock_pool2]
        
        # Run scan
        output_dir = Path("test_output")
        result = scan_aks_node_pools(output_dir, "sub123")
        
        # Verify results - only additional pool should be included
        assert len(result) == 1
        assert result[0]['name'] == "nodepool2"
        assert result[0]['node_count'] == 2
        assert result[0]['vm_size'] == "Standard_D4_v2"
        assert result[0]['mode'] == "User"
        
        # Verify file generation was called
        mock_generate.assert_called_once()
        mock_imports.assert_called_once()


class TestFormatFunctions:
    """Test formatting helper functions."""
    
    def test_format_default_node_pool(self):
        """Test default node pool formatting."""
        cluster_dict = {}
        cluster = Mock()
        cluster.agent_pool_profiles = [
            Mock(
                name="default",
                count=3,
                vm_size="Standard_DS2_v2",
                os_disk_size_gb=100,
                vnet_subnet_id="/subscriptions/123/subnet",
                max_pods=110,
                os_type="Linux",
                enable_auto_scaling=False,
                min_count=None,
                max_count=None,
                availability_zones=None,
                enable_node_public_ip=False,
                node_labels=None,
                node_taints=None
            )
        ]
        
        _format_default_node_pool(cluster_dict, cluster)
        
        assert cluster_dict['default_node_pool_formatted']['name'] == "default"
        assert cluster_dict['default_node_pool_formatted']['node_count'] == 3
        assert cluster_dict['default_node_pool_formatted']['vm_size'] == "Standard_DS2_v2"
        assert cluster_dict['default_node_pool_formatted']['enable_auto_scaling'] == False
    
    def test_format_identity_managed(self):
        """Test managed identity formatting."""
        cluster_dict = {}
        cluster = Mock()
        cluster.identity = Mock(
            type="SystemAssigned",
            principal_id="principal123",
            tenant_id="tenant456"
        )
        cluster.service_principal_profile = None
        
        _format_identity(cluster_dict, cluster)
        
        assert cluster_dict['identity_formatted']['type'] == "SystemAssigned"
        assert cluster_dict['identity_formatted']['principal_id'] == "principal123"
        assert 'service_principal_formatted' not in cluster_dict
    
    def test_format_identity_service_principal(self):
        """Test service principal formatting."""
        cluster_dict = {}
        cluster = Mock()
        cluster.service_principal_profile = Mock(
            client_id="client123"
        )
        cluster.identity = None
        
        _format_identity(cluster_dict, cluster)
        
        assert cluster_dict['service_principal_formatted']['client_id'] == "client123"
        assert cluster_dict['service_principal_formatted']['client_secret'] == "REDACTED"
        assert 'identity_formatted' not in cluster_dict
    
    def test_format_network_profile(self):
        """Test network profile formatting."""
        cluster_dict = {}
        cluster = Mock()
        cluster.network_profile = Mock(
            network_plugin="kubenet",
            network_policy=None,
            dns_service_ip="10.0.0.10",
            docker_bridge_cidr="172.17.0.1/16",
            pod_cidr="10.244.0.0/16",
            service_cidr="10.0.0.0/16",
            load_balancer_sku="basic",
            outbound_type="loadBalancer"
        )
        
        _format_network_profile(cluster_dict, cluster)
        
        assert cluster_dict['network_profile_formatted']['network_plugin'] == "kubenet"
        assert cluster_dict['network_profile_formatted']['pod_cidr'] == "10.244.0.0/16"
        assert cluster_dict['network_profile_formatted']['load_balancer_sku'] == "basic"
    
    def test_format_addon_profiles(self):
        """Test addon profiles formatting."""
        cluster_dict = {}
        cluster = Mock()
        cluster.addon_profiles = {
            "azureKeyvaultSecretsProvider": Mock(enabled=True, config={"enableSecretRotation": "true"}),
            "httpApplicationRouting": Mock(enabled=False, config=None),
            "omsagent": Mock(enabled=True, config={"logAnalyticsWorkspaceResourceID": "/subscriptions/123/workspace"})
        }
        
        _format_addon_profiles(cluster_dict, cluster)
        
        # Only enabled addons should be included
        assert len(cluster_dict['addon_profiles_formatted']) == 2
        assert 'azureKeyvaultSecretsProvider' in cluster_dict['addon_profiles_formatted']
        assert 'omsagent' in cluster_dict['addon_profiles_formatted']
        assert 'httpApplicationRouting' not in cluster_dict['addon_profiles_formatted']
    
    def test_format_node_pool_properties(self):
        """Test node pool properties formatting."""
        pool_dict = {}
        pool = Mock(
            count=5,
            vm_size="Standard_F8s_v2",
            os_disk_size_gb=200,
            vnet_subnet_id="/subscriptions/123/subnet",
            max_pods=60,
            os_type="Linux",
            enable_auto_scaling=True,
            min_count=3,
            max_count=10,
            availability_zones=["1", "2"],
            enable_node_public_ip=True,
            node_labels={"gpu": "true", "tier": "compute"},
            node_taints=["gpu=true:NoSchedule"],
            mode="User",
            orchestrator_version="1.21.2"
        )
        
        _format_node_pool_properties(pool_dict, pool)
        
        assert pool_dict['node_count'] == 5
        assert pool_dict['vm_size'] == "Standard_F8s_v2"
        assert pool_dict['enable_auto_scaling'] == True
        assert pool_dict['min_count'] == 3
        assert pool_dict['max_count'] == 10
        assert pool_dict['availability_zones'] == ["1", "2"]
        assert pool_dict['node_labels'] == {"gpu": "true", "tier": "compute"}
        assert pool_dict['mode'] == "User"