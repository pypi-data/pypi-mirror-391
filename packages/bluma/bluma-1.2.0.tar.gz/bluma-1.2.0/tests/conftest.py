"""
Shared fixtures and configuration for pytest
"""
from datetime import datetime, timedelta
from typing import Dict, Any
import pytest
from bluma import Bluma


@pytest.fixture
def api_key():
    """Test API key"""
    return "test_key_12345"


@pytest.fixture
def base_url():
    """Test base URL"""
    return "https://api.bluma.app/api/v1"


@pytest.fixture
def client(api_key, base_url):
    """Create a test Bluma client"""
    return Bluma(api_key=api_key, base_url=base_url)


# Mock response data fixtures

@pytest.fixture
def mock_video_data() -> Dict[str, Any]:
    """Mock video response data"""
    return {
        "id": "batch_abc123",
        "status": "completed",
        "template_id": "meme-dialogue",
        "url": "https://cdn.getbluma.com/videos/test.mp4",
        "thumbnail_url": "https://cdn.getbluma.com/thumbnails/test.jpg",
        "duration": 45,
        "size_bytes": 1024000,
        "credits_charged": 5,
        "created_at": "2024-01-15T10:00:00Z",
        "completed_at": "2024-01-15T10:02:00Z",
        "error": None,
    }


@pytest.fixture
def mock_template_data() -> Dict[str, Any]:
    """Mock template response data"""
    return {
        "id": "meme-dialogue",
        "name": "Meme Dialogue",
        "description": "Create funny dialogue videos",
        "base_cost": 5,
        "category": "entertainment",
        "duration": 60,
        "aspect_ratio": "9:16",
        "context_schema": {"type": "object", "properties": {"prompt": {"type": "string"}}},
        "example_url": "https://cdn.getbluma.com/examples/meme.mp4",
    }


@pytest.fixture
def mock_credit_balance_data() -> Dict[str, Any]:
    """Mock credit balance response data"""
    return {
        "credits": 88,
        "tier": "pro",
        "monthly_allowance": 500,
        "overage_used": 12,
        "reset_date": (datetime.now() + timedelta(days=15)).isoformat(),
        "usage": {
            "total_spent": 412,
            "average_per_video": 6.5,
        },
    }


@pytest.fixture
def mock_transaction_data() -> Dict[str, Any]:
    """Mock transaction response data"""
    return {
        "id": "txn_abc123",
        "type": "deduction",
        "amount": -5,
        "balance_after": 83,
        "description": "Video generation: batch_xyz789",
        "metadata": {"video_id": "batch_xyz789"},
        "created_at": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def mock_api_key_data() -> Dict[str, Any]:
    """Mock API key response data"""
    return {
        "id": "key_abc123",
        "key": "sk_test_1234567890",  # Only on creation
        "name": "Production Key",
        "environment": "production",
        "last_used": "2024-01-15T10:00:00Z",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_webhook_data() -> Dict[str, Any]:
    """Mock webhook response data"""
    return {
        "id": "webhook_abc123",
        "url": "https://myapp.com/webhooks/bluma",
        "events": ["video.completed", "video.failed"],
        "secret": "whsec_1234567890",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_variant_data() -> Dict[str, Any]:
    """Mock variant response data"""
    return {
        "id": "var_abc123",
        "template_id": "meme-dialogue",
        "brand_id": "brand_xyz789",
        "name": "Funny Tone Preset",
        "payload": {
            "settings": {
                "systemPrompt": "Use a funny tone",
                "compositionProps": {
                    "voiceId": "female-casual",
                    "primaryColor": "#FF69B4",
                },
            }
        },
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_collection_data() -> Dict[str, Any]:
    """Mock collection response data"""
    return {
        "id": "coll_abc123",
        "brand_id": "brand_xyz789",
        "name": "Product Photos",
        "description": "High-quality product photography",
        "asset_count": 5,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_asset_data() -> Dict[str, Any]:
    """Mock asset response data"""
    return {
        "id": "asset_abc123",
        "brand_id": "brand_xyz789",
        "name": "product-photo.jpg",
        "original_filename": "photo.jpg",
        "file_type": "image/jpeg",
        "file_size_bytes": 102400,
        "s3_key": "assets/brand_xyz789/photo.jpg",
        "cdn_url": "https://cdn.getbluma.com/assets/photo.jpg",
        "thumbnail_url": "https://cdn.getbluma.com/assets/photo_thumb.jpg",
        "metadata": {"width": 1920, "height": 1080},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "deleted_at": None,
    }


@pytest.fixture
def mock_asset_upload_response_data() -> Dict[str, Any]:
    """Mock asset upload response data"""
    return {
        "asset_id": "asset_abc123",
        "upload_url": "https://s3.amazonaws.com/bluma-assets/upload?sig=xyz",
        "cdn_url": "https://cdn.getbluma.com/assets/photo.jpg",
        "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
    }


@pytest.fixture
def mock_usage_metrics_data() -> Dict[str, Any]:
    """Mock usage metrics response data"""
    return {
        "total_requests": 1000,
        "successful_requests": 950,
        "failed_requests": 50,
        "average_latency": 250.5,
        "credits_consumed": 500,
        "period": {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-31T23:59:59Z",
        },
    }


@pytest.fixture
def mock_error_response() -> Dict[str, Any]:
    """Mock error response"""
    return {
        "error": {
            "type": "validation_error",
            "status": 400,
            "detail": "Invalid request parameters",
        }
    }


@pytest.fixture
def mock_insufficient_credits_error() -> Dict[str, Any]:
    """Mock insufficient credits error response"""
    return {
        "error": {
            "type": "insufficient_credits",
            "status": 402,
            "detail": "You have 2 credits, but 5 are required.",
            "metadata": {
                "credits_required": 5,
                "credits_available": 2,
                "credits_reset_at": (datetime.now() + timedelta(days=10)).isoformat(),
            },
            "links": {
                "upgrade": "https://bluma.app/billing",
            },
        }
    }
