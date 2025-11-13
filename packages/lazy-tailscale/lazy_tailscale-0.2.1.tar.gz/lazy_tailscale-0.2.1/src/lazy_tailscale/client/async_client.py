from aiohttp import ClientError, ClientSession

from .exceptions import ServerError, UnauthorizedError
from .resources import Device


class AsyncTailscaleClient:
    BASE_URL = "https://api.tailscale.com/api/v2"

    def __init__(self, api_key: str, tailnet: str = "-"):
        self._api_key = api_key
        self._tailnet = tailnet

        self._open_session = None

    @property
    def _token_header(self):
        return {"Authorization": f"Bearer {self._api_key}"}

    @property
    def _session(self) -> ClientSession:
        if not self._open_session:
            session = ClientSession()
            session.headers.update(self._token_header)
            self._open_session = session

        return self._open_session

    async def close_session(self) -> None:
        if self._open_session:
            await self._session.close()
            self._open_session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        if self._open_session:
            await self.close_session()

    async def _make_request(self, url: str):
        response = await self._session.get(url)

        try:
            response.raise_for_status()
            return await response.json()
        except ClientError as e:
            if response.status == 401:
                raise UnauthorizedError("Not authorized")
            if response.status == 500:
                raise ServerError("Internal error in Tailscale server")
            raise e

    async def list_devices(self, tailnet: str | None = None) -> list[Device]:
        # TODO: Add query parameters option
        tailnet = tailnet or self._tailnet
        url = f"{self.BASE_URL}/tailnet/{tailnet}/devices"
        resp = await self._make_request(url)
        json = resp["devices"]
        return [Device(**device) for device in json]

    async def get_device(self, id: str) -> Device:
        url = f"{self.BASE_URL}/device/{id}"
        resp = await self._make_request(url)
        return Device(**resp)
