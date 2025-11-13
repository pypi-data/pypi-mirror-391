import platform
import re
import subprocess
from logging import getLogger

import httpx

from .status import TailscaleStatus
from .exceptions import ConnectionFailedError

logger = getLogger(__name__)


class TailscaleLocalClient:
    def __init__(self) -> None:
        self.client = self._initialize_client()

    def _make_request(self, endpoint: str):
        response = self.client.get(endpoint)
        response.raise_for_status()
        return response.json()

    def _initialize_client(self) -> httpx.Client:
        platform_name = platform.system().lower()
        if platform_name == "darwin":
            return self._create_client_macos()
        elif platform_name == "linux":
            return self._create_client_linux()
        raise NotImplementedError(f"Tailscale client not implemented for {platform_name}")

    def _create_client_macos(self) -> httpx.Client:
        cmd = ["lsof", "-n", "-a", "-c", "IPNExtension", "-F"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        match = re.search(r"sameuserproof-(\d+)-([\w]+)", result.stdout)
        if not match:
            raise ConnectionFailedError("Could not find Tailscale Local API info on macOS")

        port, password = match.group(1), match.group(2)
        base_url = f"http://127.0.0.1:{port}/localapi/v0/"
        return httpx.Client(base_url=base_url, auth=("", password), timeout=5.0)

    def _create_client_linux(self) -> httpx.Client:
        transport = httpx.HTTPTransport(uds="/run/tailscale/tailscaled.sock")
        return httpx.Client(base_url="http://local-tailscaled.sock/localapi/v0/", transport=transport, timeout=5.0)

    def close(self) -> None:
        self.client.close()

    def status(self) -> TailscaleStatus:
        logger.debug("Fetching Tailscale status from local API")
        data = self._make_request("status")
        return TailscaleStatus(**data)
