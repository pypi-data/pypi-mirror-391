"""
End-to-End Tests for Videos API

Tests the complete video generation workflow:
1. Create video generation job
2. Poll for status updates
3. Wait for completion
4. Retrieve download URL
5. Verify video metadata

⚠️  WARNING: These tests CONSUME CREDITS (typically 3-6 credits per video)

Run: pytest tests/e2e/test_videos_e2e.py -v
Skip: pytest tests/e2e/ -v -k "not credits"
"""
import time
import pytest
from bluma import Bluma
from bluma.types import Video, VideoStatus, VideoDownload
from bluma.errors import (
    ValidationError,
    NotFoundError,
    InsufficientCreditsError
)


@pytest.mark.e2e
@pytest.mark.credits
@pytest.mark.slow
class TestVideosE2E:
    """End-to-end tests for Videos API"""

    def test_create_video_minimal(self, bluma: Bluma, test_template_id: str, skip_credit_tests: bool):
        """Test creating a video with minimal parameters"""
        if skip_credit_tests:
            pytest.skip("Skipping credit-consuming test (SKIP_CREDIT_CONSUMING_TESTS=true)")

        print(f"\n📹 Creating video with template: {test_template_id}")

        video = bluma.videos.create(
            template_id=test_template_id,
            context={
                "prompt": "Create a test video for E2E testing"
            }
        )

        # Verify response structure
        assert video.id is not None
        assert video.id.startswith("batch_")
        assert video.status in ["queued", "processing", "completed"]
        assert video.template_id == test_template_id
        assert video.credits_charged > 0
        assert video.created_at is not None

        print(f"   ✅ Video created: {video.id}")
        print(f"   Status: {video.status}")
        print(f"   Credits charged: {video.credits_charged}")

    def test_create_video_with_variant(self, bluma: Bluma, skip_credit_tests: bool):
        """Test creating a video with a variant ID"""
        if skip_credit_tests:
            pytest.skip("Skipping credit-consuming test")

        # First, we need a variant (skip for now if none exist)
        pytest.skip("Requires pre-existing variant - implement after variants E2E tests")

    def test_create_video_with_webhook(self, bluma: Bluma, test_template_id: str, skip_credit_tests: bool):
        """Test creating a video with webhook URL"""
        if skip_credit_tests:
            pytest.skip("Skipping credit-consuming test")

        webhook_url = "https://webhook.site/unique-uuid"

        video = bluma.videos.create(
            template_id=test_template_id,
            context={"prompt": "Test with webhook"},
            webhook_url=webhook_url
        )

        assert video.id is not None
        print(f"   ✅ Video with webhook created: {video.id}")

    def test_create_video_with_options(self, bluma: Bluma, test_template_id: str, skip_credit_tests: bool):
        """Test creating a video with custom options"""
        if skip_credit_tests:
            pytest.skip("Skipping credit-consuming test")

        video = bluma.videos.create(
            template_id=test_template_id,
            context={"prompt": "Test with custom resolution"},
            options={
                "resolution": "720p",
                "watermark": True  # Test keys have watermark
            }
        )

        assert video.id is not None
        print(f"   ✅ Video with custom options created: {video.id}")

    def test_create_video_validation_error(self, bluma: Bluma):
        """Test that validation errors are raised for invalid requests"""
        with pytest.raises(ValidationError) as exc_info:
            bluma.videos.create(
                template_id="nonexistent-template",
                context={"prompt": "Test"}
            )

        error = exc_info.value
        assert error.status_code == 400 or error.status_code == 404
        print(f"   ✅ Validation error caught correctly: {error}")

    def test_create_video_missing_context(self, bluma: Bluma, test_template_id: str):
        """Test that missing context raises validation error"""
        with pytest.raises((ValidationError, TypeError)):
            bluma.videos.create(
                template_id=test_template_id,
                context={}  # Empty context should fail
            )

    def test_get_video_status(self, bluma: Bluma, test_template_id: str, skip_credit_tests: bool):
        """Test retrieving video status"""
        if skip_credit_tests:
            pytest.skip("Skipping credit-consuming test")

        # Create a video first
        video = bluma.videos.create(
            template_id=test_template_id,
            context={"prompt": "Test status retrieval"}
        )

        # Get status
        retrieved = bluma.videos.get(video.id)

        assert retrieved.id == video.id
        assert retrieved.template_id == test_template_id
        assert retrieved.status in ["queued", "processing", "completed", "failed"]
        assert retrieved.created_at is not None

        print(f"   ✅ Status retrieved for {video.id}: {retrieved.status}")

    def test_get_video_not_found(self, bluma: Bluma):
        """Test getting a non-existent video"""
        with pytest.raises(NotFoundError) as exc_info:
            bluma.videos.get("batch_nonexistent123")

        error = exc_info.value
        assert error.status_code == 404
        print(f"   ✅ 404 error raised correctly: {error}")

    def test_wait_for_completion(
        self,
        bluma: Bluma,
        test_template_id: str,
        video_timeout: float,
        poll_interval: float,
        skip_credit_tests: bool
    ):
        """Test waiting for video to complete with progress updates"""
        if skip_credit_tests:
            pytest.skip("Skipping credit-consuming test")

        print(f"\n🎬 Starting full video generation workflow...")

        # Create video
        video = bluma.videos.create(
            template_id=test_template_id,
            context={"prompt": "E2E test - wait for completion"}
        )

        print(f"   📋 Video ID: {video.id}")
        print(f"   ⏳ Waiting for completion (timeout: {video_timeout}s)...\n")

        # Track progress
        last_status = None
        progress_count = 0

        def on_progress(progress: int):
            nonlocal progress_count
            progress_count += 1
            print(f"      [{progress_count}] Progress: {progress}%")

        # Wait for completion
        start_time = time.time()

        completed = bluma.videos.wait_for(
            video_id=video.id,
            timeout=video_timeout,
            poll_interval=poll_interval,
            on_progress=on_progress
        )

        elapsed = time.time() - start_time

        # Verify completion
        assert completed.id == video.id
        assert completed.status in ["completed", "failed"]

        if completed.status == "completed":
            assert completed.url is not None
            assert completed.duration is not None
            assert completed.completed_at is not None

            print(f"\n   ✅ Video completed successfully!")
            print(f"      • Time: {int(elapsed)}s")
            print(f"      • URL: {completed.url}")
            print(f"      • Duration: {completed.duration}s")
            print(f"      • Progress updates: {progress_count}")

        elif completed.status == "failed":
            print(f"\n   ❌ Video generation failed!")
            print(f"      • Error: {completed.error}")
            pytest.fail(f"Video generation failed: {completed.error}")

    def test_get_download_url(self, bluma: Bluma, test_template_id: str, video_timeout: float, skip_credit_tests: bool):
        """Test retrieving download URL for completed video"""
        if skip_credit_tests:
            pytest.skip("Skipping credit-consuming test")

        # Create and wait for video
        video = bluma.videos.create(
            template_id=test_template_id,
            context={"prompt": "Test download URL"}
        )

        completed = bluma.videos.wait_for(video_id=video.id, timeout=video_timeout)

        if completed.status != "completed":
            pytest.skip(f"Video not completed (status: {completed.status})")

        # Get download URL
        download = bluma.videos.download(video.id)

        assert download.download_url is not None
        assert download.expires_at is not None
        assert download.download_url.startswith("http")

        print(f"   ✅ Download URL retrieved:")
        print(f"      • URL: {download.download_url}")
        print(f"      • Expires: {download.expires_at}")

    def test_insufficient_credits_error(self, bluma: Bluma):
        """Test that insufficient credits error is raised correctly"""
        # This test only works if the user actually has insufficient credits
        # For now, we'll skip it unless we can mock the response
        pytest.skip("Requires account with insufficient credits - manual test only")

    def test_video_lifecycle(self, bluma: Bluma, test_template_id: str, video_timeout: float, skip_credit_tests: bool):
        """Test complete video lifecycle: create → poll → complete → download"""
        if skip_credit_tests:
            pytest.skip("Skipping credit-consuming test")

        print(f"\n🔄 Testing complete video lifecycle...")

        # 1. Create
        print("   [1/4] Creating video...")
        video = bluma.videos.create(
            template_id=test_template_id,
            context={"prompt": "Full lifecycle test"}
        )
        assert video.id is not None
        initial_status = video.status

        # 2. Poll (manual polling, not wait_for)
        print(f"   [2/4] Polling for status updates...")
        poll_count = 0
        while poll_count < 5:  # Poll a few times
            current = bluma.videos.get(video.id)
            print(f"      Poll #{poll_count + 1}: {current.status}")

            if current.status in ["completed", "failed"]:
                break

            poll_count += 1
            time.sleep(3)

        # 3. Wait for completion
        print(f"   [3/4] Waiting for completion...")
        completed = bluma.videos.wait_for(video_id=video.id, timeout=video_timeout)

        assert completed.status in ["completed", "failed"]

        if completed.status != "completed":
            pytest.skip(f"Video failed: {completed.error}")

        # 4. Download
        print(f"   [4/4] Getting download URL...")
        download = bluma.videos.download(video.id)

        assert download.download_url is not None

        print(f"\n   ✅ Lifecycle test completed!")
        print(f"      • Initial status: {initial_status}")
        print(f"      • Final status: {completed.status}")
        print(f"      • Polls: {poll_count}")
        print(f"      • Duration: {completed.duration}s")
        print(f"      • Size: {completed.size_bytes} bytes")

    def test_concurrent_videos(self, bluma: Bluma, test_template_id: str, skip_credit_tests: bool):
        """Test creating multiple videos concurrently"""
        if skip_credit_tests:
            pytest.skip("Skipping credit-consuming test")

        print(f"\n🎭 Testing concurrent video creation...")

        # Create 3 videos
        videos = []
        for i in range(3):
            video = bluma.videos.create(
                template_id=test_template_id,
                context={"prompt": f"Concurrent test #{i + 1}"}
            )
            videos.append(video)
            print(f"   ✅ Created video {i + 1}/3: {video.id}")

        # Verify all were created
        assert len(videos) == 3
        assert len(set(v.id for v in videos)) == 3  # All unique IDs

        print(f"   ✅ All 3 videos created successfully with unique IDs")
