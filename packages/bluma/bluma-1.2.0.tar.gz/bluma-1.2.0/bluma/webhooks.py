"""Webhook verification utilities"""

import hashlib
import hmac
import json
from typing import Any, Dict, Union


def verify_webhook_signature(payload: Union[str, bytes], signature: str, secret: str) -> bool:
    """
    Verify webhook signature using HMAC-SHA256

    Args:
        payload: Webhook payload (string or bytes)
        signature: Signature from X-Bluma-Signature header
        secret: Webhook secret

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Convert payload to bytes if needed
        if isinstance(payload, str):
            payload_bytes = payload.encode("utf-8")
        else:
            payload_bytes = payload

        # Compute expected signature
        expected_signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

        expected_format = f"sha256={expected_signature}"

        # Constant-time comparison
        return hmac.compare_digest(signature, expected_format)
    except Exception:
        return False


def verify_webhook(payload: Union[str, bytes], signature: str, secret: str) -> Dict[str, Any]:
    """
    Verify and parse webhook event

    Args:
        payload: Webhook payload (string or bytes)
        signature: Signature from X-Bluma-Signature header
        secret: Webhook secret

    Returns:
        Parsed webhook event

    Raises:
        ValueError: If signature is invalid
    """
    if not verify_webhook_signature(payload, signature, secret):
        raise ValueError("Invalid webhook signature")

    # Parse payload
    payload_str = payload if isinstance(payload, str) else payload.decode("utf-8")
    return json.loads(payload_str)
