import json
import os
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

if TYPE_CHECKING:
    import ovh


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


@dataclass
class OVHClient:
    """
    OVHcloud API client wrapper around the official ovh library.
    """

    endpoint: str
    application_key: str
    application_secret: str
    consumer_key: str
    project_id: str
    _client: ovh.Client | None = None

    def __post_init__(self):
        """
        Initialize the OVH client after dataclass initialization.
        """
        import ovh

        self._client = ovh.Client(
            endpoint=self.endpoint,
            application_key=self.application_key,
            application_secret=self.application_secret,
            consumer_key=self.consumer_key,
        )

    def request(self, method: str, path: str, body: dict | None = None) -> Any:
        """
        Make an authenticated request to OVH API using the ovh library.
        """
        if not self._client:
            raise RuntimeError("OVH client not initialized")

        if method == "GET":
            return self._client.get(path)
        elif method == "POST":
            return self._client.post(path, **body) if body else self._client.post(path)
        elif method == "PUT":
            return self._client.put(path, **body) if body else self._client.put(path)
        elif method == "DELETE":
            return self._client.delete(path)
        else:
            raise ValueError(f"Unsupported method: {method}")


# Global default client (lazy-loaded)
_default_client: OVHClient | None = None


def _error_env_var_required(varname):
    sys.stderr.write(f"Error: {varname} environment variable is required\n")


def _get_default_client() -> OVHClient:
    """Get or create the default client from environment variables."""
    global _default_client

    if _default_client is None:
        # Get values and validate they exist
        endpoint = os.environ.get("OVH_ENDPOINT", "ovh-eu")
        application_key = os.environ.get("OVH_APPLICATION_KEY")
        application_secret = os.environ.get("OVH_APPLICATION_SECRET")
        consumer_key = os.environ.get("OVH_CONSUMER_KEY")
        project_id = os.environ.get("OVH_PROJECT_ID")

        # Check required fields
        if not application_key:
            _error_env_var_required("OVH_APPLICATION_KEY")
            sys.exit(1)
        if not application_secret:
            _error_env_var_required("OVH_APPLICATION_SECRET")
            sys.exit(1)
        if not consumer_key:
            _error_env_var_required("OVH_CONSUMER_KEY")
            sys.exit(1)
        if not project_id:
            _error_env_var_required("OVH_PROJECT_ID")
            sys.exit(1)

        _default_client = OVHClient(
            endpoint=endpoint,
            application_key=application_key,
            application_secret=application_secret,
            consumer_key=consumer_key,
            project_id=project_id,
        )

    return _default_client


# def _camel_to_snake(name):
#     s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
#     s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
#     return s2.lower()


# def _dict_keys_to_snake(obj: dict[str, Any]) -> dict[str, Any]:
#     return {_camel_to_snake(k) if isinstance(k, str) else k: v for k, v in obj.items()}


def _wait_for_item_ready(
    client: OVHClient,
    item_name: str,
    get_func,
    get_func_args: list[str],
    status: str,
    timeout: int = 600,
) -> None:
    """
    Wait for item to be in available status.
    """
    print(f"Waiting for {item_name} to reach status {status}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            item = get_func(*get_func_args, client)
            if item.status == status:
                print(f"{item_name.capitalize()} status reached!")
                return
            print(f"Current {item_name} status: {item.status}")
        except Exception as e:
            print(f"Error checking {item_name} status: {e}")
        time.sleep(10)
    raise TimeoutError(
        f"{item_name.capitalize()} did not reach desired status within {timeout} seconds"
    )


def _wait_for_item_deleted(
    client: OVHClient,
    item_name: str,
    get_func,
    get_func_args: list[Any],
    timeout: int = 600,
) -> None:
    """
    Wait for volume to be deleted.
    """
    print(f"Waiting for {item_name} to be deleted...")
    start_time = time.time()
    item = None
    deleted = False
    while True:
        time.sleep(10)
        try:
            item = get_func(*get_func_args, client)
            if not item:
                deleted = True
            else:
                print(f"Current {item_name} status: {item.status} ")
        except ovh.exceptions.ResourceNotFoundError:
            deleted = True
        except Exception as e:
            # Check if it's a 404-like error
            if "404" in str(e) or "not found" in str(e).lower():
                deleted = True
            elif "Expecting value: line 1 column 1 (char 0)" in str(e):
                # We sometimes get this when trying to "get" deleted resources.
                # I think this happens because the API returns a successful http request but
                # (for some reason) doesn't add a json payload to the response.
                # I think it is a bug in the API. It should not return a successful response.
                deleted = True
            else:
                print(f"Error checking {item_name} status: {e}")
        if deleted:
            print(f"{item_name.capitalize()} deleted successfully!")
            return
        if time.time() - start_time > timeout:
            # We keep on waiting when the item is marked 'deleted' but still available.
            if item and item.status != "DELETED":
                break

    raise TimeoutError(
        f"{item_name.capitalize()} was not deleted within {timeout} seconds"
    )


class Volume(BaseSchema):
    attached_to: list[str]
    availability_zone: str | None
    bootable: bool
    creation_date: str
    description: str
    id: str
    name: str
    plan_code: str
    region: str
    size: int
    status: str
    type: str


class VolumeSnapshot(BaseSchema):
    creation_date: str
    description: str
    id: str
    name: str
    plan_code: str | None
    region: str
    size: int
    status: str
    volume_id: str


class VolumeType(str, Enum):
    classic = "classic"
    classic_luks = "classic-luks"
    classic_multiattach = "classic-multiattach"
    high_speed = "high-speed"
    high_speed_gen2 = "high-speed-gen2"
    high_speed_gen2_luks = "high-speed-gen2-luks"
    high_speed_luks = "high-speed-luks"


def volume_create(
    name: str,
    region: str,
    size: int,
    description: str | None = None,
    image_id: str | None = None,
    snapshot_id: str | None = None,
    volume_type: VolumeType = VolumeType.classic,
    wait: bool = True,
    client: OVHClient | None = None,
) -> Volume:
    """
    Create a new OVHcloud volume.

    volume_types: classic, classic-luks, classic-multiattach, high-speed,
    high-speed-gen2, high-speed-gen2-luks, high-speed-luks

    Args:
        name: Volume name
        region: OVH region (e.g., GRA7, BHS5)
        size: Volume size in GB
        description: Volume description
        image_id: Image ID to use for volume creation
        snapshot_id: Snapshot ID to use for volume creation
        volume_type: Volume type (default: "classic")
        client: Optional OVHClient instance (uses default if not provided)

    Returns:
        Volume object with details about the created volume
    """
    client = client or _get_default_client()

    payload: dict[str, Any] = {
        "name": name,
        "region": region,
        "size": size,
        "type": volume_type.value,
    }

    if description:
        payload["description"] = description
    if image_id:
        payload["imageId"] = image_id
    if snapshot_id:
        payload["snapshotId"] = snapshot_id

    print(f"\nCreating OVHcloud volume '{name}'...")
    print(f"Request Payload: {json.dumps(payload, indent=2)}\n")

    path = f"/cloud/project/{client.project_id}/volume"
    volume_data = client.request("POST", path, payload)
    volume = Volume(**volume_data)

    print(f"Volume created with ID: {volume.id}")

    if wait:
        _wait_for_item_ready(
            client, "volume", volume_get, [volume.id, region], "available"
        )

    return volume


def volume_get(
    volume_id: str,
    region: str,
    client: OVHClient | None = None,
) -> Volume | None:
    """
    Get detailed information about a volume.

    Args:
        volume_id: Volume ID
        region: OVH region (e.g., GRA7, BHS5)
        client: Optional OVHClient instance (uses default if not provided)

    Returns:
        Volume object with details about the volume
    """
    client = client or _get_default_client()
    path = f"/cloud/project/{client.project_id}/volume/{volume_id}"

    response = client.request("GET", path)
    volume_data = response.copy()
    volume_data["region"] = region

    if volume_data.get("status") == "DELETED":
        return None

    return Volume(**volume_data)


def volume_list(
    region: str | None = None,
    client: OVHClient | None = None,
) -> list[Volume]:
    """
    List all volumes in the project.

    Args:
        client: Optional OVHClient instance (uses default if not provided)

    Returns:
        List of Volume objects
    """
    client = client or _get_default_client()

    # Prepare query parameters
    params = {}
    if region:
        params["region"] = region

    path = f"/cloud/project/{client.project_id}/volume"
    response = client.request("GET", path, params)

    return [Volume(**v) for v in response if v.get("status") != "DELETED"]


def volume_delete(
    volume_id: str,
    wait: bool = True,
    client: OVHClient | None = None,
) -> None:
    """
    Delete a volume.

    Args:
        volume_id: Volume ID
        client: Optional OVHClient instance (uses default if not provided)
    """
    client = client or _get_default_client()
    print(f"\nDeleting volume {volume_id}...")
    path = f"/cloud/project/{client.project_id}/volume/{volume_id}"
    client.request("DELETE", path)
    print("Volume deletion initiated.")

    if wait:
        _wait_for_item_deleted(client, "volume", volume_get, [volume_id])


def volume_snapshot_create(
    volume_id: str,
    name: str,
    description: str | None = None,
    wait: bool = True,
    client: OVHClient | None = None,
) -> VolumeSnapshot:
    """
    Create a snapshot of an OVHcloud volume.

    Args:
        volume_id: Volume ID to snapshot
        name: Snapshot name
        description: Snapshot description
        client: Optional OVHClient instance (uses default if not provided)

    Returns:
        VolumeSnapshot object with details about the created snapshot
    """
    client = client or _get_default_client()

    payload: dict[str, Any] = {
        "name": name,
    }

    if description:
        payload["description"] = description

    print(f"\nCreating snapshot for volume '{volume_id}'...")
    print(f"Request Payload: {json.dumps(payload, indent=2)}\n")

    path = f"/cloud/project/{client.project_id}/volume/{volume_id}/snapshot"
    snapshot_data = client.request("POST", path, payload)
    snapshot = VolumeSnapshot(**snapshot_data)

    print(f"Snapshot created with ID: {snapshot.id}")

    if wait:
        _wait_for_item_ready(
            client,
            "volume snapshot",
            volume_snapshot_get,
            [snapshot.id],
            "available",
        )

    return snapshot


def volume_snapshot_get(
    snapshot_id: str,
    client: OVHClient | None = None,
) -> VolumeSnapshot | None:
    """
    Get detailed information about a volume snapshot.

    Args:
        snapshot_id: Snapshot ID
        client: Optional OVHClient instance (uses default if not provided)

    Returns:
        VolumeSnapshot object with details about the snapshot
    """
    client = client or _get_default_client()
    path = f"/cloud/project/{client.project_id}/volume/snapshot/{snapshot_id}"

    response = client.request("GET", path)

    if response.get("status") == "DELETED":
        return None

    return VolumeSnapshot(**response)


def volume_snapshot_list(
    region: str | None = None,
    client: OVHClient | None = None,
) -> list[VolumeSnapshot]:
    """
    List all volume snapshots in the project.

    Args:
        region: Optional region filter
        client: Optional OVHClient instance (uses default if not provided)

    Returns:
        List of VolumeSnapshot objects
    """
    client = client or _get_default_client()
    path = f"/cloud/project/{client.project_id}/volume/snapshot"

    # Prepare query parameters
    params = {}
    if region:
        params["region"] = region

    response = client.request("GET", path, params)
    return [
        VolumeSnapshot(**snapshot)
        for snapshot in response
        if snapshot.get("status") != "DELETED"
    ]


def volume_snapshot_delete(
    snapshot_id: str,
    wait: bool = True,
    client: OVHClient | None = None,
) -> None:
    """
    Delete a volume snapshot.

    Args:
        snapshot_id: Snapshot ID
        client: Optional OVHClient instance (uses default if not provided)
    """
    client = client or _get_default_client()
    print(f"\nDeleting volume snapshot {snapshot_id}...")
    path = f"/cloud/project/{client.project_id}/volume/snapshot/{snapshot_id}"
    try:
        client.request("DELETE", path)
        print("Volume snapshot deletion initiated.")
    except ovh.ResourceNotFoundError:
        print(
            "Could not find volume snapshot for deletion. Maybe it is already deleted?"
        )

    if wait:
        _wait_for_item_deleted(
            client, "volume snapshot", volume_snapshot_get, [snapshot_id]
        )


class InstanceFlavorCapability(BaseSchema):
    enabled: bool
    name: str


class InstanceFlavor(BaseSchema):
    available: bool
    capabilities: list[InstanceFlavorCapability]
    disk: int
    id: str
    inbound_bandwidth: int
    name: str
    os_type: str
    outbound_bandwidth: int
    quota: int
    ram: int
    region: str
    type: str
    vcpus: int
    plan_codes: dict[str, str | None]


class InstanceImage(BaseSchema):
    creation_date: str
    id: str
    min_disk: int
    min_ram: int
    name: str
    region: str
    size: int
    status: str
    tags: list[str]
    type: str
    user: str
    visibility: str
    flavor_type: str | None = None
    plan_code: str | None = None


class InstanceIpAddress(BaseSchema):
    gateway_ip: str
    ip: str
    network_id: str
    type: str
    version: int


class InstanceMonthlyBilling(BaseSchema):
    since: str
    status: str


class InstanceSSHKey(BaseSchema):
    finger_print: str
    id: str
    name: str
    public_key: str
    regions: list[str]


class Instance(BaseSchema):
    id: str
    name: str
    status: str
    region: str
    created: str
    ip_addresses: list[InstanceIpAddress]
    monthly_billing: InstanceMonthlyBilling | None
    plan_code: str
    operation_ids: list[str]
    current_month_outgoing_traffic: int | None = None
    availability_zone: str | None = None
    license_plan_code: str | None
    rescue_password: str | None = None
    image: InstanceImage | None = None
    flavor: InstanceFlavor | None = None
    ssh_key: InstanceSSHKey | None = None
    flavor_id: str | None = None
    image_id: str | None = None
    sshKey_id: str | None = None


class InstanceNetwork(BaseSchema):
    network_id: str
    ip: str | None = None


class InstanceAutobackup(BaseSchema):
    cron: str | None = None
    rotation: int | None = None


def instance_create(
    name: str,
    region: str,
    flavor_id: str,
    image_id: str | None = None,
    ssh_key_id: str | None = None,
    user_data: str | None = None,
    monthly_billing: bool = False,
    availability_zone: str | None = None,
    group_id: str | None = None,
    volume_id: str | None = None,
    autobackup: InstanceAutobackup | None = None,
    networks: list[InstanceNetwork] | None = None,
    wait: bool = True,
    client: OVHClient | None = None,
) -> Instance:
    """
    Create a new OVHcloud instance.

    Args:
        name: Instance name
        region: OVH region (e.g., GRA7, BHS5)
        flavor_id: Flavor ID for the instance
        image_id: Image ID to use
        ssh_key_id: SSH key ID to inject
        user_data: User data for cloud-init
        monthly_billing: Enable monthly billing
        availability_zone: Availability zone
        group_id: Security group ID
        volume_id: Volume ID to attach
        autobackup: Autobackup configuration
        networks: Network configuration
        wait: Wait for instance to be ready
        client: Optional OVHClient instance (uses default if not provided)

    Returns:
        Instance object with details about the created instance
    """
    client = client or _get_default_client()

    payload: dict[str, Any] = {
        "name": name,
        "region": region,
        "flavorId": flavor_id,
    }

    if monthly_billing:
        payload["monthlyBilling"] = monthly_billing
    if image_id:
        payload["imageId"] = image_id
    if ssh_key_id:
        payload["sshKeyId"] = ssh_key_id
    if user_data:
        payload["userData"] = user_data
    if availability_zone:
        payload["availabilityZone"] = availability_zone
    if group_id:
        payload["groupId"] = group_id
    if volume_id:
        payload["volumeId"] = volume_id
    if autobackup:
        payload["autobackup"] = {
            "cron": autobackup.cron,
            "rotation": autobackup.rotation,
        }
    if networks:
        payload["networks"] = [
            {"ip": network.ip, "networkId": network.network_id} for network in networks
        ]

    print(f"\nCreating OVHcloud instance '{name}'...")
    print(f"Request Payload: {json.dumps(payload, indent=2)}\n")

    path = f"/cloud/project/{client.project_id}/instance"
    instance_data = client.request("POST", path, payload)

    instance = Instance(**instance_data)

    print(f"Instance created with ID: {instance.id}")

    if wait:
        _wait_for_item_ready(
            client,
            "instance",
            instance_get,
            [instance.id],
            "ACTIVE",
        )

    return instance


def instance_get(
    instance_id: str,
    client: OVHClient | None = None,
) -> Instance | None:
    """Get detailed information about an instance."""
    client = client or _get_default_client()
    path = f"/cloud/project/{client.project_id}/instance/{instance_id}"
    response = client.request("GET", path)

    if response.get("status") == "DELETED":
        return None

    return Instance(**response)


def instance_list(
    region: str | None = None,
    client: OVHClient | None = None,
) -> list[Instance]:
    """List all instances in the project."""
    client = client or _get_default_client()

    # Prepare query parameters
    params = {}
    if region:
        params["region"] = region

    path = f"/cloud/project/{client.project_id}/instance"
    response = client.request("GET", path, params)
    return [Instance(**i) for i in response if i.get("status") != "DELETED"]


def instance_start(
    instance_id: str,
    wait: bool = True,
    client: OVHClient | None = None,
) -> Instance:
    """
    Start an instance.

    Args:
        instance_id: Instance ID
        wait: Wait for instance to be started
        client: Optional OVHClient instance (uses default if not provided)
    """
    client = client or _get_default_client()
    print(f"\nStarting instance {instance_id}...")
    path = f"/cloud/project/{client.project_id}/instance/{instance_id}/start"

    instance_data = client.request("POST", path)
    instance = Instance(**instance_data)

    print("Instance start initiated.")

    if wait:
        _wait_for_item_ready(
            client,
            "instance",
            instance_get,
            [instance.id],
            "ACTIVE",
        )

    print("Instance started.")
    return instance


def instance_stop(
    instance_id: str,
    wait: bool = True,
    client: OVHClient | None = None,
) -> Instance:
    """
    Stop an instance.

    Args:
        instance_id: Instance ID
        wait: Wait for instance to be stopped
        client: Optional OVHClient instance (uses default if not provided)
    """
    client = client or _get_default_client()
    print(f"\nStopping instance {instance_id}...")
    path = f"/cloud/project/{client.project_id}/instance/{instance_id}/stop"

    instance_data = client.request("POST", path)
    instance = Instance(**instance_data)

    print("Instance stop initiated.")

    if wait:
        _wait_for_item_ready(
            client,
            "instance",
            instance_get,
            [instance.id],
            "STOPPED",
        )

    print("Instance stopped.")
    return instance


def instance_delete(
    instance_id: str,
    wait: bool = True,
    client: OVHClient | None = None,
) -> None:
    """
    Delete an instance.

    Args:
        instance_id: Instance ID
        wait: Wait for instance to be deleted
        client: Optional OVHClient instance (uses default if not provided)
    """
    client = client or _get_default_client()
    print(f"\nDeleting instance {instance_id}...")
    path = f"/cloud/project/{client.project_id}/instance/{instance_id}"
    client.request("DELETE", path)
    print("Instance deletion initiated.")

    if wait:
        _wait_for_item_deleted(client, "instance", instance_get, [instance_id])


class KubeClusterCustomization(BaseSchema):
    api_server: dict[str, Any] | None = None
    kube_proxy: dict[str, Any] | None = None


class KubeClusterOpenIdConnect(BaseSchema):
    client_id: str | None = None
    issuer_url: str | None = None
    username_claim: str | None = None
    username_prefix: str | None = None
    groups_claim: list[str] | None = None
    groups_prefix: str | None = None
    required_claim: list[str] | None = None


class KubeCluster(BaseSchema):
    id: str
    name: str
    region: str
    version: str
    status: str  # READY, UPDATING, RESETTING, SUSPENDING, REOPENING, DELETING, SUSPENDED, ERROR, USER_ERROR
    url: str
    created_at: str  # ISO 8601 datetime string
    updated_at: str  # ISO 8601 datetime string
    control_plane_is_up_to_date: bool
    is_up_to_date: bool
    nodes_url: str
    update_policy: str  # ALWAYS_UPDATE, MINIMAL_DOWNTIME, NEVER_UPDATE
    plan: str
    audit_logs_subscribed: bool
    next_upgrade_versions: list[str] | None
    nodes_subnet_id: str | None = None
    private_network_id: str | None = None
    private_network_configuration: dict[str, Any] | None = None
    customization: KubeClusterCustomization | None = None
    open_id_connect: KubeClusterOpenIdConnect | None = None
    kube_proxy_mode: str | None = None  # iptables, ipvs
    load_balancers_subnet_id: str | None = None


class KubeConfig(BaseSchema):
    content: str  # The actual kubeconfig content (YAML format)


def kube_cluster_create(
    name: str,
    region: str,
    version: str,
    update_policy: str = "ALWAYS_UPDATE",
    private_network_id: str | None = None,
    wait: bool = True,
    client: OVHClient | None = None,
) -> KubeCluster:
    """
    Create OVHcloud Kubernetes cluster.
    Args:
        name: Cluster name
        region: OVH region (e.g., GRA7, BHS5)
        version: Kubernetes version
        update_policy: Update policy (ALWAYS_UPDATE, MINIMAL_DOWNTIME, NEVER_UPDATE)
        private_network_id: Optional private network ID
        wait: Wait for cluster to be ready
        client: Optional OVHClient instance (uses default if not provided)
    Returns:
        Dictionary containing cluster information
    """
    # Use provided client or get default
    client = client or _get_default_client()

    if not client.project_id:
        raise ValueError("OVH project ID is required")

    # Create cluster
    cluster_payload = {
        "name": name,
        "region": region,
        "version": version,
        "updatePolicy": update_policy,
    }
    if private_network_id:
        cluster_payload["privateNetworkId"] = private_network_id

    print("\nCreating OVHcloud Kubernetes cluster...")
    print(f"Request Payload: {json.dumps(cluster_payload, indent=2)}\n")

    cluster_path = f"/cloud/project/{client.project_id}/kube"
    cluster_data = client.request("POST", cluster_path, cluster_payload)

    cluster_id = cluster_data.get("id")
    print(f"Cluster created with ID: {cluster_id}")

    # Wait for cluster to be ready if requested
    if wait:
        _wait_for_item_ready(client, "cluster", kube_cluster_get, [cluster_id], "READY")

    print(f"\nCluster '{name}' created successfully!")

    return KubeCluster(**cluster_data)


def kube_cluster_get(
    cluster_id: str,
    client: OVHClient | None = None,
) -> KubeCluster | None:
    """Get detailed information about a Kubernetes cluster."""
    client = client or _get_default_client()
    path = f"/cloud/project/{client.project_id}/kube/{cluster_id}"
    response = client.request("GET", path)

    if response.get("status") == "DELETED":
        return None

    return KubeCluster(**response)


def kube_cluster_get_by_name(
    cluster_name: str,
    client: OVHClient | None = None,
) -> KubeCluster | None:
    """Get detailed information about a Kubernetes cluster, select by name."""
    client = client or _get_default_client()
    clusters = kube_cluster_list(client)
    cluster = None
    for c in clusters:
        if c.name == cluster_name:
            cluster = c
    return cluster


def kube_cluster_list(
    client: OVHClient | None = None,
) -> list[KubeCluster]:
    """List all Kubernetes clusters in the project."""
    client = client or _get_default_client()
    path = f"/cloud/project/{client.project_id}/kube"

    cluster_ids = client.request("GET", path)

    valid_clusters = []
    for c_id in cluster_ids:
        cluster = kube_cluster_get(c_id, client)
        if cluster and cluster.status != "DELETED":
            valid_clusters.append(cluster)
    return valid_clusters


def kube_cluster_delete(
    cluster_id: str,
    wait: bool = True,
    client: OVHClient | None = None,
) -> None:
    """
    Delete a Kubernetes cluster.
    Args:
        cluster_id: Cluster ID
        wait: Wait for cluster to be deleted
        client: Optional OVHClient instance (uses default if not provided)
    """
    client = client or _get_default_client()
    print(f"\nDeleting cluster {cluster_id}...")
    path = f"/cloud/project/{client.project_id}/kube/{cluster_id}"
    client.request("DELETE", path)
    print("Cluster deletion initiated.")

    if wait:
        _wait_for_item_deleted(client, "cluster", kube_cluster_get, [cluster_id])


def kube_cluster_get_kubeconfig(
    cluster_id: str,
    save_to_file: str | None = None,
    client: OVHClient | None = None,
) -> KubeConfig:
    """Get the kubeconfig for a Kubernetes cluster."""
    client = client or _get_default_client()
    path = f"/cloud/project/{client.project_id}/kube/{cluster_id}/kubeconfig"
    kubeconfig_data = client.request("POST", path)
    kubeconfig = KubeConfig(**kubeconfig_data)

    if save_to_file and kubeconfig.content:
        config_path = os.path.expanduser(save_to_file)
        with open(config_path, "w") as f:
            f.write(kubeconfig.content)
        print(f"Kubeconfig downloaded and saved to {config_path}.")

    return kubeconfig


def kube_cluster_reset_kubeconfig(
    cluster_id: str,
    client: OVHClient | None = None,
) -> KubeConfig:
    """Reset/regenerate the kubeconfig for a Kubernetes cluster."""
    client = client or _get_default_client()

    print(f"\nResetting kubeconfig for cluster {cluster_id}...")

    path = f"/cloud/project/{client.project_id}/kube/{cluster_id}/kubeconfig/reset"
    result = client.request("POST", path)

    print("Kubeconfig reset successfully!")

    return KubeConfig(**result)


class KubeNodePoolTemplate(BaseSchema):
    metadata: dict[str, Any] = field(default_factory=dict)
    spec: dict[str, Any] = field(default_factory=dict)


class KubeNodePoolAutoscaling(BaseSchema):
    scale_down_utilization_threshold: float | None = None
    scale_down_unneeded_time_seconds: int | None = None
    scale_down_unready_time_seconds: int | None = None


KubeNodePoolStatus = Literal["CAPACITY_OK", "OVER_CAPACITY", "UNDER_CAPACITY"]


class KubeNodePool(BaseSchema):
    id: str
    project_id: str
    name: str
    flavor: str
    status: (
        str  # READY, UPDATING, REBOOT_REQUIRED, INSTALLING, ERROR, DELETING, DELETED
    )
    available_nodes: int
    desired_nodes: int
    current_nodes: int
    up_to_date_nodes: int
    min_nodes: int
    max_nodes: int
    created_at: str  # ISO 8601 datetime string
    updated_at: str  # ISO 8601 datetime string
    size_status: KubeNodePoolStatus
    autoscale: bool = False
    monthly_billed: bool = False
    anti_affinity: bool = False
    autoscaling: KubeNodePoolAutoscaling | None = None
    template: KubeNodePoolTemplate | None = None
    availability_zones: list[str] = field(default_factory=list)


class KubeNodePoolNode(BaseSchema):
    id: str
    project_id: str
    instance_id: str
    node_pool_id: str
    name: str
    flavor: str
    status: (
        str  # READY, INSTALLING, UPDATING, REBOOT_REQUIRED, REBUILDING, DELETING, ERROR
    )
    version: str
    is_up_to_date: bool
    created_at: str
    updated_at: str
    deployed_at: str
    deleted_at: str | None = None


def kube_node_pool_list(
    cluster_id: str,
    client: OVHClient | None = None,
) -> list[KubeNodePool]:
    """List all node pools in a Kubernetes cluster."""
    client = client or _get_default_client()
    path = f"/cloud/project/{client.project_id}/kube/{cluster_id}/nodepool"
    response = client.request("GET", path)

    return [
        KubeNodePool(**item) for item in response if item.get("status") != "DELTETED"
    ]


def kube_node_pool_create(
    cluster_id: str,
    name: str,
    flavor: str,
    desired_nodes: int,
    min_nodes: int | None = None,
    max_nodes: int | None = None,
    autoscale: bool = False,
    monthly_billed: bool = False,
    anti_affinity: bool = False,
    wait: bool = True,
    client: OVHClient | None = None,
) -> KubeNodePool:
    """Create a new node pool in a Kubernetes cluster."""
    client = client or _get_default_client()
    node_pool_payload = {
        "name": name,
        "flavorName": flavor,
        "desiredNodes": desired_nodes,
        "minNodes": min_nodes or desired_nodes,
        "maxNodes": max_nodes or desired_nodes,
        "autoscale": autoscale,
        "monthlyBilled": monthly_billed,
        "antiAffinity": anti_affinity,
    }

    print(f"\nCreating node pool '{name}'...")
    print(f"Request Payload: {json.dumps(node_pool_payload, indent=2)}\n")

    path = f"/cloud/project/{client.project_id}/kube/{cluster_id}/nodepool"
    node_pool_data = client.request("POST", path, node_pool_payload)
    node_pool = KubeNodePool(**node_pool_data)

    print(f"Node pool created with ID: {node_pool.id}")

    if wait:
        _wait_for_item_ready(
            client, "node_pool", kube_node_pool_get, [cluster_id, node_pool.id], "READY"
        )

    return node_pool


def kube_node_pool_get(
    cluster_id: str,
    node_pool_id: str,
    client: OVHClient | None = None,
) -> KubeNodePool | None:
    """Get detailed information about a node pool."""
    client = client or _get_default_client()
    path = (
        f"/cloud/project/{client.project_id}/kube/{cluster_id}/nodepool/{node_pool_id}"
    )
    response = client.request("GET", path)
    if response.get("status") == "DELETED":
        return None
    return KubeNodePool(**response)


def kube_node_pool_update(
    cluster_id: str,
    node_pool_id: str,
    desired_nodes: int | None = None,
    min_nodes: int | None = None,
    max_nodes: int | None = None,
    autoscale: bool | None = None,
    wait: bool = True,
    client: OVHClient | None = None,
) -> None:
    """Update a node pool (resize, change autoscaling settings)."""
    client = client or _get_default_client()

    # Build update payload with only provided values
    update_payload = {}
    if desired_nodes is not None:
        update_payload["desiredNodes"] = desired_nodes
    if min_nodes is not None:
        update_payload["minNodes"] = min_nodes
    if max_nodes is not None:
        update_payload["maxNodes"] = max_nodes
    if autoscale is not None:
        update_payload["autoscale"] = autoscale

    if not update_payload:
        raise ValueError("No update parameters provided")

    print(f"\nUpdating node pool {node_pool_id}...")
    print(f"Request Payload: {json.dumps(update_payload, indent=2)}\n")

    path = (
        f"/cloud/project/{client.project_id}/kube/{cluster_id}/nodepool/{node_pool_id}"
    )
    client.request("PUT", path, update_payload)
    print("Node pool update initiated.")

    if wait:
        _wait_for_item_ready(
            client,
            "kube node pool",
            kube_node_pool_get,
            [cluster_id, node_pool_id],
            "READY",
        )


def kube_node_pool_node_list(
    cluster_id: str,
    node_pool_id: str,
    client: OVHClient | None = None,
) -> list[KubeNodePoolNode]:
    """List all nodes in a node pool."""
    client = client or _get_default_client()
    path = f"/cloud/project/{client.project_id}/kube/{cluster_id}/nodepool/{node_pool_id}/nodes"
    response = client.request("GET", path)
    return [
        KubeNodePoolNode(**item)
        for item in response
        if item.get("status") != "DELTETED"
    ]


def kube_node_pool_delete(
    cluster_id: str,
    node_pool_id: str,
    wait: bool = True,
    client: OVHClient | None = None,
) -> None:
    """
    Delete a node pool from a Kubernetes cluster.
    Args:
        cluster_id: Cluster ID
        node_pool_id: Node pool ID
        wait: Wait for node pool to be deleted
        client: Optional OVHClient instance (uses default if not provided)
    """
    client = client or _get_default_client()
    print(f"\nDeleting node pool {node_pool_id}...")
    path = (
        f"/cloud/project/{client.project_id}/kube/{cluster_id}/nodepool/{node_pool_id}"
    )
    client.request("DELETE", path)
    print("Node pool deletion initiated.")

    if wait:
        _wait_for_item_deleted(
            client, "node pool", kube_node_pool_get, [cluster_id, node_pool_id]
        )
