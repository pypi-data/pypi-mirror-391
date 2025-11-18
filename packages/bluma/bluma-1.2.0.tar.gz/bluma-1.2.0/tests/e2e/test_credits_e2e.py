"""
End-to-End Tests for Credits API

Tests credit balance and transaction history endpoints.
These tests do NOT consume credits (read-only operations).

Run: pytest tests/e2e/test_credits_e2e.py -v
"""
import pytest
from datetime import datetime
from bluma import Bluma
from bluma.types import CreditBalance, Transaction, TransactionType


@pytest.mark.e2e
class TestCreditsE2E:
    """End-to-end tests for Credits API"""

    def test_get_balance(self, bluma: Bluma):
        """Test retrieving credit balance"""
        print("\n💰 Getting credit balance...")

        balance = bluma.credits.get_balance()

        # Verify response structure
        assert balance.credits is not None
        assert balance.credits >= 0, "Credits should be non-negative"
        assert balance.tier is not None
        assert isinstance(balance.tier, str)

        print(f"   ✅ Balance retrieved successfully:")
        print(f"      • Credits: {balance.credits}")
        print(f"      • Tier: {balance.tier}")

        # Optional fields
        if hasattr(balance, 'monthly_allowance') and balance.monthly_allowance:
            print(f"      • Monthly allowance: {balance.monthly_allowance}")

        if hasattr(balance, 'overage_used') and balance.overage_used is not None:
            print(f"      • Overage used: {balance.overage_used}")

        if hasattr(balance, 'reset_date') and balance.reset_date:
            print(f"      • Reset date: {balance.reset_date}")

    def test_balance_has_usage_info(self, bluma: Bluma):
        """Test that balance response includes usage information"""
        balance = bluma.credits.get_balance()

        # Check for usage field (if implemented)
        if hasattr(balance, 'usage') and balance.usage:
            assert isinstance(balance.usage, dict)

            if 'total_spent' in balance.usage:
                assert balance.usage['total_spent'] >= 0

            if 'average_per_video' in balance.usage:
                assert balance.usage['average_per_video'] >= 0

            print(f"   ✅ Usage info present:")
            print(f"      • Total spent: {balance.usage.get('total_spent', 'N/A')}")
            print(f"      • Avg per video: {balance.usage.get('average_per_video', 'N/A')}")
        else:
            print(f"   ℹ️  No usage info in balance response (optional)")

    def test_get_transaction_history(self, bluma: Bluma):
        """Test retrieving transaction history"""
        print("\n📊 Getting transaction history...")

        history = bluma.credits.get_history()

        # Verify response structure
        assert hasattr(history, 'transactions')
        assert isinstance(history.transactions, list)

        if len(history.transactions) > 0:
            # Check first transaction structure
            first = history.transactions[0]
            assert first.id is not None
            assert first.type in [TransactionType.DEDUCTION, TransactionType.CREDIT, TransactionType.REFUND]
            assert first.amount is not None
            assert first.created_at is not None

            # Deductions should be negative
            if first.type == TransactionType.DEDUCTION:
                assert first.amount < 0, "Deductions should be negative"

            # Credits/refunds should be positive
            if first.type in [TransactionType.CREDIT, TransactionType.REFUND]:
                assert first.amount > 0, "Credits/refunds should be positive"

            print(f"   ✅ Found {len(history.transactions)} transactions")
            print(f"   Recent transactions:")
            for txn in history.transactions[:5]:
                print(f"      • {txn.id}: {txn.type} {txn.amount} credits ({txn.created_at})")
        else:
            print(f"   ℹ️  No transactions found (new account or test environment)")

    def test_get_transaction_history_with_limit(self, bluma: Bluma):
        """Test retrieving transaction history with limit parameter"""
        print("\n📊 Getting transaction history with limit=5...")

        history = bluma.credits.get_history(limit=5)

        assert isinstance(history.transactions, list)
        assert len(history.transactions) <= 5, "Should respect limit parameter"

        print(f"   ✅ Returned {len(history.transactions)} transactions (limit=5)")

    def test_transaction_types_are_valid(self, bluma: Bluma):
        """Test that all transaction types are valid enum values"""
        history = bluma.credits.get_history()

        valid_types = [TransactionType.DEDUCTION, TransactionType.CREDIT, TransactionType.REFUND]

        for txn in history.transactions:
            assert txn.type in valid_types, f"Invalid transaction type: {txn.type}"

        if history.transactions:
            type_counts = {}
            for txn in history.transactions:
                type_counts[txn.type] = type_counts.get(txn.type, 0) + 1

            print(f"   ✅ Transaction type breakdown:")
            for txn_type, count in type_counts.items():
                print(f"      • {txn_type}: {count}")

    def test_transaction_timestamps_are_valid(self, bluma: Bluma):
        """Test that transaction timestamps are valid and parseable"""
        history = bluma.credits.get_history()

        for txn in history.transactions:
            # Timestamp should be parseable
            try:
                if isinstance(txn.created_at, str):
                    parsed = datetime.fromisoformat(txn.created_at.replace("Z", "+00:00"))
                    assert parsed <= datetime.now(parsed.tzinfo), "Transaction date should not be in the future"
            except ValueError as e:
                pytest.fail(f"Invalid timestamp format for transaction {txn.id}: {txn.created_at}")

        if history.transactions:
            print(f"   ✅ All {len(history.transactions)} timestamps are valid ISO 8601 format")

    def test_transaction_metadata(self, bluma: Bluma):
        """Test that transactions include relevant metadata"""
        history = bluma.credits.get_history()

        transactions_with_metadata = [t for t in history.transactions if hasattr(t, 'metadata') and t.metadata]

        if transactions_with_metadata:
            first = transactions_with_metadata[0]

            print(f"   ✅ Transaction metadata example:")
            print(f"      • Transaction ID: {first.id}")
            print(f"      • Description: {first.description if hasattr(first, 'description') else 'N/A'}")
            print(f"      • Metadata: {first.metadata}")

            # Video-related transactions should have video_id
            if first.type == TransactionType.DEDUCTION and isinstance(first.metadata, dict):
                if 'video_id' in first.metadata:
                    print(f"      • Related video: {first.metadata['video_id']}")
        else:
            print(f"   ℹ️  No transactions with metadata found")

    def test_balance_after_field(self, bluma: Bluma):
        """Test that transactions include balance_after field"""
        history = bluma.credits.get_history()

        for txn in history.transactions:
            if hasattr(txn, 'balance_after') and txn.balance_after is not None:
                assert txn.balance_after >= 0, "Balance after should be non-negative"

        transactions_with_balance = [t for t in history.transactions if hasattr(t, 'balance_after') and t.balance_after is not None]

        if transactions_with_balance:
            print(f"   ✅ {len(transactions_with_balance)}/{len(history.transactions)} transactions have balance_after field")
        else:
            print(f"   ℹ️  No transactions with balance_after field (optional)")

    def test_history_pagination(self, bluma: Bluma):
        """Test transaction history pagination"""
        # Get first page with limit
        page1 = bluma.credits.get_history(limit=10)

        # Check for pagination fields
        if hasattr(page1, 'has_more') and page1.has_more:
            # If there's a next page, try to get it
            if hasattr(page1, 'next_cursor') and page1.next_cursor:
                # Note: SDK might not support cursor pagination yet
                print(f"   ℹ️  Pagination available but not yet tested (implement cursor support)")
            else:
                print(f"   ℹ️  has_more=True but no cursor provided")
        else:
            print(f"   ✅ All transactions fit in one page")

    def test_credit_balance_consistency(self, bluma: Bluma):
        """Test that credit balance is consistent with latest transaction"""
        balance = bluma.credits.get_balance()
        history = bluma.credits.get_history(limit=1)

        # If there are transactions and balance_after is present
        if history.transactions and hasattr(history.transactions[0], 'balance_after'):
            latest_txn = history.transactions[0]

            if latest_txn.balance_after is not None:
                # Current balance should match the balance_after of latest transaction
                # (with some tolerance for concurrent operations)
                assert abs(balance.credits - latest_txn.balance_after) <= 100, \
                    "Current balance should be close to latest transaction's balance_after"

                print(f"   ✅ Balance consistency check:")
                print(f"      • Current balance: {balance.credits}")
                print(f"      • Latest txn balance_after: {latest_txn.balance_after}")
                print(f"      • Difference: {abs(balance.credits - latest_txn.balance_after)}")
        else:
            print(f"   ℹ️  No transactions to verify balance consistency")
