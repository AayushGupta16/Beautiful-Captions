"""Tests for video processing."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.core.video import Video
from src.core.config import CaptionConfig

@pytest.fixture
def mock_ffmpeg():
    """Mock FFmpeg operations."""
    with patch("src.utils.ffmpeg.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        yield mock_run

@pytest.fixture
def mock_assemblyai():
    """Mock AssemblyAI service."""
    mock_service = Mock()
    mock_service.transcribe.return_value = [
        Mock(
            speaker="Speaker 1",
            words=[
                Mock(text="Hello", start=1000, end=2000),
                Mock(text="world", start=2100, end=3000)
            ],
            start=1000,
            end=3000
        )
    ]
    return mock_service

async def test_video_initialization(sample_video):
    """Test Video class initialization."""
    video = Video(sample_video)
    assert video.video_path == Path(sample_video)
    assert video.config is not None

def test_video_invalid_path():
    """Test Video initialization with invalid path."""
    with pytest.raises(FileNotFoundError):
        Video("nonexistent.mp4")

async def test_video_transcribe(sample_video, mock_assemblyai, mock_ffmpeg):
    """Test video transcription."""
    video = Video(sample_video)
    await video.transcribe(mock_assemblyai)
    
    # Check that FFmpeg was called to extract audio
    mock_ffmpeg.assert_called()
    
    # Check that transcription service was called
    mock_assemblyai.transcribe.assert_called_once()
    assert video._srt_content is not None

async def test_video_add_captions(sample_video, mock_ffmpeg):
    """Test adding captions to video."""
    video = Video(sample_video)
    srt_content = """1
00:00:01,000 --> 00:00:02,000
Hello world
"""
    
    output_path = video.add_captions(srt_content=srt_content)
    assert output_path.exists()
    mock_ffmpeg.assert_called()

def test_video_cleanup(sample_video, temp_dir):
    """Test temporary file cleanup."""
    video = Video(sample_video)
    
    # Create mock temporary files
    temp_audio = temp_dir / "temp.aac"
    temp_ass = temp_dir / "temp.ass"
    
    with open(temp_audio, "wb") as f:
        f.write(b"test")
    with open(temp_ass, "wb") as f:
        f.write(b"test")
        
    video._audio_path = temp_audio
    video._ass_path = temp_ass
    
    # Test cleanup
    video.cleanup()
    assert not temp_audio.exists()
    assert not temp_ass.exists()

def test_video_context_manager(sample_video, temp_dir):
    """Test Video class as context manager."""
    # Create mock temporary files
    temp_audio = temp_dir / "temp.aac"
    temp_ass = temp_dir / "temp.ass"
    
    with open(temp_audio, "wb") as f:
        f.write(b"test")
    with open(temp_ass, "wb") as f:
        f.write(b"test")
    
    with Video(sample_video) as video:
        video._audio_path = temp_audio
        video._ass_path = temp_ass
        assert temp_audio.exists()
        assert temp_ass.exists()
    
    # Files should be cleaned up after context
    assert not temp_audio.exists()
    assert not temp_ass.exists()

async def test_video_custom_config(sample_video):
    """Test Video with custom configuration."""
    config = CaptionConfig(
        style=StyleConfig(
            font="Rubik",
            position=0.8,
            color="yellow"
        ),
        animation=AnimationConfig(
            enabled=False
        ),
        diarization=DiarizationConfig(
            max_speakers=5
        )
    )
    
    video = Video(sample_video, config=config)
    assert video.config.style.font == "Rubik"
    assert video.config.style.position == 0.8
    assert video.config.style.color == "yellow"
    assert not video.config.animation.enabled
    assert video.config.diarization.max_speakers == 5

@pytest.mark.asyncio
async def test_video_transcribe_with_max_speakers(sample_video, mock_assemblyai, mock_ffmpeg):
    """Test transcription with max speakers configuration."""
    config = CaptionConfig(
        diarization=DiarizationConfig(max_speakers=2)
    )
    
    video = Video(sample_video, config=config)
    await video.transcribe(mock_assemblyai)
    
    # Verify max_speakers was passed to transcription service
    mock_assemblyai.transcribe.assert_called_once_with(
        str(video._audio_path),
        max_speakers=2
    )

def test_video_output_path_generation(sample_video):
    """Test default output path generation."""
    video = Video(sample_video)
    
    # Test default output path (no extension provided)
    output_path = video.add_captions(srt_content="1\n00:00:01,000 --> 00:00:02,000\nTest\n")
    assert output_path.stem.endswith("_captioned")
    assert output_path.suffix == sample_video.suffix
    
    # Test custom output path
    custom_path = Path("custom_output.mp4")
    output_path = video.add_captions(
        srt_content="1\n00:00:01,000 --> 00:00:02,000\nTest\n",
        output_path=custom_path
    )
    assert output_path == custom_path