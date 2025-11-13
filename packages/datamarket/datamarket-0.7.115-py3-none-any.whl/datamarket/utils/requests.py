########################################################################################################################
# IMPORTS

import logging
from datetime import timedelta
from typing import Any, Dict, Optional, Sequence

from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from rnet import Emulation, Proxy
from rnet.blocking import Client
from rnet.blocking import Response as RnetResponse
from rnet.exceptions import ConnectionError, TimeoutError, TlsError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    retry_if_not_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
)

from datamarket.exceptions.main import IgnoredHTTPError

from ..exceptions import BadRequestError, EmptyResponseError, NotFoundError, RedirectionDetectedError
from ..interfaces.proxy import ProxyInterface
from .main import ban_sleep

########################################################################################################################
# SETUP LOGGER

logger = logging.getLogger(__name__)

########################################################################################################################
# CLASSES


class RequestsCompatibleResponse:
    """
    A wrapper around rnet Response that provides backward compatibility with requests.Response API.

    This class wraps an rnet Response object and provides properties and methods that match
    the requests library API, allowing legacy code to work without modifications.
    """

    def __init__(self, rnet_response: RnetResponse):
        """
        Initialize the compatibility wrapper.

        Args:
            rnet_response: The rnet Response object to wrap
        """
        self._rnet_response = rnet_response

    # Backward-compatible properties (requests-style)
    @property
    def text(self) -> str:
        """Get response text (requests-compatible property)."""
        return self._rnet_response.text()

    @property
    def content(self) -> bytes:
        """Get response content as bytes (requests-compatible property)."""
        return self._rnet_response.bytes()

    @property
    def status_code(self) -> int:
        """Get HTTP status code (requests-compatible property)."""
        return self._rnet_response.status.as_int()

    @property
    def headers(self) -> Dict[str, str]:
        """Get response headers (requests-compatible property)."""
        # Convert rnet headers to dict with string keys and values
        headers = {}
        for key, value in self._rnet_response.headers:
            key_str = key.decode("utf-8") if isinstance(key, bytes) else str(key)
            value_str = value.decode("utf-8") if isinstance(value, bytes) else str(value)
            headers[key_str] = value_str
        return headers

    @property
    def url(self) -> str:
        """Get the final URL (requests-compatible property)."""
        return str(self._rnet_response.url)

    @property
    def ok(self) -> bool:
        """Check if response status is 2xx (requests-compatible property)."""
        return self._rnet_response.status.is_success()

    # rnet-style methods for forward compatibility
    def bytes(self) -> bytes:
        """Get response content as bytes (rnet-style method)."""
        return self._rnet_response.bytes()

    def json(self) -> Any:
        """Parse response as JSON (compatible with both APIs)."""
        return self._rnet_response.json()

    @property
    def status(self):
        """Get rnet status object (rnet-style property)."""
        return self._rnet_response.status

    def raise_for_status(self) -> None:
        """
        Raise HTTPError if status is not 2xx (requests-compatible method).
        The raised exception includes the response object accessible via e.response.
        """
        if not self._rnet_response.status.is_success():
            status_code = self._rnet_response.status.as_int()
            url = str(self._rnet_response.url)
            error = HTTPError(f"HTTP {status_code} error for {url}")
            error.response = self
            raise error

    def __getattr__(self, name):
        """Forward any other attribute access to the underlying rnet response."""
        return getattr(self._rnet_response, name)


class RequestsClient:
    """A robust, proxy-enabled HTTP client with retry logic and flexible output formats."""

    def __init__(self, proxy_interface: Optional[ProxyInterface] = None):
        """
        Initializes the HTTP client.

        Args:
            proxy_interface (Optional[ProxyInterface], optional): Proxy provider. If None, no proxy is used. Defaults to None.
        """
        self.proxy_interface = proxy_interface
        # Create a base client without proxy (proxy will be set per-request)
        self.client = Client(
            emulation=Emulation.Firefox143,
            cookie_store=True,  # Enable cookie store for session continuity
            allow_redirects=True,
            max_redirects=10,
        )

    @retry(
        retry=retry_if_exception_type((TlsError, TimeoutError, ConnectionError)),
        wait=wait_exponential(exp_base=3, multiplier=3, max=60),
        stop=stop_after_delay(timedelta(minutes=10)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def _request_with_proxy_retry(self, url: str, method: str, use_auth: bool, **params):
        """
        Performs an HTTP request with proxy retry logic using rnet BlockingClient.

        Args:
            url (str): The target URL to fetch data from.
            method (str): HTTP method to use (e.g., 'GET', 'POST').
            use_auth (bool): Whether to use authenticated proxies.
            **params: Additional arguments passed to the request method.

        Returns:
            RequestsCompatibleResponse: A wrapped HTTP response object compatible with both rnet and requests APIs.
        """
        logger.info(f"Fetching data from {url} ...")

        proxy_obj = None
        if self.proxy_interface:
            host, port, user, pwd = self.proxy_interface.get_proxies(raw=True, use_auth=use_auth)
            if host and port:
                proxy_url = f"http://{host}:{port}"
                # Create Proxy object using rnet.Proxy.all() with credentials if available
                proxy_obj = Proxy.all(proxy_url, username=user, password=pwd) if user and pwd else Proxy.all(proxy_url)
                logger.info(f"Using proxy: {host}:{port}")

        request_params = params.copy()

        # Make it compatible with requests
        if "data" in request_params:
            request_params["form"] = request_params.pop("data")

        if proxy_obj:
            request_params["proxy"] = proxy_obj

        rnet_response = getattr(self.client, method.lower())(url, **request_params)
        return RequestsCompatibleResponse(rnet_response)

    @retry(
        retry=retry_if_not_exception_type((NotFoundError, BadRequestError, RedirectionDetectedError, IgnoredHTTPError)),
        wait=wait_exponential(exp_base=3, multiplier=3, max=60),
        stop=stop_after_attempt(5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def get_data(
        self,
        url: str,
        method: str = "GET",
        output: str = "json",
        sleep: tuple = (6, 3),
        use_auth_proxies: bool = False,
        max_proxy_delay: timedelta = timedelta(minutes=10),
        ignored_status_codes: Sequence[int] = (),
        **kwargs,
    ):
        """
        Fetches data from a given URL using HTTP requests with rnet, with support for proxy configuration, retries, and flexible output formats.

        Args:
            url (str): The target URL to fetch data from.
            method (str, optional): HTTP method to use (e.g., 'GET', 'POST'). Defaults to 'GET'.
            output (str, optional): Output format ('json', 'text', 'soup', 'response'). Defaults to 'json'.
            sleep (tuple, optional): Tuple specifying max and min sleep times (seconds) after request. Defaults to (6, 3).
            use_auth_proxies (bool, optional): Whether to use authenticated proxies. Defaults to False.
            max_proxy_delay (timedelta, optional): Maximum delay for proxy retry logic. Defaults to 10 minutes.
            ignored_status_codes (Sequence[int], optional): Status codes to ignore and return response for. Defaults to ().
            **kwargs: Additional arguments passed to the rnet request method. Supported parameters:
                - timeout (int): Total timeout in seconds (default: 30)
                - read_timeout (int): Read timeout in seconds
                - headers (Dict[str, str]): Custom headers
                - cookies (Dict[str, str]): Custom cookies
                - json (Dict[str, Any]): JSON body for POST/PUT requests
                - form (Dict[str, str] or List[Tuple[str, str]]): Form data
                - body (str or bytes): Raw request body
                - query (List[Tuple[str, str]]): Query parameters
                - auth (str): Authorization header value
                - basic_auth (Tuple[str, Optional[str]]): Basic auth credentials
                - bearer_auth (str): Bearer token
                - allow_redirects (bool): Allow redirects (default: True)
                - max_redirects (int): Max number of redirects
                - And other rnet Request parameters

        Returns:
            Depends on the 'output' argument:
            - 'json': Parsed JSON response.
            - 'text': Response text.
            - 'soup': BeautifulSoup-parsed HTML.
            - 'response': Raw rnet Response object.

        Raises:
            IgnoredHTTPError: If a response status code is in `ignored_status_codes`.
            NotFoundError: If a 404 or 410 status code is returned and not in `ignored_status_codes`.
            BadRequestError: If a 400 status code is returned and not in `ignored_status_codes`.
            EmptyResponseError: If the response has no content.
        """
        # Set default timeout if not provided
        params = kwargs.copy()

        if "timeout" not in params and "read_timeout" not in params:
            params["timeout"] = 30

        r = self._request_with_proxy_retry.retry_with(stop=stop_after_delay(max_proxy_delay))(
            self, url, method, use_auth_proxies, **params
        )

        ban_sleep(*sleep)

        # Get status code as integer (both rnet-style and requests-style work)
        status_code = r.status_code

        if status_code in ignored_status_codes:
            raise IgnoredHTTPError(message=f"Status {status_code} in ignored_status_codes for URL {url}", response=r)

        error_handlers = {
            404: lambda: NotFoundError(message=f"404 Not Found error for {url}", response=r),
            410: lambda: NotFoundError(message=f"410 Gone error for {url}", response=r),
            400: lambda: BadRequestError(message=f"400 Bad Request error for {url}", response=r),
        }

        if status_code in error_handlers:
            raise error_handlers[status_code]()

        # Use raise_for_status() which raises HTTPError with response accessible via e.response
        r.raise_for_status()

        response_content = r.content
        if not response_content:
            raise EmptyResponseError(message=f"Empty response received from {url} (status {status_code})", response=r)

        output_format = {
            "json": lambda: r.json(),
            "text": lambda: r.text,
            "soup": lambda: BeautifulSoup(response_content, "html.parser"),
            "response": lambda: r,
        }

        if output in output_format:
            return output_format[output]()

        raise ValueError(f"Unsupported output format: {output}")
