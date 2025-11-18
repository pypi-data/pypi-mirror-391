"""Tests for WebhooksResource"""
import pytest
from pytest_httpx import HTTPXMock
from bluma.types import Webhook, WebhookDelivery


class TestWebhooksCreate:
    """Test webhooks.create()"""

    def test_create_webhook_success(self, client, httpx_mock: HTTPXMock, mock_webhook_data):
        """Test successful webhook creation"""
        httpx_mock.add_response(json=mock_webhook_data, status_code=201)

        webhook = client.webhooks.create(
            url="https://myapp.com/webhooks/bluma", events=["video.completed", "video.failed"]
        )

        assert isinstance(webhook, Webhook)
        assert webhook.id == "webhook_abc123"
        assert webhook.url == "https://myapp.com/webhooks/bluma"
        assert webhook.events == ["video.completed", "video.failed"]
        assert webhook.is_active is True
        assert webhook.secret.startswith("whsec_")

    def test_create_webhook_single_event(self, client, httpx_mock: HTTPXMock, mock_webhook_data):
        """Test creating webhook with single event"""
        single_event_data = {**mock_webhook_data, "events": ["video.completed"]}
        httpx_mock.add_response(json=single_event_data, status_code=201)

        webhook = client.webhooks.create(url="https://myapp.com/webhook", events=["video.completed"])

        assert len(webhook.events) == 1
        assert webhook.events[0] == "video.completed"


class TestWebhooksList:
    """Test webhooks.list()"""

    def test_list_webhooks_success(self, client, httpx_mock: HTTPXMock, mock_webhook_data):
        """Test listing webhooks"""
        httpx_mock.add_response(
            json={
                "webhooks": [
                    mock_webhook_data,
                    {**mock_webhook_data, "id": "webhook_def456", "url": "https://example.com/hook"},
                ]
            }
        )

        webhooks = client.webhooks.list()

        assert len(webhooks) == 2
        assert all(isinstance(w, Webhook) for w in webhooks)
        assert webhooks[0].id == "webhook_abc123"
        assert webhooks[1].id == "webhook_def456"

    def test_list_webhooks_empty(self, client, httpx_mock: HTTPXMock):
        """Test listing webhooks when none exist"""
        httpx_mock.add_response(json={"webhooks": []})

        webhooks = client.webhooks.list()

        assert len(webhooks) == 0


class TestWebhooksDelete:
    """Test webhooks.delete()"""

    def test_delete_webhook_success(self, client, httpx_mock: HTTPXMock):
        """Test deleting a webhook"""
        httpx_mock.add_response(json={}, status_code=200)

        # Should not raise any exception
        client.webhooks.delete(webhook_id="webhook_abc123")

        request = httpx_mock.get_request()
        assert request.method == "DELETE"
        assert "/webhooks/webhook_abc123" in str(request.url)


class TestWebhooksDeliveries:
    """Test webhooks.get_deliveries()"""

    def test_get_webhook_deliveries_success(self, client, httpx_mock: HTTPXMock):
        """Test getting webhook delivery logs"""
        delivery_data = [
            {
                "id": "del_abc123",
                "event_id": "evt_abc123",
                "event_type": "video.completed",
                "attempt_number": 1,
                "status_code": 200,
                "duration_ms": 150,
                "created_at": "2024-01-15T10:00:00Z",
            },
            {
                "id": "del_def456",
                "event_id": "evt_def456",
                "event_type": "video.failed",
                "attempt_number": 3,
                "status_code": 500,
                "duration_ms": 250,
                "error_message": "Server error",
                "created_at": "2024-01-15T11:00:00Z",
            },
        ]
        httpx_mock.add_response(json={"deliveries": delivery_data})

        deliveries = client.webhooks.get_deliveries(webhook_id="webhook_abc123")

        assert len(deliveries) == 2
        assert all(isinstance(d, WebhookDelivery) for d in deliveries)
        assert deliveries[0].id == "del_abc123"
        assert deliveries[0].status_code == 200
        assert deliveries[0].attempt_number == 1
        assert deliveries[1].id == "del_def456"
        assert deliveries[1].attempt_number == 3
        assert deliveries[1].error_message == "Server error"

    def test_get_webhook_deliveries_empty(self, client, httpx_mock: HTTPXMock):
        """Test getting webhook deliveries when none exist"""
        httpx_mock.add_response(json={"deliveries": []})

        deliveries = client.webhooks.get_deliveries(webhook_id="webhook_abc123")

        assert len(deliveries) == 0
