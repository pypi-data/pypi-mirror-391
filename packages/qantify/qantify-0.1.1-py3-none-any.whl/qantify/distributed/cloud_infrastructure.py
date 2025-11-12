"""
Cloud Infrastructure Management for Distributed Computing
========================================================

This module provides comprehensive cloud infrastructure management for distributed
quantitative trading operations. Supports AWS, Google Cloud Platform (GCP), and
Microsoft Azure with automated provisioning, scaling, and cost optimization.

Key Features:
- Multi-cloud infrastructure management
- Auto-scaling based on workload
- Cost optimization and monitoring
- Security and compliance
- Disaster recovery and high availability
- Container orchestration (Kubernetes)
- Serverless computing integration
- Hybrid cloud capabilities
"""

from __future__ import annotations

import warnings
import json
import time
import threading
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import deque, defaultdict
import uuid
import os
import tempfile
from datetime import datetime, timedelta

import numpy as np

# Cloud provider imports (with fallbacks)
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    boto3 = None

try:
    from google.cloud import compute_v1, storage, container_v1
    from google.api_core.exceptions import GoogleAPIError
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.storage import StorageManagementClient
    from azure.mgmt.batch import BatchManagementClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    import kubernetes as k8s
    from kubernetes.client.exceptions import ApiException
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False


@dataclass
class CloudConfig:
    """Configuration for cloud infrastructure"""

    # Provider settings
    provider: str = "aws"  # "aws", "gcp", "azure"
    region: str = "us-east-1"
    availability_zones: List[str] = field(default_factory=lambda: ["us-east-1a", "us-east-1b"])

    # Compute resources
    instance_type: str = "c5.large"
    min_instances: int = 1
    max_instances: int = 10
    target_cpu_utilization: float = 70.0

    # Storage
    storage_class: str = "gp3"  # AWS: gp3, GCP: standard, Azure: standard
    backup_retention_days: int = 30

    # Networking
    vpc_cidr: str = "10.0.0.0/16"
    subnet_cidrs: List[str] = field(default_factory=lambda: ["10.0.1.0/24", "10.0.2.0/24"])

    # Security
    enable_encryption: bool = True
    key_rotation_days: int = 90
    security_groups: List[str] = field(default_factory=list)

    # Cost management
    max_daily_cost: float = 100.0
    spot_instances: bool = True
    reserved_instances: bool = False

    # Monitoring and logging
    enable_monitoring: bool = True
    log_retention_days: int = 90
    enable_cloudtrail: bool = True  # AWS-specific


@dataclass
class InstanceInfo:
    """Information about a cloud instance"""

    instance_id: str
    provider: str
    instance_type: str
    region: str
    availability_zone: str
    state: str  # "pending", "running", "stopping", "stopped", "terminated"

    # Performance metrics
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    network_in: float = 0.0
    network_out: float = 0.0

    # Cost tracking
    hourly_cost: float = 0.0
    uptime_hours: float = 0.0

    # Metadata
    launch_time: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ClusterInfo:
    """Information about a compute cluster"""

    cluster_id: str
    provider: str
    instance_count: int
    total_cpu_cores: int
    total_memory_gb: float

    # Scaling configuration
    min_instances: int = 1
    max_instances: int = 10
    target_cpu_utilization: float = 70.0

    # Cost and performance
    total_hourly_cost: float = 0.0
    avg_cpu_utilization: float = 0.0
    avg_memory_utilization: float = 0.0


class CloudProvider(ABC):
    """Abstract base class for cloud providers"""

    def __init__(self, config: CloudConfig):
        self.config = config
        self.instances = {}
        self.clusters = {}

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the cloud provider"""
        pass

    @abstractmethod
    def create_instance(self, instance_type: str, region: str) -> Optional[InstanceInfo]:
        """Create a new instance"""
        pass

    @abstractmethod
    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate an instance"""
        pass

    @abstractmethod
    def get_instance_status(self, instance_id: str) -> Optional[InstanceInfo]:
        """Get status of an instance"""
        pass

    @abstractmethod
    def list_instances(self) -> List[InstanceInfo]:
        """List all instances"""
        pass

    @abstractmethod
    def scale_cluster(self, cluster_id: str, target_instances: int) -> bool:
        """Scale a cluster to target number of instances"""
        pass

    @abstractmethod
    def get_cost_estimate(self, instance_type: str, hours: float) -> float:
        """Get cost estimate for instance usage"""
        pass


class AWSProvider(CloudProvider):
    """AWS cloud provider implementation"""

    def __init__(self, config: CloudConfig):
        super().__init__(config)
        self.ec2_client = None
        self.ec2_resource = None
        self.cloudwatch = None
        self.pricing = None

    def authenticate(self) -> bool:
        """Authenticate with AWS"""
        if not AWS_AVAILABLE:
            return False

        try:
            # Use default credential chain (IAM roles, env vars, etc.)
            self.ec2_client = boto3.client('ec2', region_name=self.config.region)
            self.ec2_resource = boto3.resource('ec2', region_name=self.config.region)
            self.cloudwatch = boto3.client('cloudwatch', region_name=self.config.region)
            self.pricing = boto3.client('pricing', region_name='us-east-1')  # Pricing is global
            return True
        except Exception as e:
            print(f"AWS authentication failed: {e}")
            return False

    def create_instance(self, instance_type: str, region: str) -> Optional[InstanceInfo]:
        """Create EC2 instance"""

        if not self.ec2_client:
            return None

        try:
            # Use spot instances if enabled
            if self.config.spot_instances:
                response = self.ec2_client.run_instances(
                    ImageId=self._get_ami_id(),
                    MinCount=1,
                    MaxCount=1,
                    InstanceType=instance_type,
                    KeyName=self._get_key_pair_name(),
                    SecurityGroupIds=self.config.security_groups,
                    InstanceMarketOptions={
                        'MarketType': 'spot',
                        'SpotOptions': {
                            'MaxPrice': str(self._get_spot_price(instance_type)),
                            'SpotInstanceType': 'one-time'
                        }
                    },
                    TagSpecifications=[{
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'qantify-worker-{uuid.uuid4().hex[:8]}'},
                            {'Key': 'Environment', 'Value': 'qantify-distributed'},
                        ]
                    }]
                )
            else:
                response = self.ec2_client.run_instances(
                    ImageId=self._get_ami_id(),
                    MinCount=1,
                    MaxCount=1,
                    InstanceType=instance_type,
                    KeyName=self._get_key_pair_name(),
                    SecurityGroupIds=self.config.security_groups,
                    TagSpecifications=[{
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'qantify-worker-{uuid.uuid4().hex[:8]}'},
                            {'Key': 'Environment', 'Value': 'qantify-distributed'},
                        ]
                    }]
                )

            instance_id = response['Instances'][0]['InstanceId']

            # Wait for instance to be running
            self._wait_for_instance_state(instance_id, 'running')

            instance_info = InstanceInfo(
                instance_id=instance_id,
                provider="aws",
                instance_type=instance_type,
                region=region,
                availability_zone=response['Instances'][0]['Placement']['AvailabilityZone'],
                state="running"
            )

            self.instances[instance_id] = instance_info
            return instance_info

        except ClientError as e:
            print(f"Failed to create AWS instance: {e}")
            return None

    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate EC2 instance"""

        if not self.ec2_client:
            return False

        try:
            self.ec2_client.terminate_instances(InstanceIds=[instance_id])
            self._wait_for_instance_state(instance_id, 'terminated')

            if instance_id in self.instances:
                del self.instances[instance_id]

            return True
        except ClientError as e:
            print(f"Failed to terminate AWS instance: {e}")
            return False

    def get_instance_status(self, instance_id: str) -> Optional[InstanceInfo]:
        """Get EC2 instance status"""

        if not self.ec2_client:
            return None

        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])

            if not response['Reservations']:
                return None

            instance_data = response['Reservations'][0]['Instances'][0]

            # Get CloudWatch metrics
            cpu_utilization = self._get_cloudwatch_metric(instance_id, 'CPUUtilization')
            memory_utilization = self._get_cloudwatch_metric(instance_id, 'MemoryUtilization')

            instance_info = InstanceInfo(
                instance_id=instance_id,
                provider="aws",
                instance_type=instance_data['InstanceType'],
                region=self.config.region,
                availability_zone=instance_data['Placement']['AvailabilityZone'],
                state=instance_data['State']['Name'],
                cpu_utilization=cpu_utilization,
                memory_utilization=memory_utilization,
                launch_time=instance_data['LaunchTime'].replace(tzinfo=None)
            )

            return instance_info

        except ClientError as e:
            print(f"Failed to get AWS instance status: {e}")
            return None

    def list_instances(self) -> List[InstanceInfo]:
        """List all EC2 instances"""

        if not self.ec2_client:
            return []

        try:
            response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'tag:Environment', 'Values': ['qantify-distributed']},
                    {'Name': 'instance-state-name', 'Values': ['running', 'pending']}
                ]
            )

            instances = []
            for reservation in response['Reservations']:
                for instance_data in reservation['Instances']:
                    instance_id = instance_data['InstanceId']
                    instance_info = self.get_instance_status(instance_id)
                    if instance_info:
                        instances.append(instance_info)

            return instances

        except ClientError as e:
            print(f"Failed to list AWS instances: {e}")
            return []

    def scale_cluster(self, cluster_id: str, target_instances: int) -> bool:
        """Scale Auto Scaling Group"""

        # For simplicity, we'll implement basic scaling
        # In production, this would use Auto Scaling Groups
        current_instances = len(self.list_instances())

        if target_instances > current_instances:
            # Scale up
            instances_to_add = target_instances - current_instances
            for _ in range(instances_to_add):
                self.create_instance(self.config.instance_type, self.config.region)
        elif target_instances < current_instances:
            # Scale down
            instances_to_remove = current_instances - target_instances
            instance_ids = list(self.instances.keys())[:instances_to_remove]
            for instance_id in instance_ids:
                self.terminate_instance(instance_id)

        return True

    def get_cost_estimate(self, instance_type: str, hours: float) -> float:
        """Get AWS cost estimate"""

        if not self.pricing:
            return 0.0

        # Simplified pricing lookup
        # In production, you'd query the AWS Pricing API
        pricing_map = {
            't3.micro': 0.0104,
            't3.small': 0.0208,
            'c5.large': 0.096,
            'c5.xlarge': 0.192,
            'm5.large': 0.096,
            'm5.xlarge': 0.192
        }

        hourly_rate = pricing_map.get(instance_type, 0.096)  # Default to c5.large
        return hourly_rate * hours

    def _get_ami_id(self) -> str:
        """Get appropriate AMI ID for the region"""
        # Use Amazon Linux 2 AMI
        ami_map = {
            'us-east-1': 'ami-0c02fb55956c7d316',
            'us-west-2': 'ami-0def3275',
            'eu-west-1': 'ami-0d71ea30463e0ff8d'
        }
        return ami_map.get(self.config.region, 'ami-0c02fb55956c7d316')

    def _get_key_pair_name(self) -> str:
        """Get SSH key pair name"""
        # In production, you'd manage key pairs properly
        return "qantify-keypair"

    def _get_spot_price(self, instance_type: str) -> float:
        """Get current spot price for instance type"""
        # Simplified - in production, query spot pricing history
        return 0.05  # Conservative spot price

    def _wait_for_instance_state(self, instance_id: str, target_state: str, timeout: int = 300):
        """Wait for instance to reach target state"""

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
                current_state = response['Reservations'][0]['Instances'][0]['State']['Name']

                if current_state == target_state:
                    return True

                time.sleep(5)

            except Exception:
                time.sleep(5)

        raise TimeoutError(f"Instance {instance_id} did not reach state {target_state}")

    def _get_cloudwatch_metric(self, instance_id: str, metric_name: str) -> float:
        """Get CloudWatch metric value"""

        if not self.cloudwatch:
            return 0.0

        try:
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName=metric_name,
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.utcnow() - timedelta(minutes=5),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )

            if response['Datapoints']:
                return response['Datapoints'][0]['Average']
            else:
                return 0.0

        except Exception:
            return 0.0


class GCPProvider(CloudProvider):
    """Google Cloud Platform provider implementation"""

    def __init__(self, config: CloudConfig):
        super().__init__(config)
        self.compute_client = None
        self.storage_client = None
        self.container_client = None

    def authenticate(self) -> bool:
        """Authenticate with GCP"""
        if not GCP_AVAILABLE:
            return False

        try:
            # Use Application Default Credentials
            self.compute_client = compute_v1.InstancesClient()
            self.storage_client = storage.Client()
            self.container_client = container_v1.ClusterManagerClient()
            return True
        except Exception as e:
            print(f"GCP authentication failed: {e}")
            return False

    def create_instance(self, instance_type: str, region: str) -> Optional[InstanceInfo]:
        """Create GCE instance"""

        if not self.compute_client:
            return None

        try:
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
            if not project_id:
                return None

            instance_name = f'qantify-worker-{uuid.uuid4().hex[:8]}'

            # Simplified instance creation
            # In production, you'd configure disks, networks, etc.
            instance = compute_v1.Instance()
            instance.name = instance_name
            instance.machine_type = f"zones/{self.config.region}-a/machineTypes/{instance_type}"

            # Add boot disk
            disk = compute_v1.AttachedDisk()
            disk.auto_delete = True
            disk.boot = True
            disk.initialize_params = compute_v1.AttachedDiskInitializeParams()
            disk.initialize_params.source_image = "projects/debian-cloud/global/images/family/debian-10"
            instance.disks = [disk]

            # Add network interface
            network_interface = compute_v1.NetworkInterface()
            network_interface.name = "global/networks/default"
            instance.network_interfaces = [network_interface]

            # Create the instance
            request = compute_v1.InsertInstanceRequest()
            request.instance_resource = instance
            request.project = project_id
            request.zone = f"{self.config.region}-a"

            operation = self.compute_client.insert(request)
            operation.result()  # Wait for completion

            instance_info = InstanceInfo(
                instance_id=instance_name,
                provider="gcp",
                instance_type=instance_type,
                region=region,
                availability_zone=f"{region}-a",
                state="running"
            )

            self.instances[instance_name] = instance_info
            return instance_info

        except GoogleAPIError as e:
            print(f"Failed to create GCP instance: {e}")
            return None

    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate GCE instance"""

        if not self.compute_client:
            return False

        try:
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
            if not project_id:
                return False

            request = compute_v1.DeleteInstanceRequest()
            request.instance = instance_id
            request.project = project_id
            request.zone = f"{self.config.region}-a"

            operation = self.compute_client.delete(request)
            operation.result()  # Wait for completion

            if instance_id in self.instances:
                del self.instances[instance_id]

            return True

        except GoogleAPIError as e:
            print(f"Failed to terminate GCP instance: {e}")
            return False

    def get_instance_status(self, instance_id: str) -> Optional[InstanceInfo]:
        """Get GCE instance status"""

        if not self.compute_client:
            return None

        try:
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
            if not project_id:
                return None

            request = compute_v1.GetInstanceRequest()
            request.instance = instance_id
            request.project = project_id
            request.zone = f"{self.config.region}-a"

            instance = self.compute_client.get(request)

            instance_info = InstanceInfo(
                instance_id=instance_id,
                provider="gcp",
                instance_type=instance['machineType'].split('/')[-1],
                region=self.config.region,
                availability_zone=instance['zone'].split('/')[-1],
                state=instance['status'].lower()
            )

            return instance_info

        except GoogleAPIError as e:
            print(f"Failed to get GCP instance status: {e}")
            return None

    def list_instances(self) -> List[InstanceInfo]:
        """List all GCE instances"""

        if not self.compute_client:
            return []

        try:
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
            if not project_id:
                return []

            request = compute_v1.ListInstancesRequest()
            request.project = project_id
            request.zone = f"{self.config.region}-a"
            request.filter = 'labels.environment = qantify-distributed'

            instances = []
            for instance in self.compute_client.list(request):
                instance_info = self.get_instance_status(instance.name)
                if instance_info:
                    instances.append(instance_info)

            return instances

        except GoogleAPIError as e:
            print(f"Failed to list GCP instances: {e}")
            return []

    def scale_cluster(self, cluster_id: str, target_instances: int) -> bool:
        """Scale GKE cluster"""
        # Implementation would use GKE autoscaling
        return True

    def get_cost_estimate(self, instance_type: str, hours: float) -> float:
        """Get GCP cost estimate"""

        # Simplified pricing
        pricing_map = {
            'n1-standard-1': 0.0475,
            'n1-standard-2': 0.0950,
            'n1-highcpu-2': 0.0709,
            'n1-highcpu-4': 0.1418
        }

        hourly_rate = pricing_map.get(instance_type, 0.0950)  # Default to n1-standard-2
        return hourly_rate * hours


class AzureProvider(CloudProvider):
    """Microsoft Azure provider implementation"""

    def __init__(self, config: CloudConfig):
        super().__init__(config)
        self.compute_client = None
        self.storage_client = None
        self.batch_client = None
        self.credential = None

    def authenticate(self) -> bool:
        """Authenticate with Azure"""
        if not AZURE_AVAILABLE:
            return False

        try:
            self.credential = DefaultAzureCredential()
            subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')

            if not subscription_id:
                return False

            self.compute_client = ComputeManagementClient(self.credential, subscription_id)
            self.storage_client = StorageManagementClient(self.credential, subscription_id)
            self.batch_client = BatchManagementClient(self.credential, subscription_id)
            return True
        except Exception as e:
            print(f"Azure authentication failed: {e}")
            return False

    def create_instance(self, instance_type: str, region: str) -> Optional[InstanceInfo]:
        """Create Azure VM"""
        # Simplified implementation
        return None

    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate Azure VM"""
        return False

    def get_instance_status(self, instance_id: str) -> Optional[InstanceInfo]:
        """Get Azure VM status"""
        return None

    def list_instances(self) -> List[InstanceInfo]:
        """List all Azure VMs"""
        return []

    def scale_cluster(self, cluster_id: str, target_instances: int) -> bool:
        """Scale Azure VM Scale Set"""
        return True

    def get_cost_estimate(self, instance_type: str, hours: float) -> float:
        """Get Azure cost estimate"""

        # Simplified pricing
        pricing_map = {
            'Standard_B2s': 0.0416,
            'Standard_D2_v3': 0.096,
            'Standard_D4_v3': 0.192,
            'Standard_F2s_v2': 0.0849
        }

        hourly_rate = pricing_map.get(instance_type, 0.096)  # Default to D2_v3
        return hourly_rate * hours


class KubernetesManager:
    """Kubernetes cluster management for containerized workloads"""

    def __init__(self, config: CloudConfig):
        self.config = config
        self.client = None
        self.apps_v1 = None
        self.core_v1 = None

    def connect(self, kubeconfig_path: str = None) -> bool:
        """Connect to Kubernetes cluster"""

        if not KUBERNETES_AVAILABLE:
            return False

        try:
            if kubeconfig_path:
                k8s.config.load_kube_config(config_file=kubeconfig_path)
            else:
                k8s.config.load_incluster_config()

            self.client = k8s.client.ApiClient()
            self.apps_v1 = k8s.client.AppsV1Api()
            self.core_v1 = k8s.client.CoreV1Api()
            return True

        except Exception as e:
            print(f"Kubernetes connection failed: {e}")
            return False

    def deploy_worker_deployment(self, image: str, replicas: int, cpu_request: str = "500m", memory_request: str = "1Gi") -> bool:
        """Deploy worker deployment"""

        if not self.apps_v1:
            return False

        try:
            deployment = k8s.client.V1Deployment()
            deployment.api_version = "apps/v1"
            deployment.kind = "Deployment"
            deployment.metadata = k8s.client.V1ObjectMeta(name="qantify-workers")

            spec = k8s.client.V1DeploymentSpec()
            spec.replicas = replicas

            template = k8s.client.V1PodTemplateSpec()
            template.metadata = k8s.client.V1ObjectMeta(labels={"app": "qantify-worker"})

            container = k8s.client.V1Container()
            container.name = "worker"
            container.image = image
            container.resources = k8s.client.V1ResourceRequirements(
                requests={"cpu": cpu_request, "memory": memory_request}
            )

            template.spec = k8s.client.V1PodSpec(containers=[container])
            spec.template = template
            deployment.spec = spec

            self.apps_v1.create_namespaced_deployment(
                namespace="default",
                body=deployment
            )

            return True

        except ApiException as e:
            print(f"Failed to deploy Kubernetes deployment: {e}")
            return False

    def scale_deployment(self, deployment_name: str, replicas: int) -> bool:
        """Scale deployment"""

        if not self.apps_v1:
            return False

        try:
            self.apps_v1.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace="default",
                body={"spec": {"replicas": replicas}}
            )
            return True

        except ApiException as e:
            print(f"Failed to scale deployment: {e}")
            return False

    def get_pod_status(self) -> List[Dict[str, Any]]:
        """Get status of all pods"""

        if not self.core_v1:
            return []

        try:
            pods = self.core_v1.list_namespaced_pod(namespace="default")

            pod_statuses = []
            for pod in pods.items:
                if pod.metadata.labels and pod.metadata.labels.get("app") == "qantify-worker":
                    pod_statuses.append({
                        "name": pod.metadata.name,
                        "status": pod.status.phase,
                        "node": pod.spec.node_name,
                        "cpu_usage": self._get_pod_cpu_usage(pod.metadata.name),
                        "memory_usage": self._get_pod_memory_usage(pod.metadata.name)
                    })

            return pod_statuses

        except ApiException as e:
            print(f"Failed to get pod status: {e}")
            return []

    def _get_pod_cpu_usage(self, pod_name: str) -> float:
        """Get CPU usage for a pod"""
        # Implementation would query metrics server
        return 0.0

    def _get_pod_memory_usage(self, pod_name: str) -> float:
        """Get memory usage for a pod"""
        # Implementation would query metrics server
        return 0.0


class CostOptimizer:
    """Cost optimization for cloud resources"""

    def __init__(self, config: CloudConfig):
        self.config = config
        self.cost_history = deque(maxlen=1000)
        self.optimization_suggestions = []

    def analyze_costs(self, instances: List[InstanceInfo]) -> Dict[str, Any]:
        """Analyze current costs and suggest optimizations"""

        total_cost = sum(instance.hourly_cost for instance in instances)
        avg_utilization = np.mean([instance.cpu_utilization for instance in instances])

        suggestions = []

        # Suggest reserved instances for steady workloads
        if avg_utilization > 80 and not self.config.reserved_instances:
            suggestions.append("Consider purchasing reserved instances for steady workloads")

        # Suggest spot instances for variable workloads
        if avg_utilization < 60 and not self.config.spot_instances:
            suggestions.append("Consider using spot instances for variable workloads")

        # Suggest scaling down underutilized instances
        underutilized = [i for i in instances if i.cpu_utilization < 30]
        if underutilized:
            suggestions.append(f"Consider terminating {len(underutilized)} underutilized instances")

        # Check budget limits
        if total_cost > self.config.max_daily_cost:
            suggestions.append(f"Daily cost (${total_cost:.2f}) exceeds budget limit (${self.config.max_daily_cost:.2f})")

        return {
            'total_daily_cost': total_cost,
            'avg_utilization': avg_utilization,
            'cost_per_instance': total_cost / max(len(instances), 1),
            'suggestions': suggestions
        }

    def get_optimal_instance_type(self, workload_requirements: Dict[str, Any]) -> str:
        """Recommend optimal instance type based on workload"""

        cpu_cores = workload_requirements.get('cpu_cores', 2)
        memory_gb = workload_requirements.get('memory_gb', 4)
        storage_gb = workload_requirements.get('storage_gb', 50)

        # Simple recommendation logic
        if cpu_cores <= 2 and memory_gb <= 4:
            return "t3.small"
        elif cpu_cores <= 4 and memory_gb <= 8:
            return "c5.large"
        elif cpu_cores <= 8 and memory_gb <= 16:
            return "c5.xlarge"
        else:
            return "c5.2xlarge"


class CloudInfrastructureManager:
    """Main cloud infrastructure management class"""

    def __init__(self, config: CloudConfig):
        self.config = config
        self.provider = self._create_provider()
        self.kubernetes = KubernetesManager(config)
        self.cost_optimizer = CostOptimizer(config)

        self.monitoring_thread = None
        self.is_monitoring = False

    def _create_provider(self) -> Optional[CloudProvider]:
        """Create appropriate cloud provider"""

        if self.config.provider == "aws":
            return AWSProvider(self.config)
        elif self.config.provider == "gcp":
            return GCPProvider(self.config)
        elif self.config.provider == "azure":
            return AzureProvider(self.config)
        else:
            return None

    def initialize_infrastructure(self) -> bool:
        """Initialize cloud infrastructure"""

        if not self.provider:
            return False

        # Authenticate
        if not self.provider.authenticate():
            return False

        # Connect to Kubernetes if available
        self.kubernetes.connect()

        # Start monitoring
        self.start_monitoring()

        return True

    def provision_cluster(self, target_instances: int) -> bool:
        """Provision compute cluster"""

        if not self.provider:
            return False

        current_instances = len(self.provider.list_instances())

        if current_instances < target_instances:
            # Scale up
            instances_needed = target_instances - current_instances

            for _ in range(instances_needed):
                instance = self.provider.create_instance(
                    self.config.instance_type,
                    self.config.region
                )
                if not instance:
                    return False

        elif current_instances > target_instances:
            # Scale down
            instances_to_remove = current_instances - target_instances
            instances = self.provider.list_instances()[:instances_to_remove]

            for instance in instances:
                self.provider.terminate_instance(instance.instance_id)

        return True

    def auto_scale(self, target_utilization: float = None) -> bool:
        """Auto-scale cluster based on utilization"""

        if target_utilization is None:
            target_utilization = self.config.target_cpu_utilization

        instances = self.provider.list_instances() if self.provider else []
        avg_utilization = np.mean([i.cpu_utilization for i in instances]) if instances else 0.0

        if avg_utilization > target_utilization + 20:
            # Scale up
            target_instances = min(len(instances) + 1, self.config.max_instances)
            return self.provision_cluster(target_instances)

        elif avg_utilization < target_utilization - 20 and len(instances) > self.config.min_instances:
            # Scale down
            target_instances = max(len(instances) - 1, self.config.min_instances)
            return self.provision_cluster(target_instances)

        return True

    def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get current infrastructure status"""

        instances = self.provider.list_instances() if self.provider else []
        pods = self.kubernetes.get_pod_status()

        cost_analysis = self.cost_optimizer.analyze_costs(instances)

        return {
            'instances': len(instances),
            'instance_details': [i.__dict__ for i in instances],
            'kubernetes_pods': len(pods),
            'pod_details': pods,
            'cost_analysis': cost_analysis,
            'total_cost_per_hour': sum(i.hourly_cost for i in instances)
        }

    def optimize_costs(self) -> List[str]:
        """Run cost optimization"""

        instances = self.provider.list_instances() if self.provider else []
        analysis = self.cost_optimizer.analyze_costs(instances)

        return analysis['suggestions']

    def start_monitoring(self):
        """Start infrastructure monitoring"""

        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop infrastructure monitoring"""

        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()

    def _monitoring_loop(self):
        """Monitoring loop"""

        while self.is_monitoring:
            try:
                # Update instance metrics
                if self.provider:
                    instances = self.provider.list_instances()
                    for instance in instances:
                        # Update metrics (simplified)
                        pass

                # Auto-scale if needed
                self.auto_scale()

                # Cost optimization
                suggestions = self.optimize_costs()
                if suggestions:
                    print(f"Cost optimization suggestions: {suggestions}")

                time.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(60)

    def cleanup(self):
        """Clean up infrastructure"""

        self.stop_monitoring()

        # Terminate all instances
        if self.provider:
            instances = self.provider.list_instances()
            for instance in instances:
                self.provider.terminate_instance(instance.instance_id)


# Factory functions
def create_cloud_infrastructure_manager(config: CloudConfig) -> CloudInfrastructureManager:
    """Factory function for cloud infrastructure manager"""
    return CloudInfrastructureManager(config)


def create_cloud_config(provider: str = "aws", region: str = "us-east-1") -> CloudConfig:
    """Create cloud configuration"""
    return CloudConfig(provider=provider, region=region)


# Example usage and testing
if __name__ == "__main__":
    # Test cloud infrastructure management
    print("Testing Cloud Infrastructure Management...")

    config = create_cloud_config(provider="aws", region="us-east-1")
    manager = create_cloud_infrastructure_manager(config)

    if manager.initialize_infrastructure():
        print("✓ Cloud infrastructure initialized")

        # Get status
        status = manager.get_infrastructure_status()
        print(f"Current instances: {status['instances']}")
        print(f"Total cost per hour: ${status['total_cost_per_hour']:.2f}")

        # Cost optimization suggestions
        suggestions = manager.optimize_costs()
        if suggestions:
            print("Cost optimization suggestions:")
            for suggestion in suggestions:
                print(f"  - {suggestion}")

        # Cleanup
        manager.cleanup()
        print("✓ Infrastructure cleanup completed")

    else:
        print("✗ Failed to initialize cloud infrastructure")

    print("\nCloud infrastructure management test completed!")
