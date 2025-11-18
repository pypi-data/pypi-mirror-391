"""Tests for UsageResource"""
import pytest
from pytest_httpx import HTTPXMock
from bluma.types import UsageMetrics, TimeSeriesPoint, TopEndpoint


class TestUsageGetMetrics:
    """Test usage.get_metrics()"""

    def test_get_usage_metrics_success(self, client, httpx_mock: HTTPXMock, mock_usage_metrics_data):
        """Test getting usage metrics"""
        httpx_mock.add_response(json=mock_usage_metrics_data)

        metrics = client.usage.get_metrics()

        assert isinstance(metrics, UsageMetrics)
        assert metrics.total_requests == 1000
        assert metrics.successful_requests == 950
        assert metrics.failed_requests == 50
        assert metrics.average_latency == 250.5
        assert metrics.credits_consumed == 500

    def test_get_usage_metrics_with_date_range(self, client, httpx_mock: HTTPXMock, mock_usage_metrics_data):
        """Test getting usage metrics with date range"""
        httpx_mock.add_response(json=mock_usage_metrics_data)

        client.usage.get_metrics(start_date="2024-01-01", end_date="2024-01-31")

        request = httpx_mock.get_request()
        assert "startDate=2024-01-01" in str(request.url)
        assert "endDate=2024-01-31" in str(request.url)

    def test_get_usage_metrics_with_period(self, client, httpx_mock: HTTPXMock, mock_usage_metrics_data):
        """Test getting usage metrics with period parameter"""
        httpx_mock.add_response(json=mock_usage_metrics_data)

        client.usage.get_metrics(period="7d")

        request = httpx_mock.get_request()
        assert "period=7d" in str(request.url)


class TestUsageGetTimeseries:
    """Test usage.get_timeseries()"""

    def test_get_timeseries_success(self, client, httpx_mock: HTTPXMock):
        """Test getting timeseries data"""
        timeseries_data = {
            "timeseries": [
                {"timestamp": "2024-01-15T00:00:00Z", "requests": 100, "latency": 200.5, "success_rate": 0.95},
                {"timestamp": "2024-01-15T01:00:00Z", "requests": 150, "latency": 220.3, "success_rate": 0.96},
                {"timestamp": "2024-01-15T02:00:00Z", "requests": 120, "latency": 195.8, "success_rate": 0.94},
            ]
        }
        httpx_mock.add_response(json=timeseries_data)

        timeseries = client.usage.get_timeseries()

        assert len(timeseries) == 3
        assert all(isinstance(point, TimeSeriesPoint) for point in timeseries)
        assert timeseries[0].requests == 100
        assert timeseries[0].latency == 200.5
        assert timeseries[0].success_rate == 0.95
        assert timeseries[1].requests == 150
        assert timeseries[2].requests == 120

    def test_get_timeseries_with_date_range(self, client, httpx_mock: HTTPXMock):
        """Test getting timeseries with date range"""
        httpx_mock.add_response(json={"timeseries": []})

        client.usage.get_timeseries(start_date="2024-01-01", end_date="2024-01-31")

        request = httpx_mock.get_request()
        assert "startDate=2024-01-01" in str(request.url)
        assert "endDate=2024-01-31" in str(request.url)

    def test_get_timeseries_with_granularity(self, client, httpx_mock: HTTPXMock):
        """Test getting timeseries with custom granularity"""
        httpx_mock.add_response(json={"timeseries": []})

        client.usage.get_timeseries(granularity="day")

        request = httpx_mock.get_request()
        assert "granularity=day" in str(request.url)


class TestUsageGetTopEndpoints:
    """Test usage.get_top_endpoints()"""

    def test_get_top_endpoints_success(self, client, httpx_mock: HTTPXMock):
        """Test getting top endpoints by volume"""
        endpoints_data = {
            "endpoints": [
                {"endpoint": "/videos", "method": "POST", "requests": 500, "average_latency": 1200.5, "error_rate": 0.02},
                {"endpoint": "/videos/{id}", "method": "GET", "requests": 300, "average_latency": 150.2, "error_rate": 0.01},
                {
                    "endpoint": "/templates",
                    "method": "GET",
                    "requests": 200,
                    "average_latency": 100.8,
                    "error_rate": 0.005,
                },
            ]
        }
        httpx_mock.add_response(json=endpoints_data)

        endpoints = client.usage.get_top_endpoints()

        assert len(endpoints) == 3
        assert all(isinstance(endpoint, TopEndpoint) for endpoint in endpoints)
        assert endpoints[0].endpoint == "/videos"
        assert endpoints[0].requests == 500
        assert endpoints[0].average_latency == 1200.5
        assert endpoints[1].endpoint == "/videos/{id}"
        assert endpoints[2].endpoint == "/templates"

    def test_get_top_endpoints_with_limit(self, client, httpx_mock: HTTPXMock):
        """Test getting top endpoints with custom limit"""
        httpx_mock.add_response(json={"endpoints": []})

        client.usage.get_top_endpoints(limit=5)

        request = httpx_mock.get_request()
        assert "limit=5" in str(request.url)

    def test_get_top_endpoints_with_date_range(self, client, httpx_mock: HTTPXMock):
        """Test getting top endpoints with date range"""
        httpx_mock.add_response(json={"endpoints": []})

        client.usage.get_top_endpoints(start_date="2024-01-01", end_date="2024-01-31", limit=20)

        request = httpx_mock.get_request()
        assert "startDate=2024-01-01" in str(request.url)
        assert "endDate=2024-01-31" in str(request.url)
        assert "limit=20" in str(request.url)
