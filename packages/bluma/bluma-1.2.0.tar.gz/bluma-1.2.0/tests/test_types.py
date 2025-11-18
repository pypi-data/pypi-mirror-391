"""Tests for Pydantic model validation"""
import pytest
from bluma.types import Video, VideoStatus
from datetime import datetime

# TODO: Add comprehensive type validation tests
def test_video_model_validation():
    """Test Video model validates correctly"""
    data = {
        "id": "test", "status": "completed", "template_id": "test",
        "credits_charged": 5, "created_at": datetime.now().isoformat()
    }
    video = Video(**data)
    assert video.status == VideoStatus.COMPLETED
