"""Functional API for video captioning."""

import logging
from pathlib import Path
from typing import Optional, Union, Literal

from .config import CaptionConfig
from .video import Video
from ..transcription.assemblyai import AssemblyAIService
from ..transcription.base import TranscriptionService

logger = logging.getLogger(__name__)

ServiceType = Literal["assemblyai", "deepgram", "openai"]

def create_transcription_service(
    service: ServiceType,
    api_key: str
) -> TranscriptionService:
    """Create a transcription service instance.
    
    Args:
        service: Type of transcription service to use
        api_key: API key for the service
        
    Returns:
        Configured transcription service
        
    Raises:
        ValueError: If service type is invalid
    """
    services = {
        "assemblyai": AssemblyAIService,
        "deepgram": None,  # To be implemented
        "openai": None,    # To be implemented
    }
    
    service_class = services.get(service)
    if not service_class:
        available = [s for s, c in services.items() if c is not None]
        raise ValueError(
            f"Invalid or unimplemented service type. "
            f"Currently available services: {', '.join(available)}"
        )
        
    return service_class(api_key)

async def process_video(
    video_path: Union[str, Path],
    transcribe_with: ServiceType,
    api_key: str,
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[CaptionConfig] = None
) -> Path:
    """Process a video by transcribing and adding captions.
    
    Args:
        video_path: Path to input video
        transcribe_with: Transcription service to use
        api_key: API key for transcription service
        output_path: Path for output video (optional)
        config: Caption configuration (optional)
        
    Returns:
        Path to output video file
    """
    service = create_transcription_service(transcribe_with, api_key)
    
    with Video(video_path, config) as video:
        await video.transcribe(service)
        return video.add_captions(output_path=output_path)

def add_captions(
    video_path: Union[str, Path],
    srt_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[CaptionConfig] = None
) -> Path:
    """Add captions to a video using an existing SRT file.
    
    Args:
        video_path: Path to input video
        srt_path: Path to SRT file
        output_path: Path for output video (optional)
        config: Caption configuration (optional)
        
    Returns:
        Path to output video file
    """
    with Video(video_path, config) as video:
        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
            
        return video.add_captions(
            srt_content=srt_content,
            output_path=output_path
        )

async def extract_subtitles(
    video_path: Union[str, Path],
    transcribe_with: ServiceType,
    api_key: str,
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[CaptionConfig] = None
) -> Path:
    """Extract subtitles from a video without creating a new video.
    
    Args:
        video_path: Path to input video
        transcribe_with: Transcription service to use
        api_key: API key for transcription service
        output_path: Path for output SRT file (optional)
        config: Caption configuration (optional)
        
    Returns:
        Path to output SRT file
    """
    service = create_transcription_service(transcribe_with, api_key)
    
    if not output_path:
        output_path = Path(video_path).with_suffix('.srt')
    
    with Video(video_path, config) as video:
        await video.transcribe(service)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(video._srt_content)
            
    return Path(output_path)

def caption_stream(
    video_path: Union[str, Path],
    srt_content: str,
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[CaptionConfig] = None
) -> Path:
    """Add captions to a video using SRT content directly.
    
    Args:
        video_path: Path to input video
        srt_content: SRT subtitle content as string
        output_path: Path for output video (optional)
        config: Caption configuration (optional)
        
    Returns:
        Path to output video file
    """
    with Video(video_path, config) as video:
        return video.add_captions(
            srt_content=srt_content,
            output_path=output_path
        )