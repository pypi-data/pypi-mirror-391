from requests import HTTPError, Session

from .exceptions import ServerError, UnauthorizedError
from .resources import Device


class BlockingTailscaleClient:
    BASE_URL = "https://api.tailscale.com/api/v2"

    def __init__(self, api_key: str, tailnet: str = "-"):
        self._api_key = api_key
        self._tailnet = tailnet

        self._open_session = None

    @property
    def _token_header(self):
        return {"Authorization": f"Bearer {self._api_key}"}

    @property
    def _session(self) -> Session:
        if not self._open_session:
            session = Session()
            session.headers.update(self._token_header)
            self._open_session = session

        return self._open_session

    def close_session(self) -> None:
        if self._open_session:
            self._session.close()
            self._open_session = None

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        if self._open_session:
            self.close_session()

    def _make_request(self, url: str):
        response = self._session.get(url)

        try:
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 401:
                raise UnauthorizedError("Not authorized")
            if e.response.status_code == 500:
                raise ServerError("Internal error in Tailscale server")
            raise e

    def list_devices(self, tailnet: str | None = None) -> list[Device]:
        # TODO: Add query parameters option
        tailnet = tailnet or self._tailnet
        url = f"{self.BASE_URL}/tailnet/{tailnet}/devices?fields=all"
        resp = self._make_request(url)
        json = resp["devices"]
        return [Device(**device) for device in json]

    def get_device(self, id: str) -> Device:
        url = f"{self.BASE_URL}/device/{id}"
        resp = self._session.get(url)
        return Device(**resp.json())
