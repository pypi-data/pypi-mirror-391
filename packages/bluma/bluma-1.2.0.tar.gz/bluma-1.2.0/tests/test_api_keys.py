"""Tests for ApiKeysResource"""
import pytest
from pytest_httpx import HTTPXMock
from bluma.types import ApiKey


class TestApiKeysCreate:
    """Test api_keys.create()"""

    def test_create_api_key_success(self, client, httpx_mock: HTTPXMock, mock_api_key_data):
        """Test successful API key creation"""
        httpx_mock.add_response(json=mock_api_key_data, status_code=201)

        api_key = client.api_keys.create(name="Production Key", environment="production")

        assert isinstance(api_key, ApiKey)
        assert api_key.id == "key_abc123"
        assert api_key.name == "Production Key"
        assert api_key.environment == "production"
        assert api_key.key == "sk_test_1234567890"  # Only returned on creation

    def test_create_api_key_test_environment(self, client, httpx_mock: HTTPXMock, mock_api_key_data):
        """Test creating a test environment API key"""
        test_key_data = {**mock_api_key_data, "environment": "test", "key": "sk_test_9876543210"}
        httpx_mock.add_response(json=test_key_data, status_code=201)

        api_key = client.api_keys.create(name="Test Key", environment="test")

        assert api_key.environment == "test"
        assert api_key.key.startswith("sk_test_")


class TestApiKeysList:
    """Test api_keys.list()"""

    def test_list_api_keys_success(self, client, httpx_mock: HTTPXMock, mock_api_key_data):
        """Test listing API keys"""
        httpx_mock.add_response(
            json={"api_keys": [mock_api_key_data, {**mock_api_key_data, "id": "key_def456", "name": "Dev Key"}]}
        )

        api_keys = client.api_keys.list()

        assert len(api_keys) == 2
        assert all(isinstance(k, ApiKey) for k in api_keys)
        assert api_keys[0].id == "key_abc123"
        assert api_keys[1].id == "key_def456"

    def test_list_api_keys_empty(self, client, httpx_mock: HTTPXMock):
        """Test listing API keys when none exist"""
        httpx_mock.add_response(json={"api_keys": []})

        api_keys = client.api_keys.list()

        assert len(api_keys) == 0


class TestApiKeysDelete:
    """Test api_keys.delete()"""

    def test_delete_api_key_success(self, client, httpx_mock: HTTPXMock):
        """Test deleting an API key"""
        httpx_mock.add_response(json={}, status_code=200)

        # Should not raise any exception
        client.api_keys.delete(api_key_id="key_abc123")

        request = httpx_mock.get_request()
        assert request.method == "DELETE"
        assert "/api-keys/key_abc123" in str(request.url)


class TestApiKeysRotate:
    """Test api_keys.rotate()"""

    def test_rotate_api_key_success(self, client, httpx_mock: HTTPXMock, mock_api_key_data):
        """Test rotating an API key"""
        rotated_key_data = {**mock_api_key_data, "key": "sk_test_new_1234567890"}
        httpx_mock.add_response(json=rotated_key_data)

        api_key = client.api_keys.rotate(api_key_id="key_abc123")

        assert isinstance(api_key, ApiKey)
        assert api_key.key == "sk_test_new_1234567890"  # New key value after rotation
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert "/api-keys/key_abc123/rotate" in str(request.url)
