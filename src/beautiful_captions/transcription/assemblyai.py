"""AssemblyAI transcription service implementation."""

import logging
from typing import List
import assemblyai as aai
from datetime import timedelta

from .base import TranscriptionService, Utterance, Word

logger = logging.getLogger(__name__)

class AssemblyAIService(TranscriptionService):
    """AssemblyAI transcription service implementation."""
    
    def __init__(self, api_key: str):
        """Initialize AssemblyAI client.
        
        Args:
            api_key: AssemblyAI API key
        """
        super().__init__(api_key)
        aai.settings.api_key = api_key
        
    async def transcribe(
        self,
        audio_path: str,
        max_speakers: int = 3
    ) -> List[Utterance]:
        """Transcribe audio using AssemblyAI.
        
        Args:
            audio_path: Path to audio file
            max_speakers: Maximum number of speakers to detect
            
        Returns:
            List of utterances with timing and speaker information
        """
        logger.info(f"Transcribing audio with AssemblyAI: {audio_path}")
        
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            speakers_expected=max_speakers
        )
        
        try:
            transcriber = aai.Transcriber(config=config)
            transcript = transcriber.transcribe(audio_path)
            
            if transcript.status != "completed":
                raise Exception(f"Transcription failed with status: {transcript.status}")
            
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
            
        except Exception as e:
            logger.error(f"AssemblyAI transcription failed: {str(e)}")
            raise
            
    def to_srt(self, utterances: List[Utterance], speaker_colors: List[str]) -> str:
        """Convert utterances to plain SRT format.
        
        Args:
            utterances: List of transcribed utterances
            speaker_colors: List of colors (unused in plain SRT)
            
        Returns:
            SRT formatted string
        """
        srt_content = ""
        subtitle_index = 1
        
        for utterance in utterances:
            for word in utterance.words:
                start_time = timedelta(milliseconds=word.start)
                end_time = timedelta(milliseconds=word.end)
                
                # Format times for SRT
                start_str = f"{start_time.seconds // 3600:02d}:{(start_time.seconds % 3600) // 60:02d}:{start_time.seconds % 60:02d},{start_time.microseconds // 1000:03d}"
                end_str = f"{end_time.seconds // 3600:02d}:{(end_time.seconds % 3600) // 60:02d}:{end_time.seconds % 60:02d},{end_time.microseconds // 1000:03d}"
                
                srt_content += f"{subtitle_index}\n"
                srt_content += f"{start_str} --> {end_str}\n"
                srt_content += f"{utterance.speaker}: {word.text}\n\n"
                
                subtitle_index += 1
        return srt_content