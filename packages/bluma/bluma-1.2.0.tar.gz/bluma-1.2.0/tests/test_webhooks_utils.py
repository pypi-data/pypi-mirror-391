"""Tests for webhook signature verification"""
import pytest
from bluma.webhooks import verify_webhook_signature, verify_webhook
import hmac
import hashlib

# TODO: Add comprehensive webhook verification tests
def test_verify_webhook_signature_valid():
    """Test valid webhook signature"""
    secret = "test_secret"
    payload = b'{"event": "test"}'
    # Signature should be in format "sha256=<hash>"
    hash_value = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    signature = f"sha256={hash_value}"

    assert verify_webhook_signature(payload, signature, secret) is True

def test_verify_webhook_signature_invalid():
    """Test invalid webhook signature"""
    assert verify_webhook_signature(b'test', 'invalid', 'secret') is False

def test_verify_webhook_parses_json():
    """Test verify_webhook parses JSON payload"""
    secret = "test_secret"
    payload = b'{"event": "test", "data": {"id": "123"}}'
    hash_value = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    signature = f"sha256={hash_value}"

    event = verify_webhook(payload, signature, secret)
    assert event["event"] == "test"
    assert event["data"]["id"] == "123"

def test_verify_webhook_raises_on_invalid_signature():
    """Test verify_webhook raises ValueError on invalid signature"""
    with pytest.raises(ValueError, match="Invalid webhook signature"):
        verify_webhook(b'{"test": true}', 'invalid', 'secret')
