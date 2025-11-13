from typing import Unpack

from cmdi import CmdArgs, command, strip_cmdargs

from mewo_ovhcloud import lib


@command
def volume_create(
    name: str,
    region: str,
    size: int,
    description: str | None = None,
    image_id: str | None = None,
    snapshot_id: str | None = None,
    volume_type: lib.VolumeType = lib.VolumeType.classic,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.Volume:
    """
    Create a new OVHcloud volume.
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
    return lib.volume_create(**strip_cmdargs(locals()))


@command
def volume_get(
    volume_id: str,
    region: str,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.Volume | None:
    """
    Get detailed information about a volume.
    Args:
        volume_id: Volume ID
        region: OVH region (e.g., GRA7, BHS5)
        client: Optional OVHClient instance (uses default if not provided)
    Returns:
        Volume object with details about the volume
    """
    return lib.volume_get(**strip_cmdargs(locals()))


@command
def volume_list(
    region: str | None = None,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> list[lib.Volume]:
    """
    List all volumes in the project.
    Args:
        client: Optional OVHClient instance (uses default if not provided)
    Returns:
        List of Volume objects
    """
    return lib.volume_list(**strip_cmdargs(locals()))


@command
def volume_delete(
    volume_id: str,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> None:
    """
    Delete a volume.
    Args:
        volume_id: Volume ID
        client: Optional OVHClient instance (uses default if not provided)
    """
    return lib.volume_delete(**strip_cmdargs(locals()))


@command
def volume_snapshot_create(
    volume_id: str,
    name: str,
    description: str | None = None,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.VolumeSnapshot:
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
    return lib.volume_snapshot_create(**strip_cmdargs(locals()))


@command
def volume_snapshot_get(
    snapshot_id: str,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.VolumeSnapshot | None:
    """
    Get detailed information about a volume snapshot.
    Args:
        snapshot_id: Snapshot ID
        client: Optional OVHClient instance (uses default if not provided)
    Returns:
        VolumeSnapshot object with details about the snapshot
    """
    return lib.volume_snapshot_get(**strip_cmdargs(locals()))


@command
def volume_snapshot_list(
    region: str | None = None,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> list[lib.VolumeSnapshot]:
    """
    List all volume snapshots in the project.
    Args:
        region: Optional region filter
        client: Optional OVHClient instance (uses default if not provided)
    Returns:
        List of VolumeSnapshot objects
    """
    return lib.volume_snapshot_list(**strip_cmdargs(locals()))


@command
def volume_snapshot_delete(
    snapshot_id: str,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> None:
    """
    Delete a volume snapshot.
    Args:
        snapshot_id: Snapshot ID
        client: Optional OVHClient instance (uses default if not provided)
    """
    return lib.volume_snapshot_delete(**strip_cmdargs(locals()))


@command
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
    autobackup: lib.InstanceAutobackup | None = None,
    networks: list[lib.InstanceNetwork] | None = None,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.Instance:
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
    return lib.instance_create(**strip_cmdargs(locals()))


@command
def instance_get(
    instance_id: str,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.Instance | None:
    """Get detailed information about an instance."""
    return lib.instance_get(**strip_cmdargs(locals()))


@command
def instance_list(
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> list[lib.Instance]:
    """List all instances in the project."""
    return lib.instance_list(**strip_cmdargs(locals()))


def instance_start(
    instance_id: str,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.Instance:
    """
    Start an instance.

    Args:
        instance_id: Instance ID
        wait: Wait for instance to be started
        client: Optional OVHClient instance (uses default if not provided)
    """
    return lib.instance_start(**strip_cmdargs(locals()))


def instance_stop(
    instance_id: str,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.Instance:
    """
    Stop an instance.

    Args:
        instance_id: Instance ID
        wait: Wait for instance to be stopped
        client: Optional OVHClient instance (uses default if not provided)
    """
    return lib.instance_stop(**strip_cmdargs(locals()))


@command
def instance_delete(
    instance_id: str,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> None:
    """
    Delete an instance.
    Args:
        instance_id: Instance ID
        wait: Wait for instance to be deleted
        client: Optional OVHClient instance (uses default if not provided)
    """
    return lib.instance_delete(**strip_cmdargs(locals()))


@command
def kube_cluster_create(
    name: str,
    region: str,
    version: str,
    update_policy: str = "ALWAYS_UPDATE",
    private_network_id: str | None = None,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.KubeCluster:
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
    return lib.kube_cluster_create(**strip_cmdargs(locals()))


@command
def kube_cluster_get(
    cluster_id: str,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.KubeCluster | None:
    """Get detailed information about a Kubernetes cluster."""
    return lib.kube_cluster_get(**strip_cmdargs(locals()))


@command
def kube_cluster_get_by_name(
    cluster_name: str,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.KubeCluster | None:
    """Get detailed information about a Kubernetes cluster, select by name."""
    return lib.kube_cluster_get_by_name(**strip_cmdargs(locals()))


@command
def kube_cluster_list(
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> list[lib.KubeCluster]:
    """List all Kubernetes clusters in the project."""
    return lib.kube_cluster_list(**strip_cmdargs(locals()))


@command
def kube_cluster_delete(
    cluster_id: str,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> None:
    """
    Delete a Kubernetes cluster.
    Args:
        cluster_id: Cluster ID
        wait: Wait for cluster to be deleted
        client: Optional OVHClient instance (uses default if not provided)
    """
    return lib.kube_cluster_delete(**strip_cmdargs(locals()))


@command
def kube_cluster_get_kubeconfig(
    cluster_id: str,
    save_to_file: str | None = None,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.KubeConfig:
    """Get the kubeconfig for a Kubernetes cluster."""
    return lib.kube_cluster_get_kubeconfig(**strip_cmdargs(locals()))


@command
def kube_cluster_reset_kubeconfig(
    cluster_id: str,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.KubeConfig:
    """Reset/regenerate the kubeconfig for a Kubernetes cluster."""
    return lib.kube_cluster_reset_kubeconfig(**strip_cmdargs(locals()))


@command
def kube_node_pool_list(
    cluster_id: str,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> list[lib.KubeNodePool]:
    """List all node pools in a Kubernetes cluster."""
    return lib.kube_node_pool_list(**strip_cmdargs(locals()))


@command
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
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.KubeNodePool:
    """Create a new node pool in a Kubernetes cluster."""
    return lib.kube_node_pool_create(**strip_cmdargs(locals()))


@command
def kube_node_pool_get(
    cluster_id: str,
    node_pool_id: str,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> lib.KubeNodePool | None:
    """Get detailed information about a node pool."""
    return lib.kube_node_pool_get(**strip_cmdargs(locals()))


@command
def kube_node_pool_update(
    cluster_id: str,
    node_pool_id: str,
    desired_nodes: int | None = None,
    min_nodes: int | None = None,
    max_nodes: int | None = None,
    autoscale: bool | None = None,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> None:
    """Update a node pool (resize, change autoscaling settings)."""
    return lib.kube_node_pool_update(**strip_cmdargs(locals()))


@command
def kube_node_pool_node_list(
    cluster_id: str,
    node_pool_id: str,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> list[lib.KubeNodePoolNode]:
    """List all nodes in a node pool."""
    return lib.kube_node_pool_node_list(**strip_cmdargs(locals()))


@command
def kube_node_pool_delete(
    cluster_id: str,
    node_pool_id: str,
    wait: bool = True,
    client: lib.OVHClient | None = None,
    **cmdargs: Unpack[CmdArgs],
) -> None:
    """
    Delete a node pool from a Kubernetes cluster.
    Args:
        cluster_id: Cluster ID
        node_pool_id: Node pool ID
        wait: Wait for node pool to be deleted
        client: Optional OVHClient instance (uses default if not provided)
    """
    return lib.kube_node_pool_delete(**strip_cmdargs(locals()))
