"""
Audio Speech Recognition module for MediSynth Agent.

This module handles audio input processing and speech-to-text conversion
using OpenAI Whisper for high-quality medical transcription.
"""

import asyncio
import io
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Union

import librosa
import numpy as np
import soundfile as sf
import whisper
from pydub import AudioSegment


class ASRProcessor:
    """Audio Speech Recognition processor using OpenAI Whisper."""
    
    def __init__(self, model_size: str = "base", device: str = "cpu"):
        """
        Initialize the ASR processor.
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            device: Device to run inference on ("cpu" or "cuda")
        """
        self.model_size = model_size
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the Whisper model."""
        try:
            self.model = whisper.load_model(self.model_size, device=self.device)
            print(f"Loaded Whisper model: {self.model_size}")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            raise
    
    def preprocess_audio(
        self, 
        audio_data: Union[str, bytes, np.ndarray], 
        target_sr: int = 16000
    ) -> np.ndarray:
        """
        Preprocess audio data for transcription.
        
        Args:
            audio_data: Audio file path, bytes, or numpy array
            target_sr: Target sample rate for preprocessing
            
        Returns:
            Preprocessed audio as numpy array
        """
        try:
            if isinstance(audio_data, str):
                # Load from file path
                audio, sr = librosa.load(audio_data, sr=target_sr)
            elif isinstance(audio_data, bytes):
                # Load from bytes
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_file.flush()
                    audio, sr = librosa.load(tmp_file.name, sr=target_sr)
                Path(tmp_file.name).unlink()  # Clean up temp file
            elif isinstance(audio_data, np.ndarray):
                audio = audio_data
                sr = target_sr
            else:
                raise ValueError("Unsupported audio data type")
            
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            # Ensure audio is mono
            if len(audio.shape) > 1:
                audio = librosa.to_mono(audio)
            
            return audio
            
        except Exception as e:
            print(f"Error preprocessing audio: {e}")
            raise
    
    def convert_audio_format(
        self, 
        input_path: str, 
        output_format: str = "wav"
    ) -> str:
        """
        Convert audio file to specified format.
        
        Args:
            input_path: Path to input audio file
            output_format: Target format (wav, mp3, etc.)
            
        Returns:
            Path to converted audio file
        """
        try:
            audio = AudioSegment.from_file(input_path)
            
            # Create output path
            input_path_obj = Path(input_path)
            output_path = input_path_obj.with_suffix(f'.{output_format}')
            
            # Export in target format
            audio.export(str(output_path), format=output_format)
            
            return str(output_path)
            
        except Exception as e:
            print(f"Error converting audio format: {e}")
            raise
    
    async def transcribe_async(
        self, 
        audio_data: Union[str, bytes, np.ndarray],
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> dict:
        """
        Asynchronously transcribe audio to text.
        
        Args:
            audio_data: Audio input (file path, bytes, or numpy array)
            language: Language code (e.g., "en", "es") or None for auto-detection
            task: "transcribe" or "translate"
            
        Returns:
            Dictionary with transcription results
        """
        def _transcribe():
            # Preprocess audio
            audio = self.preprocess_audio(audio_data)
            
            # Transcribe using Whisper
            result = self.model.transcribe(
                audio,
                language=language,
                task=task,
                verbose=False
            )
            
            return result
        
        # Run transcription in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _transcribe)
        
        return result
    
    def transcribe(
        self, 
        audio_data: Union[str, bytes, np.ndarray],
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> dict:
        """
        Synchronously transcribe audio to text.
        
        Args:
            audio_data: Audio input (file path, bytes, or numpy array)
            language: Language code (e.g., "en", "es") or None for auto-detection
            task: "transcribe" or "translate"
            
        Returns:
            Dictionary with transcription results
        """
        # Preprocess audio
        audio = self.preprocess_audio(audio_data)
        
        # Transcribe using Whisper
        result = self.model.transcribe(
            audio,
            language=language,
            task=task,
            verbose=False
        )
        
        return result
    
    def extract_segments_with_timestamps(self, transcription_result: dict) -> list:
        """
        Extract text segments with timestamps from transcription result.
        
        Args:
            transcription_result: Result from transcribe() method
            
        Returns:
            List of segments with text and timestamps
        """
        segments = []
        
        for segment in transcription_result.get("segments", []):
            segments.append({
                "text": segment["text"].strip(),
                "start": segment["start"],
                "end": segment["end"],
                "confidence": segment.get("no_speech_prob", 0.0)
            })
        
        return segments
    
    def get_confidence_score(self, transcription_result: dict) -> float:
        """
        Calculate overall confidence score for transcription.
        
        Args:
            transcription_result: Result from transcribe() method
            
        Returns:
            Overall confidence score (0.0 to 1.0)
        """
        segments = transcription_result.get("segments", [])
        
        if not segments:
            return 0.0
        
        # Calculate average confidence (1 - no_speech_prob)
        total_confidence = sum(
            1.0 - segment.get("no_speech_prob", 0.0) 
            for segment in segments
        )
        
        return total_confidence / len(segments)


# Factory function for easy instantiation
def create_asr_processor(model_size: str = "base", device: str = "cpu") -> ASRProcessor:
    """
    Factory function to create an ASR processor.
    
    Args:
        model_size: Whisper model size
        device: Device for inference
        
    Returns:
        Configured ASRProcessor instance
    """
    return ASRProcessor(model_size=model_size, device=device)
