"""Functional API for video captioning."""

import logging
from pathlib import Path
from typing import Optional, Union, Literal, Dict, Any
from .config import CaptionConfig, StyleConfig, DiarizationConfig
from .video import Video
from ..transcription.assemblyai import AssemblyAIService
from ..transcription.base import TranscriptionService
from ..utils.subtitles import style_srt_content


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

async def add_subtitles(
    video_path: Union[str, Path],
    transcribe_with: ServiceType,
    api_key: str,
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[CaptionConfig] = None,
    style: Optional[Union[str, Dict[str, Any], StyleConfig]] = None,
    srt_output_path: Optional[Union[str, Path]] = None,
    cuda: Optional[bool] = False 
) -> Union[Path, tuple[Path, Path]]:
    """Process a video by transcribing and adding captions.
    
    Args:
        video_path: Path to input video
        transcribe_with: Transcription service to use
        api_key: API key for transcription service
        output_path: Path for output video (optional)
        config: Caption configuration (optional)
        style: Style configuration (optional). Can include censorship options via
               style.censor_subtitles and style.custom_censored_words.
        srt_output_path: (Optional) Path to write out the generated SRT content.
                         If provided, the SRT file will be created (including parent directories)
                         and its path will be returned along with the video output.
        cuda: Use CUDA acceleration for video processing (optional)
    
    Returns:
        Either the Path to the output video, or a tuple (video_output_path, srt_file_path)
        if srt_output_path was provided.
        
    Examples:
        ```python
        # Example with censorship enabled
        style = {
            "max_words_per_line": 3,
            "censor_subtitles": True,
            "custom_censored_words": {"example": "e**mple"}
        }
        
        await add_subtitles("input.mp4", "assemblyai", API_KEY, style=style)
        ```
    """
    # If config is not provided but style is, create a config with the style
    if config is None:
        # Create style config
        if style is not None:
            if isinstance(style, str):
                style_config = StyleConfig()
            elif isinstance(style, dict):
                style_config = StyleConfig(**style)
            elif isinstance(style, StyleConfig):
                style_config = style
            else:
                raise TypeError("Style must be a string, dictionary, or StyleConfig object")
        else:
            # Create default style config
            style_config = StyleConfig()
        
        # Create config with diarization explicitly enabled for coloring
        # Use the color from style_config as the first color in diarization colors
        diarization_colors = [style_config.color, "yellow", "blue"]
        config = CaptionConfig(
            style=style_config,
            diarization=DiarizationConfig(
                enabled=True,  # Enable diarization for color assignment
                keep_speaker_labels=False,  # Don't show speaker labels by default
                colors=diarization_colors  # Use the style color as first diarization color
            )
        )
    
    service = create_transcription_service(transcribe_with, api_key)
    
    with Video(video_path, config) as video:
        await video.transcribe(service)
        
        # If an SRT output path is provided, process the SRT content through style_srt_content.
        if srt_output_path:
            srt_output_path = Path(srt_output_path)
            srt_output_path.parent.mkdir(parents=True, exist_ok=True)
            # Process the raw SRT content so that speaker labels are replaced with color encodings.
            styled_srt = style_srt_content(
                video._srt_content,
                video.config.diarization.colors,
                encode_speaker_colors=video.config.diarization.enabled,
                keep_speaker_labels=video.config.diarization.keep_speaker_labels,  
                max_words_per_line=video.config.style.max_words_per_line
            )
            with open(srt_output_path, 'w', encoding='utf-8') as f:
                f.write(styled_srt)
        
        video_output = video.add_captions(output_path=output_path, cuda=cuda)
    
    if srt_output_path:
        return video_output, srt_output_path
    return video_output



async def subtitles_from_srt(
    video_path: Union[str, Path],
    srt_input_path: Optional[Union[str, Path]] = None,
    srt_content: Optional[str] = None,
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[CaptionConfig] = None,
    style: Optional[Union[str, Dict[str, Any], StyleConfig]] = None,
    cuda: Optional[bool] = False

) -> Union[Path, tuple[Path, Path]]:
    """Add captions to a video using an existing SRT file.
    
    Args:
        video_path: Path to input video
        srt_input_path: Path to SRT file to read from
        srt_content: Direct SRT content as string (alternative to srt_input_path)
        output_path: Path for output video (optional)
        config: Caption configuration (optional)
        style: Style configuration (optional). Can include settings like 
               max_words_per_line and font options. Note that censorship
               options (censor_subtitles, custom_censored_words) have no effect
               when using existing SRT content, as the text isn't re-transcribed.
        cuda: Use CUDA acceleration for video processing (optional)
    
    Returns:
        Path to the output video with captions
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
        
        # Use the color from style_config as the first color in diarization colors
        diarization_colors = [style_config.color, "yellow", "blue"]
        config = CaptionConfig(
            style=style_config,
            diarization=DiarizationConfig(
                enabled=True,
                keep_speaker_labels=False,
                colors=diarization_colors
            )
        )
    
    with Video(video_path, config) as video:
        if srt_content is None and srt_input_path is not None:
            with open(srt_input_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
    
        video_output = video.add_captions(
            srt_content=srt_content,
            output_path=output_path,
            add_styling=False,
            cuda=cuda
        )
    
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
               or dict of style parameters. Can include censorship options via
               style.censor_subtitles and style.custom_censored_words.
        
    Returns:
        Path to output SRT file
        
    Note:
        If both config and style are provided, style will be ignored.
    """
    # If config is not provided, create one
    if config is None:
        # Create style config
        if style is not None:
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
        else:
            # Create default style config
            style_config = StyleConfig()
            
        # Create a new config with the specified style and default settings for other options
        # Use the color from style_config as the first color in diarization colors
        diarization_colors = [style_config.color, "yellow", "blue"]
        config = CaptionConfig(
            style=style_config,
            diarization=DiarizationConfig(
                enabled=True,
                keep_speaker_labels=False,
                colors=diarization_colors
            )
        )
    
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
        # Use the color from style_config as the first color in diarization colors
        diarization_colors = [style_config.color, "yellow", "blue"]
        config = CaptionConfig(
            style=style_config,
            diarization=DiarizationConfig(
                enabled=True,
                keep_speaker_labels=False,
                colors=diarization_colors
            )
        )
    
    with Video(video_path, config) as video:
        return video.add_captions(
            srt_content=srt_content,
            output_path=output_path
        )