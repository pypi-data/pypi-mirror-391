import requests
from typing import Optional
from .models import (
    UserInformationResponse,
    ManagedClashResponse,
    NodeListResponse,
    UserInformationData,
    ManagedClashData,
    LoginResponse
)


class DlerAPIClient:
    """A Python client for the Dler API."""

    def __init__(self, token: str, base_url: str = "https://dler.cloud/api/v1"):
        """
        Initializes the DlerAPIClient.

        Args:
            token: Your Dler API access token.
            base_url: The base URL for the Dler API.
        """
        if not token:
            raise ValueError("API token cannot be empty.")
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.token_for_body = {"access_token": token}

    @staticmethod
    def login(email: str, password: str, base_url: str = "https://dler.cloud/api/v1") -> str:
        """
        Logs in to the Dler API to retrieve an access token.

        Args:
            email: User's email.
            password: User's password.
            base_url: The base URL for the Dler API.

        Returns:
            The access token string.
        """
        url = f"{base_url}/login"
        data = {"email": email, "passwd": password}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("ret") != 200:
                raise ConnectionError(f"API login failed: {response_data.get('msg', 'Unknown error')}")

            login_response = LoginResponse(**response_data)
            return login_response.data.token
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}") from e
        except ValueError:
            raise ValueError("Failed to decode API response as JSON.")

    def _post(self, endpoint: str, extra_data: Optional[dict] = None) -> dict:
        """Helper method to make POST requests."""
        url = f"{self.base_url}{endpoint}"
        data = self.token_for_body.copy()
        if extra_data:
            data.update(extra_data)

        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            # Handle connection errors, timeouts, etc.
            raise ConnectionError(f"API request failed: {e}") from e
        except ValueError:
            # Handle JSON decoding errors
            raise ValueError("Failed to decode API response as JSON.")

    def get_account_info(self) -> UserInformationData:
        """
        Fetches user information.
        Corresponds to the /api/v1/information endpoint.

        Returns:
            A Pydantic model containing user information.
        """
        response_data = self._post("/information")
        # The actual data is nested within the 'data' key
        return UserInformationResponse(**response_data).data

    def get_managed_config(self) -> ManagedClashData:
        """
        Fetches managed Clash configuration URLs.
        Corresponds to the /api/v1/managed/clash endpoint.

        Returns:
            A Pydantic model containing the Clash configuration details.
        """
        response_data = self._post("/managed/clash")
        # This endpoint has a unique structure where the data is at the top level
        # We manually construct the data object for the model.
        data_for_model = {
            "ret": response_data.get("ret"),
            "msg": response_data.get("msg"),
            "name": response_data.get("name"),
            "smart": response_data.get("smart"),
            "ss": response_data.get("ss"),
            "vmess": response_data.get("vmess"),
            "trojan": response_data.get("trojan"),
            "ss2022": response_data.get("ss2022"),
        }
        return ManagedClashData(**response_data)

    def get_nodes(self) -> NodeListResponse:
        """
        Fetches the list of available nodes.
        Corresponds to the /api/v1/nodes/list endpoint.

        Returns:
            A Pydantic model containing a list of nodes.
        """
        response_data = self._post("/nodes/list")
        return NodeListResponse(**response_data)
