"""
End-to-End Test Configuration

These tests run against a real Bluma API backend (local development server).
They test the full SDK → API → Database flow without mocks.

Prerequisites:
1. Backend server running: cd /Users/stephenni/web && pnpm dev:backend
2. Test API key created: Create at http://localhost:3001/brand/api-keys
3. Environment configured: Copy .env.test.example to .env.test and fill in values

Run tests:
    pytest tests/e2e/ -v                    # All E2E tests
    pytest tests/e2e/test_videos_e2e.py -v  # Specific endpoint
    pytest tests/e2e/ -v -k "not video"     # Skip credit-consuming tests
"""
import os
import sys
from pathlib import Path
from typing import Generator
import pytest
from dotenv import load_dotenv
from bluma import Bluma

# Load E2E test environment
env_file = Path(__file__).parent / ".env.test"
if not env_file.exists():
    print(f"\n❌ ERROR: {env_file} not found!")
    print("\nTo fix this:")
    print(f"1. Copy .env.test.example to .env.test")
    print("2. Fill in your BLUMA_API_KEY (create one at http://localhost:3001/brand/api-keys)")
    print("3. Ensure backend is running: cd /Users/stephenni/web && pnpm dev:backend")
    print("4. Run tests again: pytest tests/e2e/ -v\n")
    sys.exit(1)

load_dotenv(env_file)


# ============================================================================
# Configuration
# ============================================================================

@pytest.fixture(scope="session")
def api_key() -> str:
    """Get API key from environment"""
    key = os.getenv("BLUMA_API_KEY")
    if not key or key == "bluma_test_your_key_here":
        pytest.fail(
            "BLUMA_API_KEY not set in .env.test file. "
            "Create an API key at http://localhost:3001/brand/api-keys"
        )
    return key


@pytest.fixture(scope="session")
def base_url() -> str:
    """Get base URL from environment"""
    return os.getenv("BLUMA_BASE_URL", "http://localhost:5001/api/v1")


@pytest.fixture(scope="session")
def test_template_id() -> str:
    """Get test template ID from environment"""
    return os.getenv("TEST_TEMPLATE_ID", "meme-dialogue")


@pytest.fixture(scope="session")
def video_timeout() -> float:
    """Get video generation timeout from environment"""
    return float(os.getenv("TEST_VIDEO_TIMEOUT", "600"))


@pytest.fixture(scope="session")
def poll_interval() -> float:
    """Get polling interval from environment"""
    return float(os.getenv("TEST_POLL_INTERVAL", "5"))


@pytest.fixture(scope="session")
def skip_credit_tests() -> bool:
    """Whether to skip tests that consume credits"""
    return os.getenv("SKIP_CREDIT_CONSUMING_TESTS", "false").lower() == "true"


# ============================================================================
# Client Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def bluma_client(api_key: str, base_url: str) -> Generator[Bluma, None, None]:
    """
    Create a Bluma client for E2E tests.

    This client connects to the real API backend.
    Scope: session (reused across all tests for efficiency)
    """
    print(f"\n🔧 Initializing Bluma client...")
    print(f"   Base URL: {base_url}")
    print(f"   API Key: {api_key[:20]}...\n")

    client = Bluma(
        api_key=api_key,
        base_url=base_url,
        timeout=30.0,
        max_retries=3
    )

    # Verify connection by checking credit balance
    try:
        balance = client.credits.get_balance()
        print(f"✅ Connected to API successfully!")
        print(f"   Current balance: {balance.credits} credits")
        print(f"   Tier: {balance.tier}\n")
    except Exception as e:
        pytest.fail(
            f"Failed to connect to API at {base_url}. "
            f"Error: {e}\n\n"
            "Ensure the backend is running: cd /Users/stephenni/web && pnpm dev:backend"
        )

    yield client

    # Teardown: No cleanup needed (session-scoped)
    print("\n🧹 E2E tests completed\n")


@pytest.fixture
def bluma(bluma_client: Bluma) -> Bluma:
    """
    Function-scoped client fixture for individual tests.

    Use this in tests that don't need isolation.
    """
    return bluma_client


# ============================================================================
# Test Data Cleanup
# ============================================================================

@pytest.fixture
def cleanup_webhooks(bluma: Bluma):
    """Clean up webhooks created during tests"""
    created_webhook_ids = []

    yield created_webhook_ids

    # Cleanup
    for webhook_id in created_webhook_ids:
        try:
            bluma.webhooks.delete(webhook_id)
            print(f"   🧹 Cleaned up webhook: {webhook_id}")
        except Exception as e:
            print(f"   ⚠️  Failed to cleanup webhook {webhook_id}: {e}")


@pytest.fixture
def cleanup_collections(bluma: Bluma):
    """Clean up collections created during tests"""
    created_collection_ids = []

    yield created_collection_ids

    # Cleanup
    for collection_id in created_collection_ids:
        try:
            bluma.collections.delete(collection_id)
            print(f"   🧹 Cleaned up collection: {collection_id}")
        except Exception as e:
            print(f"   ⚠️  Failed to cleanup collection {collection_id}: {e}")


@pytest.fixture
def cleanup_assets(bluma: Bluma):
    """Clean up assets created during tests"""
    created_asset_ids = []

    yield created_asset_ids

    # Cleanup
    for asset_id in created_asset_ids:
        try:
            bluma.assets.delete(asset_id)
            print(f"   🧹 Cleaned up asset: {asset_id}")
        except Exception as e:
            print(f"   ⚠️  Failed to cleanup asset {asset_id}: {e}")


@pytest.fixture
def cleanup_variants(bluma: Bluma):
    """Clean up variants created during tests"""
    created_variants = []  # List of (template_id, variant_id) tuples

    yield created_variants

    # Cleanup
    for template_id, variant_id in created_variants:
        try:
            bluma.variants.delete(template_id, variant_id)
            print(f"   🧹 Cleaned up variant: {template_id}/{variant_id}")
        except Exception as e:
            print(f"   ⚠️  Failed to cleanup variant {template_id}/{variant_id}: {e}")


# ============================================================================
# Pytest Markers
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests that require a running backend"
    )
    config.addinivalue_line(
        "markers", "credits: Tests that consume credits (video generation)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (>30 seconds)"
    )


# ============================================================================
# Test Session Hooks
# ============================================================================

def pytest_sessionstart(session):
    """Print info at start of test session"""
    print("\n" + "=" * 80)
    print("🧪 Bluma Python SDK - End-to-End Test Suite")
    print("=" * 80)
    print("\n📋 Configuration:")
    print(f"   API Endpoint: {os.getenv('BLUMA_BASE_URL', 'http://localhost:5001/api/v1')}")
    print(f"   API Key: {os.getenv('BLUMA_API_KEY', 'NOT SET')[:20]}...")
    print(f"   Test Template: {os.getenv('TEST_TEMPLATE_ID', 'meme-dialogue')}")
    print(f"   Skip Credit Tests: {os.getenv('SKIP_CREDIT_CONSUMING_TESTS', 'false')}")
    print("\n" + "=" * 80 + "\n")


def pytest_sessionfinish(session, exitstatus):
    """Print summary at end of test session"""
    print("\n" + "=" * 80)
    print("📊 Test Session Summary")
    print("=" * 80)
    print(f"   Exit Status: {'✅ PASSED' if exitstatus == 0 else '❌ FAILED'}")
    print("=" * 80 + "\n")
