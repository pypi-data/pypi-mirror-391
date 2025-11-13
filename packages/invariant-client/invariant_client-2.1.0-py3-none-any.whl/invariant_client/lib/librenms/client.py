from urllib.parse import urljoin
import httpx
import sys


class LibreNMSClient:
    """Grabs hosts from the LibreNMS device inventory and then logs into
    each device and gathers configs.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = urljoin(base_url, "/api/v0/")
        headers = {"Authorization": f"Bearer {api_key}"}
        self.client = httpx.Client(headers=headers)
        try:
            self.test_connection()
        except ConnectionError as e:
            raise ConnectionError(e)

    def _request(self, method: str, endpoint: str, **kwargs: dict):
        """Base request method."""
        try:
            url = urljoin(self.base_url, endpoint)
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectTimeout:
            raise ConnectionError(
                f"Unable to connect to {self.base_url} due to connection timeout."
            )
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"Error connecting to endpoint: {e}")

    def _get(self, endpoint: str):
        return self._request("GET", endpoint, params={"format": "json"})

    def test_connection(self):
        return self._get("system")

    def get_device(self, node_id: str):
        return self._get(f"devices/{node_id}")

    def get_devices_by_group(self, group: str):
        try:
            result = self._get(f"devicegroups/{group}")
        except ConnectionError as e:
            if "404 Not Found" in str(e):
                print(f"Error, device group {group} not found.")
            else:
                print(e)
            sys.exit(1)
        return result
