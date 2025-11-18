"""Type definitions for the Bluma SDK"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Enums
class VideoStatus(str, Enum):
    """Video status"""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TransactionType(str, Enum):
    """Transaction type"""

    DEDUCTION = "deduction"
    PURCHASE = "purchase"
    REFUND = "refund"


# Video models
class VideoError(BaseModel):
    """Video error details"""

    type: str
    detail: str


class Video(BaseModel):
    """Video object"""

    id: str
    status: VideoStatus
    template_id: str
    variant_id: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    size_bytes: Optional[int] = None
    credits_charged: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[VideoError] = None


class VideoDownload(BaseModel):
    """Video download information"""

    download_url: str
    expires_at: datetime


# Template models
class Template(BaseModel):
    """Template object"""

    id: str
    name: str
    description: str
    base_cost: int
    category: str
    duration: int
    aspect_ratio: str
    context_schema: Dict[str, Any]
    example_url: Optional[str] = None


# Credits models
class CreditUsage(BaseModel):
    """Credit usage statistics"""

    total_spent: int
    average_per_video: float


class CreditBalance(BaseModel):
    """Credit balance information"""

    credits: int
    tier: str
    monthly_allowance: int
    overage_used: int = 0
    reset_date: Optional[datetime] = None
    usage: Optional[CreditUsage] = None


class Transaction(BaseModel):
    """Credit transaction"""

    id: str
    type: TransactionType
    amount: int
    balance_after: int
    description: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class CreditHistory(BaseModel):
    """Credit history response"""

    transactions: List[Transaction]
    total: int


# Webhook models
class Webhook(BaseModel):
    """Webhook object"""

    id: str
    url: str
    events: List[str]
    secret: Optional[str] = None
    is_active: bool
    created_at: datetime


class WebhookDelivery(BaseModel):
    """Webhook delivery information"""

    id: str
    event_id: str
    event_type: str
    attempt_number: int
    status_code: int
    duration_ms: int
    error_message: Optional[str] = None
    next_retry_at: Optional[datetime] = None
    created_at: datetime


# Usage models
class UsagePeriod(BaseModel):
    """Usage period"""

    start: datetime
    end: datetime


class UsageMetrics(BaseModel):
    """Usage metrics"""

    total_requests: int
    successful_requests: int
    failed_requests: int
    average_latency: float
    credits_consumed: int
    period: UsagePeriod


class TimeSeriesPoint(BaseModel):
    """Time series data point"""

    timestamp: datetime
    requests: int
    latency: float
    success_rate: float


class TopEndpoint(BaseModel):
    """Top endpoint information"""

    endpoint: str
    method: str
    requests: int
    average_latency: float
    error_rate: float


class RecentRequest(BaseModel):
    """Recent API request"""

    id: str
    method: str
    endpoint: str
    status_code: int
    latency: int
    timestamp: datetime


class UsageByKey(BaseModel):
    """Usage by API key"""

    api_key_id: str
    api_key_name: str
    requests: int
    credits_consumed: int


class ErrorBreakdown(BaseModel):
    """Error breakdown"""

    status_code: int
    count: int
    percentage: float


# API Key models
class ApiKey(BaseModel):
    """API Key object"""

    id: str
    key: Optional[str] = None  # Only present on creation
    name: str
    environment: str
    last_used: Optional[datetime] = None
    created_at: datetime


# Template Variant models
class TemplateVariant(BaseModel):
    """Template variant preset"""

    id: str
    template_id: str
    brand_id: str
    name: str
    payload: Dict[str, Any]  # Contains settings dict
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Asset Collection models
class Collection(BaseModel):
    """Asset collection object"""

    id: str
    brand_id: str
    name: str
    description: Optional[str] = None
    asset_count: int = 0
    created_at: datetime
    updated_at: datetime


class Asset(BaseModel):
    """Asset object"""

    id: str
    brand_id: str
    name: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    s3_key: str
    cdn_url: str
    thumbnail_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class AssetUploadResponse(BaseModel):
    """Asset upload response"""

    asset_id: str
    upload_url: str
    cdn_url: str
    expires_at: datetime
