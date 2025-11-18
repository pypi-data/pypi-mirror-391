"""
Tests for VideosResource
"""
import pytest
from pytest_httpx import HTTPXMock
from bluma.types import Video, VideoStatus, VideoDownload
from bluma.errors import NotFoundError, InsufficientCreditsError


class TestVideosCreate:
    """Test videos.create()"""

    def test_create_video_success(self, client, httpx_mock: HTTPXMock, mock_video_data):
        """Test successful video creation"""
        httpx_mock.add_response(json=mock_video_data, status_code=202)

        video = client.videos.create(
            template_id="meme-dialogue",
            context={"prompt": "Create a funny video"},
        )

        assert isinstance(video, Video)
        assert video.id == "batch_abc123"
        assert video.status == VideoStatus.COMPLETED
        assert video.template_id == "meme-dialogue"

    def test_create_video_with_webhook(self, client, httpx_mock: HTTPXMock, mock_video_data):
        """Test video creation with webhook URL"""
        httpx_mock.add_response(json=mock_video_data)

        client.videos.create(
            template_id="meme-dialogue",
            context={"prompt": "Test"},
            webhook_url="https://myapp.com/webhook",
        )

        request = httpx_mock.get_request()
        body = request.read().decode()
        assert "webhook_url" in body

    def test_create_video_insufficient_credits(
        self, client, httpx_mock: HTTPXMock, mock_insufficient_credits_error
    ):
        """Test video creation with insufficient credits"""
        httpx_mock.add_response(json=mock_insufficient_credits_error, status_code=402)

        with pytest.raises(InsufficientCreditsError) as exc_info:
            client.videos.create(template_id="meme-dialogue", context={"prompt": "Test"})

        error = exc_info.value
        assert error.status == 402
        assert error.credits_required == 5
        assert error.credits_available == 2

    def test_create_video_with_variant_id(self, client, httpx_mock: HTTPXMock, mock_video_data):
        """Test video creation with variant_id instead of template_id"""
        response_data = {**mock_video_data, "variant_id": "var_abc123"}
        httpx_mock.add_response(json=response_data, status_code=202)

        video = client.videos.create(
            variant_id="var_abc123",
            context={"prompt": "Create a funny video"},
        )

        assert isinstance(video, Video)
        assert video.variant_id == "var_abc123"

        # Verify request body includes variant_id
        request = httpx_mock.get_request()
        body = request.read().decode()
        assert "variant_id" in body
        assert "template_id" not in body

    def test_create_video_with_options(self, client, httpx_mock: HTTPXMock, mock_video_data):
        """Test video creation with options (resolution, watermark)"""
        httpx_mock.add_response(json=mock_video_data, status_code=202)

        client.videos.create(
            template_id="meme-dialogue",
            context={"prompt": "Test"},
            options={"resolution": "4k", "watermark": True},
        )

        # Verify request body includes options
        request = httpx_mock.get_request()
        body = request.read().decode()
        assert "options" in body

    def test_create_video_requires_one_identifier(self, client):
        """Test that either template_id or variant_id must be provided"""
        with pytest.raises(ValueError, match="Either template_id or variant_id must be provided"):
            client.videos.create(context={"prompt": "Test"})

    def test_create_video_rejects_both_identifiers(self, client):
        """Test that both template_id and variant_id cannot be provided"""
        with pytest.raises(ValueError, match="Cannot provide both template_id and variant_id"):
            client.videos.create(
                template_id="meme-dialogue",
                variant_id="var_abc123",
                context={"prompt": "Test"},
            )


class TestVideosGet:
    """Test videos.get()"""

    def test_get_video_success(self, client, httpx_mock: HTTPXMock, mock_video_data):
        """Test getting video status"""
        httpx_mock.add_response(json=mock_video_data)

        video = client.videos.get("batch_abc123")

        assert isinstance(video, Video)
        assert video.id == "batch_abc123"
        assert video.url is not None

    def test_get_video_not_found(self, client, httpx_mock: HTTPXMock):
        """Test getting non-existent video"""
        httpx_mock.add_response(
            json={"error": {"type": "not_found", "status": 404}},
            status_code=404,
        )

        with pytest.raises(NotFoundError):
            client.videos.get("invalid_id")


class TestVideosDownload:
    """Test videos.download()"""

    def test_download_video_success(self, client, httpx_mock: HTTPXMock):
        """Test getting download URL"""
        from datetime import datetime, timedelta

        download_data = {
            "download_url": "https://s3.amazonaws.com/bluma-videos/video.mp4?sig=xyz",
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
        }
        httpx_mock.add_response(json=download_data)

        download = client.videos.download("batch_abc123")

        assert isinstance(download, VideoDownload)
        assert "s3.amazonaws.com" in download.download_url
        assert download.expires_at is not None


class TestVideosWaitFor:
    """Test videos.wait_for() polling logic"""

    def test_wait_for_completed_video(self, client, httpx_mock: HTTPXMock, mock_video_data):
        """Test waiting for video that completes"""
        # First call: processing
        processing_data = {**mock_video_data, "status": "processing"}
        httpx_mock.add_response(json=processing_data)

        # Second call: completed
        httpx_mock.add_response(json=mock_video_data)

        video = client.videos.wait_for("batch_abc123", poll_interval=0.1)

        assert video.status == VideoStatus.COMPLETED
        assert len(httpx_mock.get_requests()) == 2

    def test_wait_for_with_progress_callback(
        self, client, httpx_mock: HTTPXMock, mock_video_data
    ):
        """Test wait_for with progress callback"""
        progress_calls = []

        def on_progress(progress):
            progress_calls.append(progress)

        # Mock two processing responses then completed
        processing_data = {**mock_video_data, "status": "processing"}
        httpx_mock.add_response(json=processing_data)
        httpx_mock.add_response(json=processing_data)
        httpx_mock.add_response(json=mock_video_data)

        client.videos.wait_for(
            "batch_abc123",
            poll_interval=0.1,
            on_progress=on_progress,
        )

        assert len(progress_calls) > 0
        assert 100 in progress_calls  # Final progress should be 100

    def test_wait_for_timeout(self, client, httpx_mock: HTTPXMock, mock_video_data):
        """Test wait_for times out"""
        # Always return processing status
        # With 0.5s timeout and 0.1s poll interval, expect ~5 requests
        processing_data = {**mock_video_data, "status": "processing"}
        for _ in range(5):
            httpx_mock.add_response(json=processing_data)

        with pytest.raises(Exception, match="timed out"):
            client.videos.wait_for("batch_abc123", poll_interval=0.1, timeout=0.5)
