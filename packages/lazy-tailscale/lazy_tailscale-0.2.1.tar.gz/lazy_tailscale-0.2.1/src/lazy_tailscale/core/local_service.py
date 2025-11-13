import subprocess

from lazy_tailscale.local_client import TailscaleLocalClient, TailscaleStatus

from .exceptions import ExitNodeActivationException


class TailscaleLocalService:
    def __init__(self, client: TailscaleLocalClient):
        self.client = client

    def get_status_info(self) -> TailscaleStatus:
        return self.client.status()

    def activate_exit_node(self, hostname: str) -> None:
        cmd = ["tailscale", "set", "--exit-node", hostname]
        process = subprocess.run(cmd, timeout=3)
        if process.returncode != 0:
            raise ExitNodeActivationException()

    def deactivate_exit_node(self) -> None:
        cmd = ["tailscale", "set", "--exit-node", ""]
        process = subprocess.run(cmd, timeout=3, stderr=None, stdout=None)
        if process.returncode != 0:
            raise ExitNodeActivationException()
