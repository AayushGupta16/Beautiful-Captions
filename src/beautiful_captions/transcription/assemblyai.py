import os
import logging
from typing import List
import assemblyai as aai
from datetime import timedelta
import time  # Use time instead of asyncio

from .base import TranscriptionService, Utterance, Word

logger = logging.getLogger(__name__)

class AssemblyAIService(TranscriptionService):
    """
    Transcription service using AssemblyAI
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the AssemblyAI service
        
        Args:
            api_key: AssemblyAI API key
        """
        self.api_key = api_key
        
    def transcribe(self, audio_path: str, diarize: bool = False, speaker_count: int = None) -> List[Utterance]:
        """
        Transcribe audio using AssemblyAI
        
        Args:
            audio_path: Path to audio file
            diarize: Whether to enable speaker diarization
            speaker_count: Optional number of speakers (None for auto-detection)
            
        Returns:
            List of utterances
        """
        
        # Create configuration
        config = aai.TranscriptionConfig(
            speaker_labels=diarize,
            speakers_expected=speaker_count,
            punctuate=True,
            format_text=True,
            speech_model="best tier",
        )
        
        try:
            # Set up the transcriber with config
            transcriber = aai.Transcriber(config=config)
            
            # First upload the file and get a transcript object - with retry logic
            max_retries = 3
            retry_delay = 5  # seconds
            transcript = None
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Submitting transcription job (attempt {attempt+1}/{max_retries})...")
                    # Use the transcriber directly
                    transcript = transcriber.submit(audio_path)
                    break
                except Exception as e:
                    logger.warning(f"Transcription submission failed (attempt {attempt+1}): {str(e)}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)  # Use time.sleep instead of await asyncio.sleep
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error("All retry attempts failed")
                        raise
            
            # Then poll for completion with a timeout
            max_wait_time = 600  # 10 minutes max wait time
            poll_interval = 5    # Check every 5 seconds
            wait_time = 0
            
            logger.info("Waiting for AssemblyAI transcription to complete...")
            while wait_time < max_wait_time:
                # Get the latest status
                try:
                    # Access the status directly without trying to access a nested property
                    status = transcript.status
                    
                    if status == "completed":
                        logger.info("Transcription completed successfully")
                        break
                    elif status == "error":
                        error_msg = getattr(transcript, "error", "Unknown error")
                        raise Exception(f"Transcription failed with error: {error_msg}")
                except Exception as e:
                    logger.warning(f"Error checking transcription status: {str(e)}")
                    # Continue polling despite status check errors
                
                # Wait before polling again - use time.sleep
                time.sleep(poll_interval)
                wait_time += poll_interval
                logger.info(f"Waiting for transcription... ({wait_time}s elapsed)")
            
            if wait_time >= max_wait_time:
                raise Exception("Transcription timed out after waiting for 10 minutes")
            
            # Get the completed transcript
            completed_transcript = transcript.get()
            
            # Update to access status directly
            if completed_transcript.status != "completed":
                raise Exception(f"Transcription failed with status: {completed_transcript.status}")
            
            utterances: List[Utterance] = []
            
            for u in completed_transcript.utterances:
                words = [
                    Word(
                        text=w.text,
                        start=timedelta(milliseconds=w.start),
                        end=timedelta(milliseconds=w.end)
                    )
                    for w in u.words
                ]
                
                # Use speaker label if available, otherwise "Speaker 0"
                speaker = u.speaker or "Speaker 0"
                
                utterances.append(
                    Utterance(
                        text=u.text,
                        start=timedelta(milliseconds=u.start),
                        end=timedelta(milliseconds=u.end),
                        speaker=speaker,
                        words=words
                    )
                )
            
            return utterances
            
        except Exception as e:
            logger.error(f"AssemblyAI transcription failed: {str(e)}")
            raise
            
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
        # The rest of the method remains unchanged
        srt_content = ""
        subtitle_index = 1
        
        for utterance in utterances:
            # Determine how to split words into lines
            if max_words_per_line > 1 and utterance.words:
                word_index = 0
                
                while word_index < len(utterance.words):
                    # Calculate how many words to include in this line
                    remaining_words = len(utterance.words) - word_index
                    line_word_count = min(max_words_per_line, remaining_words)
                    
                    # Extract the words for this line
                    line_words = utterance.words[word_index:word_index + line_word_count]
                    line = " ".join([w.text for w in line_words])
                    
                    # Get timing for this line
                    start = line_words[0].start
                    end = line_words[-1].end
                    
                    # Format the timing
                    start_str = f"{start.total_seconds()//3600:02.0f}:{(start.total_seconds()//60)%60:02.0f}:{start.total_seconds()%60:06.3f}".replace(".", ",")
                    end_str = f"{end.total_seconds()//3600:02.0f}:{(end.total_seconds()//60)%60:02.0f}:{end.total_seconds()%60:06.3f}".replace(".", ",")
                    
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
                # Use one subtitle per word
                for word in utterance.words:
                    # Format the timing
                    start = word.start
                    end = word.end
                    
                    start_str = f"{start.total_seconds()//3600:02.0f}:{(start.total_seconds()//60)%60:02.0f}:{start.total_seconds()%60:06.3f}".replace(".", ",")
                    end_str = f"{end.total_seconds()//3600:02.0f}:{(end.total_seconds()//60)%60:02.0f}:{end.total_seconds()%60:06.3f}".replace(".", ",")
                    
                    srt_content += f"{subtitle_index}\n"
                    srt_content += f"{start_str} --> {end_str}\n"
                    
                    # Add speaker label if requested
                    if include_speaker_labels:
                        srt_content += f"{utterance.speaker}: {word.text}\n\n"
                    else:
                        srt_content += f"{word.text}\n\n"
                    
                    subtitle_index += 1
                
        return srt_content