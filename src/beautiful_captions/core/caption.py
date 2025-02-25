"""Functional API for video captioning."""

import logging
from pathlib import Path
from typing import Optional, Union, Literal, Dict, Any

from .config import CaptionConfig, StyleConfig
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
    config: Optional[CaptionConfig] = None,
    style: Optional[Union[str, Dict[str, Any], StyleConfig]] = None,
    srt_output_path: Optional[Union[str, Path]] = None  
) -> Union[Path, tuple[Path, Path]]:
    """Process a video by transcribing and adding captions.
    
    Args:
        video_path: Path to input video
        transcribe_with: Transcription service to use
        api_key: API key for transcription service
        output_path: Path for output video (optional)
        config: Caption configuration (optional)
        style: Style configuration (optional)
        srt_output_path: (Optional) Path to write out the generated SRT content.
                         If provided, the SRT file will be created (including parent directories)
                         and its path will be returned along with the video output.
    
    Returns:
        Either the Path to the output video, or a tuple (video_output_path, srt_file_path)
        if srt_output_path was provided.
    """
    # If config is not provided but style is, create a config with the style
    if config is None and style is not None:
        if isinstance(style, str):
            style_config = StyleConfig()
        elif isinstance(style, dict):
            style_config = StyleConfig(**style)
        elif isinstance(style, StyleConfig):
            style_config = style
        else:
            raise TypeError("Style must be a string, dictionary, or StyleConfig object")
        config = CaptionConfig(style=style_config)
    
    service = create_transcription_service(transcribe_with, api_key)
    
    with Video(video_path, config) as video:
        await video.transcribe(service)
        
        # If an SRT output path is provided, write the SRT content there.
        if srt_output_path:
            srt_output_path = Path(srt_output_path)
            srt_output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(srt_output_path, 'w', encoding='utf-8') as f:
                f.write(video._srt_content)
        
        video_output = video.add_captions(output_path=output_path)
    
    # Return a tuple if SRT file was written, otherwise just the video output.
    if srt_output_path:
        return video_output, srt_output_path
    return video_output



def add_captions(
    video_path: Union[str, Path],
    srt_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[CaptionConfig] = None,
    style: Optional[Union[str, Dict[str, Any], StyleConfig]] = None,
    srt_output_path: Optional[Union[str, Path]] = None  # NEW optional parameter
) -> Union[Path, tuple[Path, Path]]:
    """Add captions to a video using an existing SRT file.
    
    Args:
        video_path: Path to input video
        srt_path: Path to SRT file to read from
        output_path: Path for output video (optional)
        config: Caption configuration (optional)
        style: Style configuration (optional)
        srt_output_path: (Optional) Path to write out the SRT content.
    
    Returns:
        Either the Path to the output video, or a tuple (video_output_path, srt_file_path)
        if srt_output_path was provided.
    """
    if config is None and style is not None:
        if isinstance(style, str):
            style_config = StyleConfig()
        elif isinstance(style, dict):
            style_config = StyleConfig(**style)
        elif isinstance(style, StyleConfig):
            style_config = style
        else:
            raise TypeError("Style must be a string, dictionary, or StyleConfig object")
        config = CaptionConfig(style=style_config)
    
    with Video(video_path, config) as video:
        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        # Write SRT content to file if an output path is specified.
        if srt_output_path:
            srt_output_path = Path(srt_output_path)
            srt_output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(srt_output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
        
        video_output = video.add_captions(
            srt_content=srt_content,
            output_path=output_path
        )
    
    if srt_output_path:
        return video_output, srt_output_path
    return video_output


async def extract_subtitles(
    video_path: Union[str, Path],
    transcribe_with: ServiceType,
    api_key: str,
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[CaptionConfig] = None,
    style: Optional[Union[str, Dict[str, Any], StyleConfig]] = None
) -> Path:
    """Extract subtitles from a video without creating a new video.
    
    Args:
        video_path: Path to input video
        transcribe_with: Transcription service to use
        api_key: API key for transcription service
        output_path: Path for output SRT file (optional)
        config: Caption configuration (optional)
        style: Style configuration - can be a preset name, StyleConfig object, 
               or dict of style parameters (optional)
        
    Returns:
        Path to output SRT file
        
    Note:
        If both config and style are provided, style will be ignored.
    """
    # If config is not provided but style is, create a config with the style
    if config is None and style is not None:
        if isinstance(style, str):
            # Handle preset style names
            style_config = StyleConfig()
            # You could implement preset styles here
        elif isinstance(style, dict):
            # Convert dict to StyleConfig
            style_config = StyleConfig(**style)
        elif isinstance(style, StyleConfig):
            # Use the provided StyleConfig directly
            style_config = style
        else:
            raise TypeError("Style must be a string, dictionary, or StyleConfig object")
            
        # Create a new config with the specified style and default settings for other options
        config = CaptionConfig(style=style_config)
    
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
    config: Optional[CaptionConfig] = None,
    style: Optional[Union[str, Dict[str, Any], StyleConfig]] = None
) -> Path:
    """Add captions to a video using SRT content directly.
    
    Args:
        video_path: Path to input video
        srt_content: SRT subtitle content as string
        output_path: Path for output video (optional)
        config: Caption configuration (optional)
        style: Style configuration - can be a preset name, StyleConfig object, 
               or dict of style parameters (optional)
        
    Returns:
        Path to output video file
        
    Note:
        If both config and style are provided, style will be ignored.
    """
    # If config is not provided but style is, create a config with the style
    if config is None and style is not None:
        if isinstance(style, str):
            # Handle preset style names
            style_config = StyleConfig()
            # You could implement preset styles here
        elif isinstance(style, dict):
            # Convert dict to StyleConfig
            style_config = StyleConfig(**style)
        elif isinstance(style, StyleConfig):
            # Use the provided StyleConfig directly
            style_config = style
        else:
            raise TypeError("Style must be a string, dictionary, or StyleConfig object")
            
        # Create a new config with the specified style and default settings for other options
        config = CaptionConfig(style=style_config)
    
    with Video(video_path, config) as video:
        return video.add_captions(
            srt_content=srt_content,
            output_path=output_path
        )