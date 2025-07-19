"""
Audio recording utilities for real-time speech capture.
"""

import asyncio
import threading
import time
from typing import Callable, Optional

import numpy as np
import pyaudio
import wave


class AudioRecorder:
    """Real-time audio recorder for microphone input."""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        format: int = pyaudio.paInt16
    ):
        """
        Initialize audio recorder.
        
        Args:
            sample_rate: Audio sample rate
            channels: Number of audio channels
            chunk_size: Audio chunk size for processing
            format: Audio format
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = format
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.recording_thread = None
    
    def start_recording(self) -> None:
        """Start recording audio from microphone."""
        if self.is_recording:
            return
        
        self.frames = []
        self.is_recording = True
        
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()
        
        print("Recording started...")
    
    def stop_recording(self) -> bytes:
        """
        Stop recording and return audio data.
        
        Returns:
            Audio data as bytes
        """
        if not self.is_recording:
            return b""
        
        self.is_recording = False
        
        if self.recording_thread:
            self.recording_thread.join()
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        print("Recording stopped.")
        
        # Convert frames to bytes
        audio_data = b"".join(self.frames)
        return audio_data
    
    def _record_audio(self) -> None:
        """Internal method to record audio in separate thread."""
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"Error during recording: {e}")
                break
    
    def save_recording(self, filename: str, audio_data: bytes) -> None:
        """
        Save recorded audio to file.
        
        Args:
            filename: Output filename
            audio_data: Audio data to save
        """
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)
        
        print(f"Audio saved to {filename}")
    
    def get_audio_devices(self) -> list:
        """
        Get list of available audio input devices.
        
        Returns:
            List of device information dictionaries
        """
        devices = []
        
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0:
                devices.append({
                    "index": i,
                    "name": device_info["name"],
                    "sample_rate": device_info["defaultSampleRate"]
                })
        
        return devices
    
    def __del__(self):
        """Cleanup resources."""
        if self.is_recording:
            self.stop_recording()
        
        if hasattr(self, 'audio'):
            self.audio.terminate()
