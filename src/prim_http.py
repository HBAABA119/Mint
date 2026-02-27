"""
Prim HTTP Client
Provides HTTP/HTTPS support, request/response handling, connection pooling, and async HTTP.
"""

import urllib.request
import urllib.parse
import urllib.error
import json
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HTTPStatus(Enum):
    """HTTP status codes"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


@dataclass
class HTTPRequest:
    """HTTP request"""
    method: HTTPMethod
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Any] = None
    params: Optional[Dict[str, Any]] = None
    timeout: float = 30.0


@dataclass
class HTTPResponse:
    """HTTP response"""
    status: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    status_text: str = ""


class HTTPClient:
    """HTTP client for making requests"""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url
        self.default_headers: Dict[str, str] = {
            "User-Agent": "Prim/1.0"
        }
        self.timeout = 30.0

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> HTTPResponse:
        """GET request"""
        return self.request(
            HTTPMethod.GET,
            url,
            params=params,
            headers=headers
        )

    def post(self, url: str, body: Any = None, headers: Optional[Dict[str, str]] = None) -> HTTPResponse:
        """POST request"""
        return self.request(
            HTTPMethod.POST,
            url,
            body=body,
            headers=headers
        )

    def put(self, url: str, body: Any = None, headers: Optional[Dict[str, str]] = None) -> HTTPResponse:
        """PUT request"""
        return self.request(
            HTTPMethod.PUT,
            url,
            body=body,
            headers=headers
        )

    def delete(self, url: str, headers: Optional[Dict[str, str]] = None) -> HTTPResponse:
        """DELETE request"""
        return self.request(
            HTTPMethod.DELETE,
            url,
            headers=headers
        )

    def patch(self, url: str, body: Any = None, headers: Optional[Dict[str, str]] = None) -> HTTPResponse:
        """PATCH request"""
        return self.request(
            HTTPMethod.PATCH,
            url,
            body=body,
            headers=headers
        )

    def request(self, method: HTTPMethod, url: str, **kwargs) -> HTTPResponse:
        """Make an HTTP request"""
        # Build full URL
        full_url = self._build_url(url)

        # Prepare request
        request = HTTPRequest(method=method, url=full_url, **kwargs)

        # Add query parameters
        if request.params:
            query_string = urllib.parse.urlencode(request.params)
            if '?' in full_url:
                full_url += '&' + query_string
            else:
                full_url += '?' + query_string
            request.url = full_url

        # Prepare body
        body_data = None
        if request.body is not None:
            if isinstance(request.body, dict):
                body_data = json.dumps(request.body).encode('utf-8')
                request.headers['Content-Type'] = 'application/json'
            elif isinstance(request.body, str):
                body_data = request.body.encode('utf-8')
            else:
                body_data = request.body

        # Create request object
        req = urllib.request.Request(
            request.url,
            data=body_data,
            method=request.method.value,
            headers={**self.default_headers, **request.headers}
        )

        try:
            # Make request
            with urllib.request.urlopen(req, timeout=request.timeout) as response:
                # Read response
                response_data = response.read()

                # Parse response
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    body = json.loads(response_data.decode('utf-8'))
                else:
                    body = response_data.decode('utf-8')

                return HTTPResponse(
                    status=response.status,
                    headers=dict(response.headers),
                    body=body,
                    status_text=response.reason
                )

        except urllib.error.HTTPError as e:
            return HTTPResponse(
                status=e.code,
                body=None,
                status_text=e.reason
            )
        except urllib.error.URLError as e:
            return HTTPResponse(
                status=0,
                body=None,
                status_text=str(e.reason)
            )

    def _build_url(self, url: str) -> str:
        """Build full URL"""
        if self.base_url and not url.startswith('http'):
            return f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        return url


class AsyncHTTPClient:
    """Async HTTP client"""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url
        self.default_headers: Dict[str, str] = {
            "User-Agent": "Prim/1.0"
        }

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> HTTPResponse:
        """Async GET request"""
        return await self.request(
            HTTPMethod.GET,
            url,
            params=params,
            headers=headers
        )

    async def post(self, url: str, body: Any = None, headers: Optional[Dict[str, str]] = None) -> HTTPResponse:
        """Async POST request"""
        return await self.request(
            HTTPMethod.POST,
            url,
            body=body,
            headers=headers
        )

    async def request(self, method: HTTPMethod, url: str, **kwargs) -> HTTPResponse:
        """Make an async HTTP request"""
        # Run sync request in executor
        client = HTTPClient(self.base_url)
        client.default_headers = self.default_headers

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            client.request,
            method,
            url,
            **kwargs
        )

        return response


class HTTPClientPool:
    """Pool of HTTP clients"""

    def __init__(self, max_clients: int = 5):
        self.max_clients = max_clients
        self.clients: List[HTTPClient] = []
        self.current = 0

    def get_client(self) -> HTTPClient:
        """Get a client from the pool"""
        if self.clients:
            client = self.clients[self.current]
            self.current = (self.current + 1) % len(self.clients)
            return client

        if len(self.clients) < self.max_clients:
            client = HTTPClient()
            self.clients.append(client)
            return client

        return self.clients[0]

    def close_all(self):
        """Close all clients"""
        self.clients.clear()
        self.current = 0


class HTTPClientBuilder:
    """Builder for HTTP clients"""

    def __init__(self):
        self.base_url: Optional[str] = None
        self.headers: Dict[str, str] = {}
        self.timeout: float = 30.0
        self.follow_redirects: bool = True
        self.verify_ssl: bool = True

    def base_url(self, url: str) -> 'HTTPClientBuilder':
        """Set base URL"""
        self.base_url = url
        return self

    def header(self, name: str, value: str) -> 'HTTPClientBuilder':
        """Add a header"""
        self.headers[name] = value
        return self

    def timeout(self, seconds: float) -> 'HTTPClientBuilder':
        """Set timeout"""
        self.timeout = seconds
        return self

    def no_redirects(self) -> 'HTTPClientBuilder':
        """Disable redirects"""
        self.follow_redirects = False
        return self

    def no_ssl_verify(self) -> 'HTTPClientBuilder':
        """Disable SSL verification"""
        self.verify_ssl = False
        return self

    def build(self) -> HTTPClient:
        """Build the client"""
        client = HTTPClient(self.base_url)
        client.default_headers = {**client.default_headers, **self.headers}
        client.timeout = self.timeout
        return client


def http_client(base_url: Optional[str] = None) -> HTTPClient:
    """Create an HTTP client"""
    return HTTPClient(base_url)


def async_http_client(base_url: Optional[str] = None) -> AsyncHTTPClient:
    """Create an async HTTP client"""
    return AsyncHTTPClient(base_url)


def main():
    """Main entry point for testing"""
    print("Testing HTTP client...")

    # Create client
    client = http_client("https://httpbin.org")

    # Test GET request
    response = client.get("/get", params={"test": "value"})
    print(f"GET response: {response.status}")
    print(f"Response body: {response.body}")

    # Test POST request
    response = client.post("/post", body={"key": "value"})
    print(f"POST response: {response.status}")

    # Test builder
    builder = HTTPClientBuilder()
    builder.header("X-Custom", "value").timeout(10.0)
    client2 = builder.build()
    print(f"Built client with timeout: {client2.timeout}")

    # Test async client
    async def test_async():
        async_client = async_http_client("https://httpbin.org")
        response = await async_client.get("/get")
        print(f"Async GET response: {response.status}")

    asyncio.run(test_async())

    print("\nHTTP client initialized successfully")


if __name__ == "__main__":
    main()
