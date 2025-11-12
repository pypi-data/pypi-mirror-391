import logging
import os
import sys
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

from lazy_tailscale.client import BlockingTailscaleClient
from lazy_tailscale.core.local_service import TailscaleLocalService
from lazy_tailscale.core.protocols import TailscaleLocalServiceProtocol, TailscaleRemoteServiceProtocol
from lazy_tailscale.core.remote_service import TailscaleRemoteService
from lazy_tailscale.local_client import TailscaleLocalClient

logger = getLogger(__name__)

DEFAULT_CONFIG_PATH: Path = Path.home() / ".lazy_tailscale"
API_CREDENTIALS_FILE_NAME: str = "credentials"


WELCOME_MESSAGE = """
Welcome to Lazy Tailscale!
To authenticate against the Tailscale API.
You can create an API key from the Tailscale Admin Console: `https://login.tailscale.com/admin/settings/keys`

After creating the API key set the environment variable `LAZY_TAILSCALE_API_KEY` to the value of the key.
Alternatively store the key in ~/.lazy_tailscale/credeitials.
Use `lazytailscale --token <api_key>` to store the key.
Going forward the token will be read from the config file.
"""


@dataclass
class AppDependencies:
    config_path: Path
    remote_service: TailscaleRemoteServiceProtocol
    local_service: TailscaleLocalServiceProtocol


def read_api_token_from_config(config_path: Path) -> str | None:
    try:
        with open(config_path / API_CREDENTIALS_FILE_NAME, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.info(f"API credentials file not found in {config_path}.")
        return None


def write_api_token_to_config(config_path: Path, api_key: str) -> None:
    credentials_file = config_path / API_CREDENTIALS_FILE_NAME
    credentials_file.touch(mode=0o600, exist_ok=True)
    with open(credentials_file, "w") as f:
        f.write(api_key)


def get_config_path() -> Path:
    return Path(os.getenv("LAZY_TAILSCALE_CONFIG_PATH", DEFAULT_CONFIG_PATH))


def initialise_dependencies() -> AppDependencies:
    config_path = get_config_path()

    if not config_path.exists():
        logger.info(f"Creating config directory at {config_path}")
        config_path.mkdir(parents=True, exist_ok=True, mode=0o700)

    # TODO: Configure more sophisticated logging
    logging.basicConfig(
        level="DEBUG",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(config_path / "app.log")],
    )

    api_key = os.getenv("LAZY_TAILSCALE_API_KEY")
    if api_key:
        logger.info("Writing API key from environment variable to config file")
        write_api_token_to_config(config_path, api_key)
    else:
        logger.info("Reading API key from config file")
        api_key = read_api_token_from_config(config_path)

    if not api_key:
        print(WELCOME_MESSAGE)
        sys.exit(1)

    client = BlockingTailscaleClient(api_key=api_key)
    local_client = TailscaleLocalClient()

    remote_service = TailscaleRemoteService(client)
    local_service = TailscaleLocalService(local_client)

    return AppDependencies(config_path=config_path, remote_service=remote_service, local_service=local_service)
