from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from dataclasses import dataclass

@dataclass
class Word:
    text: str
    start: int  # milliseconds
    end: int    # milliseconds

@dataclass
class Utterance:
    speaker: str
    words: List[Word]
    start: int  # milliseconds
    end: int    # milliseconds

class TranscriptionService(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def transcribe(
        self, 
        audio_path: str, 
        max_speakers: int = 3,
        censor_subtitles: bool = False,
        custom_censored_words: Optional[Dict[str, str]] = None
    ) -> List[Utterance]:
        """
        Transcribe audio file and return list of utterances with speaker diarization
        
        Args:
            audio_path: Path to the audio file
            max_speakers: Maximum number of speakers to identify
            censor_subtitles: Whether to censor profanity in subtitles
            custom_censored_words: Dictionary of words to censor {word: censored_version}
        """
        pass

    @abstractmethod
    def to_srt(self, utterances: List[Utterance], speaker_colors: List[str], max_words_per_line: int = 1, include_speaker_labels: bool = True) -> str:
        """
        Convert utterances to SRT format with colored speaker labels
        
        Args:
            utterances: List of transcribed utterances
            speaker_colors: List of colors for different speakers
            max_words_per_line: Maximum number of words per line
            include_speaker_labels: Whether to include speaker labels in the output
        
        Returns:
            SRT formatted string
        """
        pass