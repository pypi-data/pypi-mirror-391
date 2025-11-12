import platform
import re
import subprocess
from logging import getLogger

import requests

from .status import TailscaleStatus

logger = getLogger(__name__)


class TailscaleLocalClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.base_url = None
        self.online = False
        try:
            self._connect()
        except ConnectionFailedError:
            pass

    def _connect(self) -> None:
        port, password = self._get_local_api_info()
        self.base_url = f"http://127.0.0.1:{port}/localapi/v0"
        self.session.auth = ("", password)
        self.online = True

    def _make_request(self, endpoint: str):
        if not self.online:
            self._reconnect()

        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ConnectionError):
            self.online = False
            self._reconnect()
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()

    def _reconnect(self) -> None:
        try:
            self._connect()
        except ConnectionFailedError:
            raise NotConnectedError("Tailscale Local API is not reachable")

    def _get_local_api_info(self) -> tuple[str, str]:
        platform_name = platform.system().lower()
        if platform_name == "darwin":
            return self._get_macos_localapi_info()
        raise NotImplementedError(f"Local API info retrieval not implemented for {platform_name}")

    def _get_macos_localapi_info(self) -> tuple[str, str]:
        cmd = "lsof -n -a -c IPNExtension -F"
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        match = re.search(r"sameuserproof-(\d+)-([\w]+)", result.stdout)
        if not match:
            raise ConnectionFailedError("Could not find Tailscale Local API info on macOS")
        return match.group(1), match.group(2)

    def status(self) -> TailscaleStatus:
        logger.debug("Fetching Tailscale status from local API")
        try:
            return TailscaleStatus(**self._make_request("status"))
        except Exception as e:
            logger.error(f"Error fetching Tailscale status: {e}")
            raise NotConnectedError()


class ConnectionFailedError(Exception):
    pass


class NotConnectedError(Exception):
    pass
