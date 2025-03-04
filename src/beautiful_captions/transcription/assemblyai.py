import logging
import os
from typing import List, Optional, Dict
import assemblyai as aai
from datetime import timedelta
import asyncio

from .base import TranscriptionService, Utterance, Word

logger = logging.getLogger(__name__)

class AssemblyAIService(TranscriptionService):
    """AssemblyAI transcription service implementation."""
    
    def __init__(self, api_key: str):
        """Initialize AssemblyAI client."""
        super().__init__(api_key)
        aai.settings.api_key = api_key
        
    async def transcribe(
        self,
        audio_path: str,
        max_speakers: int = 3,
        censor_subtitles: bool = False,
        custom_censored_words: Optional[Dict[str, str]] = None
    ) -> List[Utterance]:
        """Transcribe audio using AssemblyAI with optional censorship.
        
        Args:
            audio_path: Path to audio file
            max_speakers: Maximum number of speakers to identify
            censor_subtitles: Whether to censor profanity in subtitles
            custom_censored_words: Dictionary of words to censor {word: censored_version}
        """
        logger.info(f"Transcribing audio with AssemblyAI: {audio_path}")
        
        # Check if file exists and log details for debugging
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        logger.info(f"Audio file size: {os.path.getsize(audio_path)} bytes")
        
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            speakers_expected=max_speakers,
            language_detection=True,
            filter_profanity=censor_subtitles
        )
        
        try:
            # Handle the synchronous SDK in an async context
            utterances = await asyncio.to_thread(self._transcribe_sync, audio_path, config)
            
            # Apply custom word censoring if provided
            if custom_censored_words and isinstance(custom_censored_words, dict):
                utterances = self._apply_custom_censoring(utterances, custom_censored_words)
                
            return utterances
            
        except Exception as e:
            logger.error(f"AssemblyAI transcription failed: {str(e)}")
            raise
    
    def _transcribe_sync(self, audio_path: str, config: aai.TranscriptionConfig) -> List[Utterance]:
        """Synchronous implementation that will be run in a separate thread."""
        transcriber = aai.Transcriber(config=config)
        
        # Use the direct transcribe method which handles submission and polling
        logger.info(f"Starting transcription of {audio_path}")
        transcript = transcriber.transcribe(audio_path)
        
        logger.info(f"Transcription complete, status: {getattr(transcript, 'status', 'unknown')}")
        
        if not transcript or transcript.status != "completed":
            logger.error(f"Transcription failed with status: {getattr(transcript, 'status', 'None')}")
            raise Exception(f"Transcription failed with status: {getattr(transcript, 'status', 'None')}")
        
        utterances: List[Utterance] = []
        
        for u in transcript.utterances:
            words = [
                Word(
                    text=w.text,
                    start=w.start,
                    end=w.end
                )
                for w in u.words
            ]
            
            utterance = Utterance(
                speaker=f"Speaker {u.speaker}",
                words=words,
                start=u.start,
                end=u.end
            )
            utterances.append(utterance)
        
        return utterances
        
    def _apply_custom_censoring(self, utterances: List[Utterance], custom_censored_words: Dict[str, str]) -> List[Utterance]:
        """Apply custom word censoring to utterances.
        
        Args:
            utterances: List of utterances to process
            custom_censored_words: Dictionary mapping words to their censored versions
            
        Returns:
            Processed utterances with censored words
        """
        censored_utterances = []
        
        for utterance in utterances:
            censored_words = []
            for word in utterance.words:
                # Check if word text (case-insensitive) is in censored words list
                if word.text.lower() in custom_censored_words:
                    # Replace with censored version
                    word.text = custom_censored_words[word.text.lower()]
                censored_words.append(word)
            
            # Create new utterance with censored words
            censored_utterance = Utterance(
                speaker=utterance.speaker,
                words=censored_words,
                start=utterance.start,
                end=utterance.end
            )
            censored_utterances.append(censored_utterance)
            
        return censored_utterances
            
    def to_srt(self, utterances: List[Utterance], speaker_colors: List[str], max_words_per_line: int = 1, include_speaker_labels: bool = True) -> str:
        """Convert utterances to plain SRT format.
        
        Args:
            utterances: List of transcribed utterances
            speaker_colors: List of colors (used for speaker identification)
            max_words_per_line: Maximum number of words per line
            include_speaker_labels: Whether to include speaker labels in the output
            
        Returns:
            SRT formatted string with speaker labels
        """
        from ..utils.subtitles import group_words_into_lines
        
        srt_content = ""
        subtitle_index = 1
        
        for utterance in utterances:
            # Group words by max_words_per_line
            if max_words_per_line > 1:
                # Group words by their text
                word_texts = [word.text for word in utterance.words]
                grouped_lines = group_words_into_lines(word_texts, max_words_per_line)
                
                # Create groups of words based on the lines
                word_index = 0
                for line in grouped_lines:
                    line_word_count = len(line.split())
                    if word_index + line_word_count <= len(utterance.words):
                        group_start = utterance.words[word_index].start
                        group_end = utterance.words[word_index + line_word_count - 1].end
                        
                        # Format times for SRT
                        start_time = timedelta(milliseconds=group_start)
                        end_time = timedelta(milliseconds=group_end)
                        
                        start_str = f"{start_time.seconds // 3600:02d}:{(start_time.seconds % 3600) // 60:02d}:{start_time.seconds % 60:02d},{start_time.microseconds // 1000:03d}"
                        end_str = f"{end_time.seconds // 3600:02d}:{(end_time.seconds % 3600) // 60:02d}:{end_time.seconds % 60:02d},{end_time.microseconds // 1000:03d}"
                        
                        srt_content += f"{subtitle_index}\n"
                        srt_content += f"{start_str} --> {end_str}\n"
                        
                        # Add speaker label if requested
                        if include_speaker_labels:
                            srt_content += f"{utterance.speaker}: {line}\n\n"
                        else:
                            srt_content += f"{line}\n\n"
                        
                        subtitle_index += 1
                        word_index += line_word_count
            else:
                # Original single-word behavior
                for word in utterance.words:
                    start_time = timedelta(milliseconds=word.start)
                    end_time = timedelta(milliseconds=word.end)
                    
                    # Format times for SRT
                    start_str = f"{start_time.seconds // 3600:02d}:{(start_time.seconds % 3600) // 60:02d}:{start_time.seconds % 60:02d},{start_time.microseconds // 1000:03d}"
                    end_str = f"{end_time.seconds // 3600:02d}:{(end_time.seconds % 3600) // 60:02d}:{end_time.seconds % 60:02d},{end_time.microseconds // 1000:03d}"
                    
                    srt_content += f"{subtitle_index}\n"
                    srt_content += f"{start_str} --> {end_str}\n"
                    
                    # Add speaker label if requested
                    if include_speaker_labels:
                        srt_content += f"{utterance.speaker}: {word.text}\n\n"
                    else:
                        srt_content += f"{word.text}\n\n"
                    
                    subtitle_index += 1
                
        return srt_content