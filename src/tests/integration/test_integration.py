"""Integration tests for Beautiful Captions."""

import os
import pytest
from pathlib import Path
import tempfile
import shutil
from src import (
    add_captions,
    process_video,
    StyleConfig,
    AnimationConfig,
    CaptionConfig,
)

@pytest.fixture
def test_data():
    """Create temporary test data directory with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        
        # Create a dummy video file (minimal valid MP4)
        video_path = temp_path / "test.mp4"
        with open(video_path, "wb") as f:
            # MP4 magic bytes + minimal valid structure
            f.write(bytes.fromhex("000000206674797069736F6D"))
            f.write(bytes([0] * 1000))
            
        # Create a sample SRT file
        srt_path = temp_path / "test.srt"
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("""1
00:00:01,000 --> 00:00:04,000
Hello, world!

2
00:00:04,100 --> 00:00:06,000
This is a test.""")
            
        yield {
            "dir": temp_path,
            "video": video_path,
            "srt": srt_path
        }

@pytest.mark.integration
def test_add_captions_basic(test_data):
    """Test basic caption addition workflow."""
    output_path = test_data["dir"] / "output.mp4"
    
    result = add_captions(
        test_data["video"],
        test_data["srt"],
        output_path=output_path
    )
    
    assert result.exists()
    assert result.stat().st_size > 0

@pytest.mark.integration
def test_add_captions_with_style(test_data):
    """Test caption addition with custom styling."""
    config = CaptionConfig(
        style=StyleConfig(
            font="Montserrat",
            position=0.8,
            color="yellow"
        ),
        animation=AnimationConfig(
            enabled=True,
            keyframes=15
        )
    )
    
    output_path = test_data["dir"] / "styled.mp4"
    
    result = add_captions(
        test_data["video"],
        test_data["srt"],
        output_path=output_path,
        config=config
    )
    
    assert result.exists()
    assert result.stat().st_size > 0

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("ASSEMBLYAI_API_KEY"),
    reason="AssemblyAI API key not provided"
)
async def test_process_video_with_transcription(test_data):
    """Test full video processing with transcription."""
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    output_path = test_data["dir"] / "transcribed.mp4"
    
    result = await process_video(
        test_data["video"],
        transcribe_with="assemblyai",
        api_key=api_key,
        output_path=output_path
    )
    
    assert result.exists()
    assert result.stat().st_size > 0