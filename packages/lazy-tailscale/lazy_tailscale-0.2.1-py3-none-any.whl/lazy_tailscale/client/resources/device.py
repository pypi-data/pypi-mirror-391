from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Latency(BaseModel):
    preferred: bool = Field(default=False, description="'true' for the node's preferred DERP server for incoming traffic.")
    latency_ms: float = Field(alias="latencyMs", description="Current latency to DERP server.")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ClientSupports(BaseModel):
    """Identifies features supported by the client."""

    hair_pinning: Optional[bool] = Field(
        default=None, alias="hairPinning", description="True if router can route LAN connections back to LAN using global IP:port"
    )
    ipv6: bool = Field(description="True if device OS supports IPv6")
    pcp: bool = Field(description="True if PCP port-mapping service exists on router")
    pmp: bool = Field(description="True if NAT-PMP port-mapping service exists on router")
    udp: bool = Field(description="True if UDP traffic is enabled on current network")
    upnp: bool = Field(description="True if UPnP port-mapping service exists on router")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ClientConnectivity(BaseModel):
    """Report on the device's current physical network conditions."""

    endpoints: list[str] = Field(description="Client's magicsock UDP IP:port endpoints (IPv4 or IPv6)")
    mapping_varies_by_dest_ip: bool = Field(
        default=False, alias="mappingVariesByDestIP", description="True if host's NAT mappings vary based on destination IP"
    )
    latency: dict[str, Latency] = Field(description="Map of DERP server locations and their current latency in seconds")
    client_supports: ClientSupports = Field(alias="clientSupports", description="Features supported by the client")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class PostureIdentity(BaseModel):
    """Extra identifiers from the device for posture identification."""

    disabled: Optional[bool] = None


class Device(BaseModel):
    """A Tailscale device (node/machine) in a tailnet."""

    addresses: list[str] = Field(description="List of Tailscale IP addresses (IPv4 and IPv6)")
    id: str = Field(description="Legacy identifier for the device (deprecated, use nodeId)")
    node_id: str = Field(alias="nodeId", description="Preferred identifier for the device")
    user: str = Field(description="User who registered the node")
    name: str = Field(description="MagicDNS name of the device")
    hostname: str = Field(description="Machine name in the admin console")
    client_version: str = Field(default="", alias="clientVersion", description="Version of Tailscale client software")
    update_available: Optional[bool] = Field(
        default=None, alias="updateAvailable", description="True if a client version upgrade is available"
    )
    os: str = Field(description="Operating system the device is running")
    created: Optional[datetime] = Field(default=None, description="Date the device was added to the tailnet")
    connected_to_control: bool = Field(
        alias="connectedToControl", description="Whether device recently maintained connection to control server"
    )
    last_seen: Optional[datetime] = Field(default=None, alias="lastSeen", description="When device was last connected to control server")
    key_expiry_disabled: bool = Field(alias="keyExpiryDisabled", description="True if device keys will not expire")
    expires: Optional[datetime] = Field(default=None, description="Expiration date of device's auth key")
    authorized: bool = Field(description="True if device has been authorized to join the tailnet")
    is_external: bool = Field(alias="isExternal", description="True if device is shared into tailnet but not a member")
    multiple_connections: Optional[bool] = Field(
        default=None, alias="multipleConnections", description="True if multiple devices use the same node key"
    )
    machine_key: str = Field(default="", alias="machineKey", description="For internal use, empty for external devices")
    node_key: str = Field(alias="nodeKey", description="Required for select operations like adding to locked tailnet")
    blocks_incoming_connections: bool = Field(
        alias="blocksIncomingConnections", description="True if device cannot accept connections over Tailscale"
    )
    enabled_routes: list[str] = Field(default_factory=list, alias="enabledRoutes", description="Subnet routes approved by tailnet admin")
    advertised_routes: list[str] = Field(
        default_factory=list, alias="advertisedRoutes", description="Subnets this device requests to expose"
    )
    client_connectivity: Optional[ClientConnectivity] = Field(
        default=None, alias="clientConnectivity", description="Report on device's current physical network conditions"
    )
    tags: list[str] = Field(default_factory=list, description="Tags assigned to the device for ACL purposes")
    tailnet_lock_error: Optional[str] = Field(
        default=None, alias="tailnetLockError", description="Issue with tailnet lock node-key signature"
    )
    tailnet_lock_key: str = Field(alias="tailnetLockKey", description="Node's tailnet lock key")
    ssh_enabled: Optional[bool] = Field(default=None, alias="sshEnabled", description="True if Tailscale SSH is enabled")
    posture_identity: Optional[PostureIdentity] = Field(
        default=None, alias="postureIdentity", description="Extra identifiers for device posture identification"
    )
    is_ephemeral: Optional[bool] = Field(default=None, alias="isEphemeral", description="True if the device is ephemeral")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
