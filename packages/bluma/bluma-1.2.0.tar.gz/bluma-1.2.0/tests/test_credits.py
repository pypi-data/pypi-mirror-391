"""Tests for CreditsResource"""
import pytest
from pytest_httpx import HTTPXMock
from bluma.types import CreditBalance, CreditHistory, Transaction


class TestCreditsGetBalance:
    """Test credits.get_balance()"""

    def test_get_balance_success(self, client, httpx_mock: HTTPXMock, mock_credit_balance_data):
        """Test getting credit balance"""
        httpx_mock.add_response(json=mock_credit_balance_data)

        balance = client.credits.get_balance()

        assert isinstance(balance, CreditBalance)
        assert balance.credits == 88
        assert balance.tier == "pro"
        assert balance.monthly_allowance == 500
        assert balance.overage_used == 12

    def test_get_balance_with_usage_details(self, client, httpx_mock: HTTPXMock, mock_credit_balance_data):
        """Test getting balance with usage statistics"""
        httpx_mock.add_response(json=mock_credit_balance_data)

        balance = client.credits.get_balance()

        assert balance.usage is not None
        assert balance.usage.total_spent == 412
        assert balance.usage.average_per_video == 6.5

    def test_get_balance_verifies_tier_allowance(self, client, httpx_mock: HTTPXMock, mock_credit_balance_data):
        """Test that tier and allowance are properly returned"""
        httpx_mock.add_response(json=mock_credit_balance_data)

        balance = client.credits.get_balance()

        assert balance.tier in ["free", "basic", "pro", "enterprise"]
        assert balance.monthly_allowance > 0
        assert balance.overage_used >= 0


class TestCreditsGetHistory:
    """Test credits.get_history()"""

    def test_get_history_success(self, client, httpx_mock: HTTPXMock, mock_transaction_data):
        """Test getting credit transaction history"""
        history_data = {
            "transactions": [
                mock_transaction_data,
                {**mock_transaction_data, "id": "txn_def456", "amount": -3, "balance_after": 80},
            ],
            "total": 2,
        }
        httpx_mock.add_response(json=history_data)

        history = client.credits.get_history()

        assert isinstance(history, CreditHistory)
        assert len(history.transactions) == 2
        assert all(isinstance(t, Transaction) for t in history.transactions)
        assert history.total == 2
        assert history.transactions[0].id == "txn_abc123"
        assert history.transactions[1].id == "txn_def456"

    def test_get_history_with_pagination(self, client, httpx_mock: HTTPXMock):
        """Test getting credit history with pagination parameters"""
        history_data = {"transactions": [], "total": 0}
        httpx_mock.add_response(json=history_data)

        client.credits.get_history(limit=20, offset=40)

        request = httpx_mock.get_request()
        assert "limit=20" in str(request.url)
        assert "offset=40" in str(request.url)

    def test_get_history_empty(self, client, httpx_mock: HTTPXMock):
        """Test getting credit history when no transactions exist"""
        history_data = {"transactions": [], "total": 0}
        httpx_mock.add_response(json=history_data)

        history = client.credits.get_history()

        assert len(history.transactions) == 0
        assert history.total == 0

    def test_get_history_transaction_types(self, client, httpx_mock: HTTPXMock):
        """Test different transaction types in history"""
        history_data = {
            "transactions": [
                {
                    "id": "txn_purchase",
                    "type": "purchase",
                    "amount": 100,
                    "balance_after": 200,
                    "description": "Credit purchase",
                    "created_at": "2024-01-15T10:00:00Z",
                },
                {
                    "id": "txn_deduction",
                    "type": "deduction",
                    "amount": -5,
                    "balance_after": 195,
                    "description": "Video generation",
                    "created_at": "2024-01-15T11:00:00Z",
                },
                {
                    "id": "txn_refund",
                    "type": "refund",
                    "amount": 5,
                    "balance_after": 200,
                    "description": "Failed video refund",
                    "created_at": "2024-01-15T12:00:00Z",
                },
            ],
            "total": 3,
        }
        httpx_mock.add_response(json=history_data)

        history = client.credits.get_history()

        assert history.transactions[0].type.value == "purchase"
        assert history.transactions[0].amount == 100
        assert history.transactions[1].type.value == "deduction"
        assert history.transactions[1].amount == -5
        assert history.transactions[2].type.value == "refund"
        assert history.transactions[2].amount == 5

    def test_get_history_verifies_balance_tracking(self, client, httpx_mock: HTTPXMock, mock_transaction_data):
        """Test that balance_after field is properly tracked"""
        history_data = {"transactions": [mock_transaction_data], "total": 1}
        httpx_mock.add_response(json=history_data)

        history = client.credits.get_history()

        transaction = history.transactions[0]
        assert transaction.balance_after == 83
        assert transaction.description == "Video generation: batch_xyz789"
        assert transaction.metadata == {"video_id": "batch_xyz789"}
