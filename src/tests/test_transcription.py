"""Tests for transcription services."""

import pytest
from unittest.mock import Mock, patch
from src.transcription.base import TranscriptionService, Word, Utterance
from src.transcription.assemblyai import AssemblyAIService

class MockTranscriptionService(TranscriptionService):
    """Mock implementation of TranscriptionService for testing."""
    async def transcribe(self, audio_path: str, max_speakers: int = 3):
        return [
            Utterance(
                speaker="Speaker 1",
                words=[
                    Word(text="Hello", start=0, end=1000),
                    Word(text="world", start=1000, end=2000)
                ],
                start=0,
                end=2000
            )
        ]
    
    def to_srt(self, utterances, speaker_colors):
        return "1\n00:00:00,000 --> 00:00:02,000\nHello world\n"

def test_transcription_service_base():
    """Test TranscriptionService base class."""
    service = MockTranscriptionService(api_key="test_key")
    assert service.api_key == "test_key"

@pytest.mark.asyncio
async def test_assemblyai_transcribe():
    """Test AssemblyAI transcription."""
    with patch("assemblyai.Transcriber") as mock_transcriber:
        # Mock AssemblyAI response
        mock_transcript = Mock()
        mock_transcript.status = "completed"
        mock_transcript.utterances = [
            Mock(
                speaker="A",
                start=0,
                end=2000,
                words=[
                    Mock(text="Hello", start=0, end=1000),
                    Mock(text="world", start=1000, end=2000)
                ]
            )
        ]
        
        mock_transcriber.return_value.transcribe.return_value = mock_transcript
        
        service = AssemblyAIService(api_key="test_key")
        utterances = await service.transcribe("test.mp3", max_speakers=2)
        
        assert len(utterances) == 1
        assert utterances[0].speaker == "Speaker A"
        assert len(utterances[0].words) == 2
        assert utterances[0].words[0].text == "Hello"

def test_assemblyai_to_srt():
    """Test AssemblyAI SRT conversion."""
    service = AssemblyAIService(api_key="test_key")
    
    utterances = [
        Utterance(
            speaker="Speaker 1",
            words=[
                Word(text="Hello", start=0, end=1000),
                Word(text="world", start=1000, end=2000)
            ],
            start=0,
            end=2000
        )
    ]
    
    srt = service.to_srt(utterances, speaker_colors=["white", "yellow"])
    
    # Verify SRT format
    assert "00:00:00,000" in srt
    assert "00:00:01,000" in srt
    assert "00:00:02,000" in srt
    assert "<font color=\"white\">" in srt
    assert "Speaker 1:" in srt
    assert "Hello" in srt
    assert "world" in srt

@pytest.mark.asyncio
async def test_assemblyai_transcribe_error():
    """Test AssemblyAI transcription error handling."""
    with patch("assemblyai.Transcriber") as mock_transcriber:
        # Mock failed transcription
        mock_transcript = Mock()
        mock_transcript.status = "error"
        mock_transcriber.return_value.transcribe.return_value = mock_transcript
        
        service = AssemblyAIService(api_key="test_key")
        
        with pytest.raises(Exception) as exc_info:
            await service.transcribe("test.mp3")
        assert "Transcription failed" in str(exc_info.value)

def test_assemblyai_speaker_mapping():
    """Test speaker mapping in AssemblyAI service."""
    service = AssemblyAIService(api_key="test_key")
    
    utterances = [
        Utterance(speaker="A", words=[Word(text="Hi", start=0, end=1000)], start=0, end=1000),
        Utterance(speaker="B", words=[Word(text="Hello", start=1000, end=2000)], start=1000, end=2000),
        Utterance(speaker="A", words=[Word(text="Bye", start=2000, end=3000)], start=2000, end=3000)
    ]
    
    srt = service.to_srt(utterances, speaker_colors=["white", "yellow"])
    
    # Check that the same speaker gets the same color
    first_a = srt.find("Speaker A:")
    second_a = srt.rfind("Speaker A:")
    assert first_a != -1 and second_a != -1
    
    color_a1 = srt[srt.find("<font color=", first_a):srt.find(">", first_a)]
    color_a2 = srt[srt.find("<font color=", second_a):srt.find(">", second_a)]
    assert color_a1 == color_a2