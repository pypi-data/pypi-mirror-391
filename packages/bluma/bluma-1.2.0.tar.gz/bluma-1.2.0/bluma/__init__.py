"""
bluma - Official Python SDK for the Bluma API

Example:
    >>> from bluma import Bluma
    >>>
    >>> bluma = Bluma(api_key="your_api_key")
    >>> video = bluma.videos.create(
    ...     template_id="meme-dialogue",
    ...     context={"prompt": "Create a funny dialogue"}
    ... )
    >>> print(video.id)
"""

__version__ = "1.2.0"

from .client import Bluma
from .errors import (
    APIError,
    AuthenticationError,
    BlumaError,
    ForbiddenError,
    InsufficientCreditsError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .types import (
    ApiKey,
    Asset,
    AssetUploadResponse,
    Collection,
    CreditBalance,
    CreditHistory,
    Template,
    TemplateVariant,
    Transaction,
    TransactionType,
    UsageByKey,
    UsageMetrics,
    Video,
    VideoDownload,
    VideoStatus,
    Webhook,
    WebhookDelivery,
)
from .webhooks import verify_webhook, verify_webhook_signature

__all__ = [
    # Client
    "Bluma",
    # Errors
    "BlumaError",
    "APIError",
    "ValidationError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    # Types
    "Video",
    "VideoStatus",
    "VideoDownload",
    "Template",
    "CreditBalance",
    "CreditHistory",
    "Transaction",
    "TransactionType",
    "Webhook",
    "WebhookDelivery",
    "ApiKey",
    "UsageMetrics",
    "UsageByKey",
    "TemplateVariant",
    "Collection",
    "Asset",
    "AssetUploadResponse",
    # Webhooks
    "verify_webhook",
    "verify_webhook_signature",
]
