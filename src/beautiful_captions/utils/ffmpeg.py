"""FFmpeg utilities for video and audio processing."""

import logging
from pathlib import Path
from typing import Union, Tuple, Optional
import subprocess
from ..styling.style import FontManager

logger = logging.getLogger(__name__)

def extract_audio(video_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Extract audio from video file.
    
    Args:
        video_path: Input video file path
        output_path: Output audio file path
    
    Raises:
        subprocess.CalledProcessError: If FFmpeg command fails
    """
    try:
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # No video
            '-acodec', 'aac',
            '-b:a', '192k',
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Audio extracted successfully")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg audio extraction failed: {e.stderr}")
        raise

def combine_video_subtitles(
    video_path: Union[str, Path],
    subtitle_path: Union[str, Path],
    output_path: Union[str, Path],
    cuda: Optional[bool] = False
) -> None:
    """Combine video with ASS subtitles.
    
    Args:
        video_path: Input videeo file path
        subtitle_path: ASS subtitle file path
        output_path: Output video file path
    
    Raises:
        subprocess.CalledProcessError: If FFmpeg command fails
    """
    font_manager = FontManager()
    fonts_dir_path = font_manager.font_dir 
    escaped_fonts_dir = str(fonts_dir_path).replace('\\', '/').replace(':', '\\:')  


    try:
        if cuda:
            cmd = [
                "ffmpeg",
                "-hwaccel", "cuda",
                "-hwaccel_output_format", "cuda",
                "-i", str(video_path),
                "-vf", f"hwdownload,format=nv12,ass={subtitle_path}:fontsdir={escaped_fonts_dir}",
                "-c:v", "h264_nvenc",
                "-preset", "medium",
                "-g", "60",
                "-keyint_min", "60",
                "-c:a", "copy",
                "-y",
                "-loglevel", "error",  # Only show errors
                output_path
            ]
        else:
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-vf", f"ass={subtitle_path}:fontsdir={escaped_fonts_dir}",
                "-c:a", "copy",  # Copy audio stream
                "-preset", "medium",  # Encoding preset
                "-movflags", "+faststart",  # Enable fast start for web playback
                "-y",  # Overwrite output file
                "-loglevel", "error",  # Only show errors
                str(output_path)
            ]
        
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Subtitles combined with video successfully")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg subtitle combination failed: {e.stderr}")
        raise

def get_video_duration(video_path: Union[str, Path]) -> float:
    """Get video duration in seconds.
    
    Args:
        video_path: Input video file path
        
    Returns:
        Duration in seconds
        
    Raises:
        subprocess.CalledProcessError: If FFmpeg command fails
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        return duration
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFprobe duration check failed: {e.stderr}")
        raise

def get_video_dimensions(video_path: Union[str, Path]) -> Tuple[int, int]:
    """Get video width and height.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Tuple of (width, height)
        
    Raises:
        subprocess.CalledProcessError: If FFmpeg command fails
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0',
            str(video_path)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        width, height = map(int, result.stdout.strip().split('x'))
        return width, height
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFprobe dimension check failed: {e.stderr}")
        raise