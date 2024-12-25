"""Video processing and captioning core functionality."""

import os
from pathlib import Path
from typing import Optional, Union

import ffmpeg
from ..core.config import CaptionConfig
from ..transcription.base import TranscriptionService
from ..utils.ffmpeg import extract_audio, combine_video_subtitles
from ..utils.subtitles import create_ass_subtitles


class Video:
    """Main video processing class for adding captions."""
    
    def __init__(
        self, 
        video_path: Union[str, Path], 
        config: Optional[CaptionConfig] = None
    ):
        """Initialize video processor.
        
        Args:
            video_path: Path to input video file
            config: Optional caption configuration
        """
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        self.config = config or CaptionConfig()
        self._audio_path: Optional[Path] = None
        self._srt_content: Optional[str] = None
        self._ass_path: Optional[Path] = None
        
    async def transcribe(
        self, 
        service: TranscriptionService,
    ) -> None:
        """Transcribe video audio using specified service.
        
        Args:
            service: Configured transcription service instance
        """
        if not self._audio_path:
            self._audio_path = self.video_path.with_suffix('.aac')
            extract_audio(self.video_path, self._audio_path)
            
        utterances = await service.transcribe(
            str(self._audio_path),
            max_speakers=self.config.diarization.max_speakers
        )
        
        self._srt_content = service.to_srt(
            utterances,
            speaker_colors=self.config.diarization.colors
        )
        
    def add_captions(
        self,
        srt_content: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> Path:
        """Add captions to video.
        
        Args:
            srt_content: Optional SRT content (uses transcribed content if not provided)
            output_path: Optional output path (defaults to input path with _captioned suffix)
            
        Returns:
            Path to output video file
        """
        if not srt_content and not self._srt_content:
            raise ValueError("No caption content available. Either provide SRT content or run transcribe() first.")
            
        srt_content = srt_content or self._srt_content
        if not output_path:
            output_path = self.video_path.with_stem(f"{self.video_path.stem}_captioned")
            
        output_path = Path(output_path)
        self._ass_path = output_path.with_suffix('.ass')
        
        create_ass_subtitles(
            srt_content,
            self._ass_path,
            self.config.style,
            self.config.animation
        )
        
        combine_video_subtitles(
            self.video_path,
            self._ass_path,
            output_path
        )
        
        return output_path
        
    def cleanup(self) -> None:
        """Remove temporary files."""
        if self._audio_path and self._audio_path.exists():
            self._audio_path.unlink()
        if self._ass_path and self._ass_path.exists():
            self._ass_path.unlink()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()