"""Tests for caption API functions."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.core.caption import (
    add_captions,
    process_video,
    extract_subtitles,
    caption_stream,
    create_transcription_service
)
from src.core.config import CaptionConfig
from src.transcription.assemblyai import AssemblyAIService
# from src.transcription.deepgram import DeepgramService
# from src.transcription.openai import OpenAIService

@pytest.fixture
def mock_video():
    """Mock Video class."""
    with patch("src.core.caption.Video") as mock:
        instance = mock.return_value.__enter__.return_value
        instance.add_captions.return_value = Path("output.mp4")
        yield instance

def test_create_transcription_service():
    """Test transcription service factory."""
    # Test AssemblyAI
    service = create_transcription_service("assemblyai", "test_key")
    assert isinstance(service, AssemblyAIService)
    
    # Test invalid service
    with pytest.raises(ValueError):
        create_transcription_service("invalid_service", "test_key")

def test_add_captions_with_srt(sample_video, sample_srt, mock_video):
    """Test adding captions from SRT file."""
    srt_path = Path("test.srt")
    with open(srt_path, "w") as f:
        f.write(sample_srt)
    
    output = add_captions(
        video_path=sample_video,
        srt_path=srt_path,
        config=CaptionConfig()
    )
    
    assert output == Path("output.mp4")
    mock_video.add_captions.assert_called_once()

@pytest.mark.asyncio
async def test_process_video(sample_video, mock_video, mock_assemblyai):
    """Test full video processing pipeline."""
    with patch("src.core.caption.create_transcription_service") as mock_create:
        mock_create.return_value = mock_assemblyai
        
        output = await process_video(
            video_path=sample_video,
            transcribe_with="assemblyai",
            api_key="test_key"
        )
        
        assert output == Path("output.mp4")
        mock_video.transcribe.assert_called_once()
        mock_video.add_captions.assert_called_once()

@pytest.mark.asyncio
async def test_extract_subtitles(sample_video, mock_video, mock_assemblyai):
    """Test subtitle extraction."""
    with patch("src.core.caption.create_transcription_service") as mock_create:
        mock_create.return_value = mock_assemblyai
        mock_video._srt_content = "Test subtitles"
        
        output_path = await extract_subtitles(
            video_path=sample_video,
            transcribe_with="assemblyai",
            api_key="test_key"
        )
        
        assert output_path.suffix == ".srt"
        mock_video.transcribe.assert_called_once()
        
        # Check that SRT content was written
        with open(output_path) as f:
            assert f.read() == "Test subtitles"

def test_caption_stream(sample_video, mock_video):
    """Test adding captions from SRT content string."""
    srt_content = "Test subtitles"
    
    output = caption_stream(
        video_path=sample_video,
        srt_content=srt_content
    )
    
    assert output == Path("output.mp4")
    mock_video.add_captions.assert_called_once_with(
        srt_content=srt_content,
        output_path=None
    )

@pytest.mark.asyncio
async def test_process_video_with_config(sample_video, mock_video, mock_assemblyai):
    """Test video processing with custom config."""
    config = CaptionConfig(
        style=StyleConfig(font="Rubik"),
        animation=AnimationConfig(enabled=False)
    )
    
    with patch("src.core.caption.create_transcription_service") as mock_create:
        mock_create.return_value = mock_assemblyai
        
        await process_video(
            video_path=sample_video,
            transcribe_with="assemblyai",
            api_key="test_key",
            config=config
        )
        
        # Verify config was passed to Video class
        mock_video.__init__.assert_called_with(sample_video, config=config)