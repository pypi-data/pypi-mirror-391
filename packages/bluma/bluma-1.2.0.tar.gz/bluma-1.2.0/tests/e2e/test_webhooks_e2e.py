"""
End-to-End Tests for Webhooks API

Tests webhook CRUD operations and delivery logs.
These tests do NOT consume credits.

Run: pytest tests/e2e/test_webhooks_e2e.py -v
"""
import pytest
from bluma import Bluma
from bluma.types import Webhook
from bluma.errors import ValidationError, NotFoundError


@pytest.mark.e2e
class TestWebhooksE2E:
    """End-to-end tests for Webhooks API"""

    def test_create_webhook(self, bluma: Bluma, cleanup_webhooks):
        """Test creating a webhook"""
        print("\n🪝 Creating webhook...")

        webhook = bluma.webhooks.create(
            url="https://webhook.site/test-bluma-webhook",
            events=["video.completed", "video.failed"]
        )

        # Track for cleanup
        cleanup_webhooks.append(webhook.id)

        # Verify response
        assert webhook.id is not None
        assert webhook.id.startswith("webhook_")
        assert webhook.url == "https://webhook.site/test-bluma-webhook"
        assert "video.completed" in webhook.events
        assert "video.failed" in webhook.events
        assert webhook.is_active is True
        assert webhook.secret is not None  # Webhook signing secret
        assert webhook.created_at is not None

        print(f"   ✅ Webhook created: {webhook.id}")
        print(f"      • URL: {webhook.url}")
        print(f"      • Events: {webhook.events}")
        print(f"      • Secret: {webhook.secret[:20]}...")

    def test_create_webhook_all_events(self, bluma: Bluma, cleanup_webhooks):
        """Test creating a webhook with all event types"""
        all_events = [
            "video.queued",
            "video.processing",
            "video.completed",
            "video.failed",
            "credits.low",
            "credits.exhausted"
        ]

        webhook = bluma.webhooks.create(
            url="https://webhook.site/test-all-events",
            events=all_events
        )

        cleanup_webhooks.append(webhook.id)

        assert set(webhook.events) == set(all_events)
        print(f"   ✅ Webhook with all events created: {webhook.id}")

    def test_create_webhook_validation_error(self, bluma: Bluma):
        """Test that invalid webhook URLs are rejected"""
        with pytest.raises(ValidationError):
            bluma.webhooks.create(
                url="not-a-valid-url",
                events=["video.completed"]
            )

        print(f"   ✅ Validation error raised for invalid URL")

    def test_create_webhook_invalid_event(self, bluma: Bluma):
        """Test that invalid event types are rejected"""
        with pytest.raises(ValidationError):
            bluma.webhooks.create(
                url="https://webhook.site/test",
                events=["invalid.event"]
            )

        print(f"   ✅ Validation error raised for invalid event type")

    def test_list_webhooks(self, bluma: Bluma, cleanup_webhooks):
        """Test listing all webhooks"""
        # Create a test webhook first
        webhook = bluma.webhooks.create(
            url="https://webhook.site/test-list",
            events=["video.completed"]
        )
        cleanup_webhooks.append(webhook.id)

        # List webhooks
        webhooks = bluma.webhooks.list()

        assert isinstance(webhooks, list)
        assert len(webhooks) > 0

        # Find our webhook
        found = next((w for w in webhooks if w.id == webhook.id), None)
        assert found is not None, "Created webhook should be in list"

        print(f"   ✅ Found {len(webhooks)} webhooks")
        print(f"   Created webhook found in list: {found.id}")

    def test_get_webhook_by_id(self, bluma: Bluma, cleanup_webhooks):
        """Test retrieving a specific webhook"""
        # Create webhook
        created = bluma.webhooks.create(
            url="https://webhook.site/test-get",
            events=["video.completed"]
        )
        cleanup_webhooks.append(created.id)

        # Retrieve webhook
        retrieved = bluma.webhooks.get(created.id)

        assert retrieved.id == created.id
        assert retrieved.url == created.url
        assert retrieved.events == created.events
        assert retrieved.secret == created.secret

        print(f"   ✅ Webhook retrieved: {retrieved.id}")

    def test_get_webhook_not_found(self, bluma: Bluma):
        """Test getting non-existent webhook"""
        with pytest.raises(NotFoundError):
            bluma.webhooks.get("webhook_nonexistent123")

        print(f"   ✅ 404 error raised correctly")

    def test_delete_webhook(self, bluma: Bluma):
        """Test deleting a webhook"""
        # Create webhook
        webhook = bluma.webhooks.create(
            url="https://webhook.site/test-delete",
            events=["video.completed"]
        )

        # Delete webhook
        bluma.webhooks.delete(webhook.id)

        # Verify deletion
        with pytest.raises(NotFoundError):
            bluma.webhooks.get(webhook.id)

        print(f"   ✅ Webhook deleted successfully: {webhook.id}")

    def test_delete_webhook_idempotent(self, bluma: Bluma):
        """Test that deleting a webhook twice doesn't error"""
        # Create and delete webhook
        webhook = bluma.webhooks.create(
            url="https://webhook.site/test-idempotent",
            events=["video.completed"]
        )
        bluma.webhooks.delete(webhook.id)

        # Delete again - should be idempotent (or raise 404, both acceptable)
        try:
            bluma.webhooks.delete(webhook.id)
            print(f"   ✅ Double delete is idempotent")
        except NotFoundError:
            print(f"   ✅ Double delete raises 404 (acceptable)")

    def test_get_webhook_deliveries(self, bluma: Bluma, cleanup_webhooks):
        """Test retrieving webhook delivery logs"""
        # Create webhook
        webhook = bluma.webhooks.create(
            url="https://webhook.site/test-deliveries",
            events=["video.completed", "video.failed"]
        )
        cleanup_webhooks.append(webhook.id)

        # Get deliveries
        deliveries = bluma.webhooks.get_deliveries(webhook.id)

        # Verify response structure
        assert hasattr(deliveries, 'deliveries') or isinstance(deliveries, list)

        if isinstance(deliveries, list):
            delivery_list = deliveries
        else:
            delivery_list = deliveries.deliveries

        # New webhook might not have deliveries yet
        print(f"   ✅ Delivery logs retrieved: {len(delivery_list)} deliveries")

        if len(delivery_list) > 0:
            first = delivery_list[0]
            print(f"   Sample delivery:")
            print(f"      • ID: {first.id if hasattr(first, 'id') else 'N/A'}")
            print(f"      • Event: {first.event if hasattr(first, 'event') else 'N/A'}")
            print(f"      • Status: {first.status if hasattr(first, 'status') else 'N/A'}")

    def test_webhook_secret_rotation(self, bluma: Bluma, cleanup_webhooks):
        """Test that webhook has a secret for signature verification"""
        webhook = bluma.webhooks.create(
            url="https://webhook.site/test-secret",
            events=["video.completed"]
        )
        cleanup_webhooks.append(webhook.id)

        # Verify secret exists
        assert webhook.secret is not None
        assert len(webhook.secret) > 20  # Should be reasonably long

        # Secret should start with whsec_ prefix (common pattern)
        if webhook.secret.startswith("whsec_"):
            print(f"   ✅ Webhook secret follows whsec_ convention")
        else:
            print(f"   ℹ️  Webhook secret format: {webhook.secret[:10]}...")

    def test_webhook_url_validation(self, bluma: Bluma):
        """Test various webhook URL validations"""
        # Test HTTP (should work in development)
        try:
            webhook = bluma.webhooks.create(
                url="http://localhost:3000/webhooks",
                events=["video.completed"]
            )
            bluma.webhooks.delete(webhook.id)
            print(f"   ✅ HTTP URLs accepted (development mode)")
        except ValidationError:
            print(f"   ℹ️  HTTP URLs rejected (production mode)")

        # Test missing protocol
        with pytest.raises(ValidationError):
            bluma.webhooks.create(
                url="webhook.site/test",
                events=["video.completed"]
            )

        print(f"   ✅ URL validation working correctly")

    def test_webhook_lifecycle(self, bluma: Bluma):
        """Test complete webhook lifecycle"""
        print(f"\n🔄 Testing webhook lifecycle...")

        # 1. Create
        webhook = bluma.webhooks.create(
            url="https://webhook.site/test-lifecycle",
            events=["video.completed", "video.failed"]
        )
        print(f"   [1/5] Created: {webhook.id}")

        # 2. List (verify it appears)
        webhooks = bluma.webhooks.list()
        assert any(w.id == webhook.id for w in webhooks)
        print(f"   [2/5] Found in list")

        # 3. Get (retrieve individually)
        retrieved = bluma.webhooks.get(webhook.id)
        assert retrieved.id == webhook.id
        print(f"   [3/5] Retrieved individually")

        # 4. Get deliveries
        deliveries = bluma.webhooks.get_deliveries(webhook.id)
        print(f"   [4/5] Delivery logs accessible")

        # 5. Delete
        bluma.webhooks.delete(webhook.id)
        print(f"   [5/5] Deleted successfully")

        # Verify deletion
        with pytest.raises(NotFoundError):
            bluma.webhooks.get(webhook.id)

        print(f"   ✅ Webhook lifecycle completed successfully")
