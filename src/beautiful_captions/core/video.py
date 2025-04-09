"""Video processing and captioning core functionality."""

import os
from pathlib import Path
from typing import Optional, Union

import ffmpeg
from ..core.config import CaptionConfig
from ..transcription.base import TranscriptionService
from ..utils.ffmpeg import extract_audio, combine_video_subtitles
from ..utils.subtitles import create_ass_subtitles, style_srt_content


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
        service: Union[str, TranscriptionService],
        api_key: Optional[str] = None,
        max_speakers: int = 3
    ) -> None:
        """Transcribe video audio using specified service.
        
        Args:
            service: Either a TranscriptionService instance or service type string
            api_key: API key for transcription service (required if service is a string)
            max_speakers: Maximum number of speakers to detect
            
        Raises:
            ValueError: If service is a string and no api_key is provided
        """
        if isinstance(service, str):
            if not api_key:
                raise ValueError("API key is required when specifying service by name")
            
            from ..core.caption import create_transcription_service
            service = create_transcription_service(service, api_key)
        
        if not self._audio_path:
            self._audio_path = self.video_path.with_suffix('.aac')
            extract_audio(self.video_path, self._audio_path)
        
        # Get censorship settings from style config
        censor_subtitles = getattr(self.config.style, 'censor_subtitles', False)
        custom_censored_words = getattr(self.config.style, 'custom_censored_words', None)
        
        # Transcribe with optional censorship
        self._utterances = await service.transcribe(
            str(self._audio_path), 
            max_speakers,
            censor_subtitles=censor_subtitles,
            custom_censored_words=custom_censored_words
        )
        
        self._srt_content = service.to_srt(
            self._utterances, 
            self.config.diarization.colors,
            max_words_per_line=self.config.style.max_words_per_line,
            include_speaker_labels=True
        )
        
    def add_captions(
        self,
        srt_input_path: Optional[Union[str, Path]] = None,
        srt_content: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None,
        add_styling: Optional[bool] = True,
        cuda: Optional[bool] = False,
    ) -> Path:
        """Add captions to video.
        
        Args:
            srt_path: Optional path to SRT file
            srt_content: Optional SRT content string (ignored if srt_path is provided)
            output_path: Optional output path (defaults to input path with _captioned suffix)
            
        Returns:
            Path to output video file
        """
        # Get SRT content from file or string or transcription
        if srt_input_path:
            with open(srt_input_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
        elif not srt_content and not self._srt_content:
            raise ValueError("No caption content available. Provide either srt_path, srt_content, or run transcribe() first.")
        
        srt_content = srt_content or self._srt_content
        
        # Apply styling if enabled
        if add_styling and self.config.diarization.enabled:
            srt_content = style_srt_content(
                srt_content, 
                self.config.diarization.colors,
                encode_speaker_colors=True,
                keep_speaker_labels=self.config.diarization.keep_speaker_labels,
                max_words_per_line=self.config.style.max_words_per_line,
                font=self.config.style.font
            )
            
        if not output_path:
            output_path = self.video_path.with_stem(f"{self.video_path.stem}_captioned")
            
        output_path = Path(output_path)
        self._ass_path = output_path.with_suffix('.ass')
        
        create_ass_subtitles(
            srt_content,
            self.video_path,
            self._ass_path,
            self.config.style,
            self.config.animation
        )
        
        combine_video_subtitles(
            self.video_path,
            self._ass_path,
            output_path,
            cuda
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