"""
End-to-End Tests for Usage Analytics API

Tests usage metrics and analytics endpoints.
These tests do NOT consume credits.

Run: pytest tests/e2e/test_usage_e2e.py -v
"""
import pytest
from datetime import datetime, timedelta
from bluma import Bluma


@pytest.mark.e2e
class TestUsageE2E:
    """End-to-end tests for Usage Analytics API"""

    def test_get_usage_metrics(self, bluma: Bluma):
        """Test getting overall usage metrics"""
        print("\n📊 Getting usage metrics...")

        metrics = bluma.usage.get_metrics()

        # Verify response structure
        assert metrics is not None
        assert hasattr(metrics, 'total_requests') or hasattr(metrics, 'period')

        print(f"   ✅ Usage metrics retrieved successfully")

        if hasattr(metrics, 'total_requests'):
            print(f"      • Total requests: {metrics.total_requests}")

        if hasattr(metrics, 'successful_requests'):
            print(f"      • Successful: {metrics.successful_requests}")

        if hasattr(metrics, 'failed_requests'):
            print(f"      • Failed: {metrics.failed_requests}")

    def test_get_usage_metrics_with_date_range(self, bluma: Bluma):
        """Test getting usage metrics with custom date range"""
        # Last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        metrics = bluma.usage.get_metrics(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )

        assert metrics is not None
        print(f"   ✅ Metrics retrieved for date range")

    def test_get_usage_timeseries(self, bluma: Bluma):
        """Test getting time series data"""
        print("\n📈 Getting time series data...")

        try:
            timeseries = bluma.usage.get_timeseries(
                period="day",
                granularity="hour"
            )

            assert timeseries is not None
            print(f"   ✅ Time series data retrieved")
        except AttributeError:
            pytest.skip("timeseries endpoint not implemented in SDK")

    def test_get_top_endpoints(self, bluma: Bluma):
        """Test getting top endpoints by volume"""
        try:
            endpoints = bluma.usage.get_top_endpoints(limit=10)

            assert endpoints is not None
            print(f"   ✅ Top endpoints retrieved")
        except AttributeError:
            pytest.skip("top_endpoints not implemented in SDK")

    def test_get_recent_requests(self, bluma: Bluma):
        """Test getting recent API requests"""
        try:
            requests = bluma.usage.get_recent_requests(limit=20)

            assert requests is not None
            print(f"   ✅ Recent requests retrieved")
        except AttributeError:
            pytest.skip("recent_requests not implemented in SDK")

    def test_get_usage_by_api_key(self, bluma: Bluma):
        """Test getting usage breakdown by API key"""
        try:
            by_key = bluma.usage.get_usage_by_key()

            assert by_key is not None
            print(f"   ✅ Usage by API key retrieved")
        except AttributeError:
            pytest.skip("usage_by_key not implemented in SDK")

    def test_get_error_breakdown(self, bluma: Bluma):
        """Test getting error breakdown by status code"""
        try:
            errors = bluma.usage.get_error_breakdown()

            assert errors is not None
            print(f"   ✅ Error breakdown retrieved")
        except AttributeError:
            pytest.skip("error_breakdown not implemented in SDK")
