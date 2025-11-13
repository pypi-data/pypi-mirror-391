from typing import Protocol

from lazy_tailscale.client.resources.device import Device
from lazy_tailscale.local_client.status import TailscaleStatus


class TailscaleRemoteServiceProtocol(Protocol):
    def list_devices(self) -> list[Device]: ...

    def ping_device(self, device: Device) -> tuple[str, int]: ...

    def ssh_into_device(self, device: Device) -> None: ...


class TailscaleLocalServiceProtocol(Protocol):
    def get_status_info(self) -> TailscaleStatus: ...

    def activate_exit_node(self, hostname: str) -> None: ...

    def deactivate_exit_node(self) -> None: ...
