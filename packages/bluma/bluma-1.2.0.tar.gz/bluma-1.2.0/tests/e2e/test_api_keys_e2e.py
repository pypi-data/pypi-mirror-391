"""
End-to-End Tests for API Keys Management

NOTE: API Keys endpoint uses Clerk authentication (NOT API key auth).
These tests require a Clerk user token.

Run: pytest tests/e2e/test_api_keys_e2e.py -v
Skip if no Clerk token: pytest tests/e2e/ -v --ignore=tests/e2e/test_api_keys_e2e.py
"""
import os
import pytest
from bluma import Bluma


@pytest.mark.e2e
@pytest.mark.skipif(
    not os.getenv("CLERK_USER_TOKEN"),
    reason="CLERK_USER_TOKEN not set (API Keys endpoint requires Clerk auth)"
)
class TestAPIKeysE2E:
    """End-to-end tests for API Keys Management"""

    @pytest.fixture
    def clerk_client(self):
        """
        Create a Bluma client with Clerk authentication.

        Note: API Keys endpoints use Clerk auth, not API key auth.
        This is different from other endpoints.
        """
        # This would require a different client setup with Clerk tokens
        # For now, skip these tests unless Clerk integration is added to SDK
        pytest.skip("API Keys endpoint requires Clerk authentication - not yet supported in SDK")

    def test_list_api_keys(self, clerk_client):
        """Test listing all API keys for the authenticated user"""
        keys = clerk_client.api_keys.list()

        assert isinstance(keys, list)
        print(f"   ✅ Found {len(keys)} API keys")

    def test_create_api_key(self, clerk_client):
        """Test creating a new API key"""
        api_key = clerk_client.api_keys.create(
            name="E2E Test Key",
            environment="test"
        )

        assert api_key.id is not None
        assert api_key.key is not None  # Only returned on creation
        assert api_key.name == "E2E Test Key"
        assert api_key.environment == "test"

        print(f"   ✅ API key created: {api_key.id}")

        # Clean up
        clerk_client.api_keys.delete(api_key.id)

    def test_rotate_api_key(self, clerk_client):
        """Test rotating an API key"""
        # Create key
        api_key = clerk_client.api_keys.create(
            name="Rotation Test",
            environment="test"
        )

        # Rotate
        rotated = clerk_client.api_keys.rotate(api_key.id)

        assert rotated.key != api_key.key  # New secret
        assert rotated.id == api_key.id  # Same ID

        print(f"   ✅ API key rotated: {rotated.id}")

        # Clean up
        clerk_client.api_keys.delete(api_key.id)

    def test_delete_api_key(self, clerk_client):
        """Test deleting an API key"""
        # Create key
        api_key = clerk_client.api_keys.create(
            name="Delete Test",
            environment="test"
        )

        # Delete
        clerk_client.api_keys.delete(api_key.id)

        # Verify deletion
        keys = clerk_client.api_keys.list()
        assert not any(k.id == api_key.id for k in keys)

        print(f"   ✅ API key deleted: {api_key.id}")

    def test_api_key_permissions(self, clerk_client):
        """Test that API keys have proper environment restrictions"""
        # Test keys should only work in test environment
        # Live keys should only work in production
        pytest.skip("Permission testing requires multi-environment setup")
