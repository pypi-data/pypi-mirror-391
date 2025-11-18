# bluma

Official Python SDK for the Bluma API

## Installation

```bash
pip install bluma
```

## Quick Start

```python
from bluma import Bluma

bluma = Bluma(api_key="your_api_key")

# Generate a video
video = bluma.videos.create(
    template_id="meme-dialogue",
    context={"prompt": "Create a funny dialogue between a programmer and their computer"}
)

print(f"Video ID: {video.id}")

# Wait for completion
completed = bluma.videos.wait_for(video.id)
print(f"Video ready: {completed.url}")
```

## Features

- ✅ **Type hints** for full IDE support
- ✅ **Automatic retries** with exponential backoff
- ✅ **Webhook verification** utilities
- ✅ **Polling helpers** for video completion
- ✅ **Custom exception classes** for each error type
- ✅ **Context manager** support
- ✅ **Pydantic models** for response validation

## Configuration

```python
from bluma import Bluma

bluma = Bluma(
    api_key="your_api_key",
    base_url="https://api.bluma.app/api/v1",  # optional
    timeout=30.0,  # seconds
    max_retries=3,
    retry_delay=1.0,  # seconds
    retry_multiplier=2.0  # exponential backoff
)
```

## API Reference

### Videos

```python
# Create video
video = bluma.videos.create(
    template_id="meme-dialogue",
    context={"prompt": "Create a funny video"},
    webhook_url="https://myapp.com/webhook",  # optional
    metadata={"user_id": "user_123"}  # optional
)

# Get video status
video = bluma.videos.get("batch_abc123")

# Wait for completion with progress
def on_progress(progress):
    print(f"Progress: {progress}%")

completed = bluma.videos.wait_for(
    "batch_abc123",
    poll_interval=5.0,
    timeout=600.0,
    on_progress=on_progress
)

# Download video
download = bluma.videos.download("batch_abc123")
print(download.download_url)
```

### Templates

```python
# List all templates
templates = bluma.templates.list()

# Get template details
template = bluma.templates.get("meme-dialogue")
```

### Credits

```python
# Get balance
balance = bluma.credits.get_balance()
print(f"{balance.credits} credits remaining")

# Get history
history = bluma.credits.get_history(limit=50)
for txn in history.transactions:
    print(f"{txn.description}: {txn.amount}")
```

### Template Variants (Configuration Presets)

Save and reuse template configurations:

```python
# Create a variant preset
variant = bluma.variants.create(
    template_id="meme-dialogue",
    name="Funny Tone Preset",
    settings={
        "systemPrompt": "Use a funny, lighthearted tone",
        "captionPrompt": "Create engaging captions with emojis",
        "compositionProps": {
            "voiceId": "female-casual",
            "primaryColor": "#FF69B4"
        }
    }
)

# List variant presets for a template
variants = bluma.variants.list("meme-dialogue")

# Get variant details
variant = bluma.variants.get("meme-dialogue", "variant_xyz789")

# Update variant preset
updated = bluma.variants.update(
    template_id="meme-dialogue",
    variant_id="variant_xyz789",
    settings={"systemPrompt": "Updated tone instructions"}
)

# Delete variant
bluma.variants.delete("meme-dialogue", "variant_xyz789")
```

### Asset Collections

Organize your brand assets into collections:

```python
# Create a collection
collection = bluma.collections.create(
    name="Product Photos",
    description="High-quality product photography"
)

# List all collections
collections = bluma.collections.list()

# Get collection details
collection = bluma.collections.get("collection_abc123")

# Rename collection
bluma.collections.rename("collection_abc123", "New Name")

# Add assets to collection
bluma.collections.add_assets(
    collection_id="collection_abc123",
    asset_ids=["asset_1", "asset_2"]
)

# Remove asset from collection
bluma.collections.remove_asset("collection_abc123", "asset_1")

# List assets in collection
assets = bluma.collections.list_assets("collection_abc123")

# Delete collection
bluma.collections.delete("collection_abc123")
```

### Assets

Upload and manage brand assets:

```python
import requests

# Upload an asset (returns presigned URL)
upload_response = bluma.assets.upload(
    file_name="product.jpg",
    file_type="image/jpeg",
    collection_ids=["collection_abc123"]  # optional
)

# Upload file to presigned URL
with open("product.jpg", "rb") as f:
    requests.put(upload_response.upload_url, data=f)

print(f"CDN URL: {upload_response.cdn_url}")

# Get asset details
asset = bluma.assets.get("asset_abc123")

# List assets with filters
assets = bluma.assets.list(
    file_type="image",  # optional filter
    collection_id="collection_abc123",  # optional filter
    include_deleted=False
)

# Get random asset from collection
random_asset = bluma.assets.get_random(
    file_type="image",
    collection_id="collection_abc123",
    used_asset_ids=["asset_1", "asset_2"]  # Exclude these
)

# Rename asset
bluma.assets.rename("asset_abc123", "New Asset Name")

# Soft delete asset
bluma.assets.delete("asset_abc123")

# Recover deleted asset
bluma.assets.recover("asset_abc123")
```

### Webhooks

```python
# Create webhook
webhook = bluma.webhooks.create(
    url="https://myapp.com/webhooks/bluma",
    events=["video.completed", "video.failed"]
)
print(f"Secret: {webhook.secret}")  # Save this!

# List webhooks
webhooks = bluma.webhooks.list()

# Delete webhook
bluma.webhooks.delete("webhook_abc123")

# Get deliveries
deliveries = bluma.webhooks.get_deliveries("webhook_abc123")
```

### Webhook Verification

```python
from bluma import verify_webhook
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhooks/bluma', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Bluma-Signature')
    payload = request.get_data()

    try:
        event = verify_webhook(payload, signature, 'your_webhook_secret')
        print(f"Event: {event['type']}")
        return '', 200
    except ValueError:
        return 'Unauthorized', 401
```

## Error Handling

```python
from bluma import (
    ValidationError,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    NotFoundError,
    APIError
)

try:
    video = bluma.videos.create(...)
except ValidationError as error:
    print(f"Invalid input: {error.detail}")
except InsufficientCreditsError:
    print("Out of credits!")
except RateLimitError as error:
    print(f"Rate limited. Retry after {error.retry_after}s")
except APIError as error:
    print(f"API error: {error.status} - {error.detail}")
```

## Context Manager

```python
with Bluma(api_key="your_api_key") as client:
    video = client.videos.create(
        template_id="meme-dialogue",
        context={"prompt": "Test"}
    )
    print(video.id)

# Client is automatically closed here
```

## Type Hints

Full type hint support for IDE autocompletion:

```python
from bluma import Bluma, Video, VideoStatus

bluma = Bluma(api_key="your_api_key")

video: Video = bluma.videos.get("batch_abc123")

if video.status == VideoStatus.COMPLETED:
    print(video.url)
```

## Development

### Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy bluma

# Format code
black bluma tests
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bluma --cov-report=html
```

## License

MIT

## Support

- **Documentation:** https://docs.bluma.app
- **GitHub:** https://github.com/bluma/bluma-python
- **Email:** sdk@bluma.app
