"""Test configuration and fixtures."""

import os
import tempfile
from pathlib import Path
import pytest
import shutil

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

@pytest.fixture
def sample_video(temp_dir):
    """Create a sample video file for testing."""
    video_path = temp_dir / "sample.mp4"
    # Create a minimal valid MP4 file
    with open(video_path, "wb") as f:
        f.write(b"\x00" * 1024)
    return video_path

@pytest.fixture
def sample_srt():
    """Sample SRT content for testing."""
    return """1
00:00:01,000 --> 00:00:04,000
<font color="white">Speaker 1: Hello, world!</font>

2
00:00:04,100 --> 00:00:06,000
<font color="yellow">Speaker 2: How are you?</font>
"""

@pytest.fixture
def mock_assemblyai_response():
    """Mock AssemblyAI response for testing."""
    return {
        "status": "completed",
        "utterances": [
            {
                "speaker": "A",
                "start": 1000,
                "end": 4000,
                "words": [
                    {"text": "Hello", "start": 1000, "end": 2000},
                    {"text": "world", "start": 2100, "end": 4000}
                ]
            }
        ]
    }