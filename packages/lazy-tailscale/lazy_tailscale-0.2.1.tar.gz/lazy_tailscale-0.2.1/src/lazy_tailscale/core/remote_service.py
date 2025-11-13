import re
import subprocess

from lazy_tailscale.client.blocking_client import BlockingTailscaleClient
from lazy_tailscale.client.resources.device import Device

from .exceptions import PingTimeOutException, SSHConnectionException


class TailscaleRemoteService:
    def __init__(self, client: BlockingTailscaleClient):
        self.client = client

    def list_devices(self) -> list[Device]:
        with self.client:
            devices = self.client.list_devices()
        return devices

    def _parse_ping_response(self, output: str) -> tuple[str, int]:
        pattern = r"pong from .+? \(([0-9.]+)\) .+? in (\d+)ms"

        match = re.search(pattern, output)
        if match:
            ip_address = match.group(1)
            milliseconds = int(match.group(2))
            return (ip_address, milliseconds)

        raise ValueError("Ping response format is invalid")

    def ping_device(self, device: Device) -> tuple[str, int]:
        cmd = ["tailscale", "ping", device.name]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        except subprocess.TimeoutExpired:
            raise PingTimeOutException("Ping command timed out")

        return self._parse_ping_response(res.stdout)

    def ssh_into_device(self, device: Device) -> None:
        cmd = ["ssh", "-o", "ConnectTimeout=5", device.name]
        process = subprocess.run(cmd, text=True, capture_output=False, stdout=None, stderr=None)
        if process.returncode != 0:
            raise SSHConnectionException()
