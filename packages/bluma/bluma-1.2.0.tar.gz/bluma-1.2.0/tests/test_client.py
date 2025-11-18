"""
Tests for Bluma client initialization and core functionality
"""
import pytest
from pytest_httpx import HTTPXMock
from bluma import Bluma
from bluma.errors import BlumaError, AuthenticationError, RateLimitError


class TestClientInitialization:
    """Test client initialization"""

    def test_client_init_with_api_key(self, api_key):
        """Test successful client initialization"""
        client = Bluma(api_key=api_key)
        assert client.api_key == api_key
        assert client.base_url == "https://api.bluma.app/api/v1"
        assert client.timeout == 30.0
        assert client.max_retries == 3

    def test_client_init_without_api_key(self):
        """Test client initialization fails without API key"""
        with pytest.raises(BlumaError, match="API key is required"):
            Bluma(api_key="")

    def test_client_init_with_custom_config(self, api_key):
        """Test client initialization with custom configuration"""
        client = Bluma(
            api_key=api_key,
            base_url="https://custom.api.com/v1",
            timeout=60.0,
            max_retries=5,
            retry_delay=2.0,
            retry_multiplier=3.0,
        )
        assert client.base_url == "https://custom.api.com/v1"
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.retry_delay == 2.0
        assert client.retry_multiplier == 3.0

    def test_client_resources_initialized(self, client):
        """Test all resource classes are initialized"""
        assert client.videos is not None
        assert client.templates is not None
        assert client.credits is not None
        assert client.api_keys is not None
        assert client.webhooks is not None
        assert client.usage is not None
        assert client.variants is not None
        assert client.collections is not None
        assert client.assets is not None


class TestContextManager:
    """Test client context manager functionality"""

    def test_context_manager_enters_and_exits(self, api_key):
        """Test client works as context manager"""
        with Bluma(api_key=api_key) as client:
            assert client.api_key == api_key

    def test_context_manager_closes_connection(self, api_key):
        """Test context manager closes HTTP client"""
        client = Bluma(api_key=api_key)
        with client:
            assert client._client is not None
        # After exiting context, client should be closed
        # httpx.Client.is_closed is the attribute to check
        assert client._client.is_closed


class TestRequestHandling:
    """Test HTTP request handling"""

    def test_successful_request(self, client, httpx_mock: HTTPXMock):
        """Test successful HTTP request"""
        httpx_mock.add_response(
            url="https://api.bluma.app/api/v1/templates",
            json={"templates": []},
            status_code=200,
        )

        response = client._request("GET", "/templates")
        assert response == {"templates": []}

    def test_request_includes_auth_header(self, client, httpx_mock: HTTPXMock):
        """Test requests include authorization header"""
        httpx_mock.add_response(json={"templates": []})

        client._request("GET", "/templates")

        request = httpx_mock.get_request()
        assert "Authorization" in request.headers
        assert request.headers["Authorization"] == f"Bearer {client.api_key}"

    def test_request_includes_user_agent(self, client, httpx_mock: HTTPXMock):
        """Test requests include user agent"""
        httpx_mock.add_response(json={"templates": []})

        client._request("GET", "/templates")

        request = httpx_mock.get_request()
        assert "User-Agent" in request.headers
        assert "bluma-python" in request.headers["User-Agent"]


class TestRetryLogic:
    """Test automatic retry logic"""

    def test_retries_on_500_error(self, client, httpx_mock: HTTPXMock):
        """Test client retries on 500 server error"""
        # First two requests fail, third succeeds
        httpx_mock.add_response(status_code=500)
        httpx_mock.add_response(status_code=500)
        httpx_mock.add_response(json={"templates": []}, status_code=200)

        response = client._request("GET", "/templates")
        assert response == {"templates": []}
        assert len(httpx_mock.get_requests()) == 3

    def test_retries_on_429_rate_limit(self, client, httpx_mock: HTTPXMock):
        """Test client retries on 429 rate limit"""
        httpx_mock.add_response(
            status_code=429,
            headers={"Retry-After": "1"},
        )
        httpx_mock.add_response(json={"templates": []}, status_code=200)

        response = client._request("GET", "/templates")
        assert response == {"templates": []}
        assert len(httpx_mock.get_requests()) == 2

    def test_max_retries_exceeded(self, client, httpx_mock: HTTPXMock):
        """Test client stops after max retries"""
        # All requests fail - need exactly max_retries + 1 = 4 responses
        for _ in range(4):
            httpx_mock.add_response(status_code=500)

        with pytest.raises(Exception):
            client._request("GET", "/templates")

        # Should only make max_retries + 1 attempts (3 retries + 1 initial = 4 total)
        assert len(httpx_mock.get_requests()) == 4

    def test_no_retry_on_400_error(self, client, httpx_mock: HTTPXMock):
        """Test client does not retry on 400 errors"""
        httpx_mock.add_response(
            status_code=400,
            json={"error": {"type": "validation_error", "status": 400}},
        )

        with pytest.raises(Exception):
            client._request("GET", "/templates")

        # Should only make 1 attempt (no retries for 4xx except 429)
        assert len(httpx_mock.get_requests()) == 1


class TestErrorTransformation:
    """Test error transformation"""

    def test_transforms_401_to_authentication_error(self, client, httpx_mock: HTTPXMock):
        """Test 401 errors are transformed to AuthenticationError"""
        httpx_mock.add_response(
            status_code=401,
            json={"error": {"type": "authentication_error", "status": 401}},
        )

        with pytest.raises(AuthenticationError):
            client._request("GET", "/templates")

    def test_transforms_429_to_rate_limit_error(self, client, httpx_mock: HTTPXMock):
        """Test 429 errors are transformed to RateLimitError"""
        # Mock all retries to fail (need exactly max_retries + 1 = 4 responses)
        for _ in range(4):
            httpx_mock.add_response(
                status_code=429,
                headers={"Retry-After": "60"},
                json={"error": {"type": "rate_limit_error", "status": 429}},
            )

        with pytest.raises(RateLimitError) as exc_info:
            client._request("GET", "/templates")

        # retry_after is parsed as int, not string
        assert exc_info.value.retry_after == 60
