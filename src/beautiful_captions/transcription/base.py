from abc import ABC, abstractmethod
from typing import List, Optional
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
    async def transcribe(self, audio_path: str, max_speakers: int = 3) -> List[Utterance]:
        """
        Transcribe audio file and return list of utterances with speaker diarization
        """
        pass

    @abstractmethod
    def to_srt(self, utterances: List[Utterance], speaker_colors: List[str], max_words_per_line: int = 1) -> str:
        """
        Convert utterances to SRT format with colored speaker labels
        """
        pass