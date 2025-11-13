# daffalib/api.py
import requests
from urllib.parse import urljoin
from requests.auth import AuthBase
from typing import Any, Dict, Optional, Tuple, Union

class API:
    """
    A modern wrapper for the requests library to simplify REST API interactions.

    This class provides methods for common HTTP requests (GET, POST, PUT, DELETE)
    and automatically handles JSON parsing and error reporting.
    """

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Union[Tuple[str, str], AuthBase]] = None,
    ):
        """
        Initializes the API client.

        Args:
            base_url (str): The base URL for all API endpoints.
            headers (Optional[Dict[str, str]]): A dictionary of headers to be
                                                 sent with every request.
            auth (Optional[Union[Tuple[str, str], AuthBase]]): Authentication tuple
                                                               or a requests AuthBase object.
        """
        self.base_url = base_url
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
        if auth:
            self.session.auth = auth

    def _handle_response(self, response: requests.Response) -> Union[Dict[str, Any], str]:
        """
        Private method to handle API responses.

        Parses JSON response, falls back to text, and raises HTTP errors for
        unsuccessful status codes.

        Args:
            response (requests.Response): The response object from a request.

        Returns:
            Union[Dict[str, Any], str]: The parsed JSON dictionary or the response text.

        Raises:
            requests.exceptions.HTTPError: For 4xx or 5xx status codes.
        """
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return response.text

    def get(self, endpoint: str = "", **kwargs: Any) -> Union[Dict[str, Any], str]:
        """
        Sends a GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to append to the base URL.
            **kwargs: Additional arguments passed to `requests.get`.

        Returns:
            Union[Dict[str, Any], str]: The response data.
        """
        url = urljoin(self.base_url, endpoint)
        response = self.session.get(url, **kwargs)
        return self._handle_response(response)

    def post(self, data: Dict[str, Any], endpoint: str = "", **kwargs: Any) -> Union[Dict[str, Any], str]:
        """
        Sends a POST request with JSON data to the specified endpoint.

        Args:
            data (Dict[str, Any]): The dictionary to send as JSON.
            endpoint (str): The API endpoint to append to the base URL.
            **kwargs: Additional arguments passed to `requests.post`.

        Returns:
            Union[Dict[str, Any], str]: The response data.
        """
        url = urljoin(self.base_url, endpoint)
        response = self.session.post(url, json=data, **kwargs)
        return self._handle_response(response)

    def put(self, endpoint: str, data: Dict[str, Any], **kwargs: Any) -> Union[Dict[str, Any], str]:
        """
        Sends a PUT request with JSON data to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to append to the base URL.
            data (Dict[str, Any]): The dictionary to send as JSON.
            **kwargs: Additional arguments passed to `requests.put`.

        Returns:
            Union[Dict[str, Any], str]: The response data.
        """
        url = urljoin(self.base_url, endpoint)
        response = self.session.put(url, json=data, **kwargs)
        return self._handle_response(response)

    def delete(self, endpoint: str, **kwargs: Any) -> Union[Dict[str, Any], str]:
        """
        Sends a DELETE request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to append to the base URL.
            **kwargs: Additional arguments passed to `requests.delete`.

        Returns:
            Union[Dict[str, Any], str]: The response data.
        """
        url = urljoin(self.base_url, endpoint)
        response = self.session.delete(url, **kwargs)
        return self._handle_response(response)