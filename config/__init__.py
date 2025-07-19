"""
Configuration settings for MediSynth Agent.
"""

import os
from typing import Dict, Any


class Config:
    """Application configuration."""
    
    # ASR Configuration
    ASR_MODEL_SIZE = os.getenv("ASR_MODEL_SIZE", "base")  # tiny, base, small, medium, large
    ASR_DEVICE = os.getenv("ASR_DEVICE", "cpu")  # cpu or cuda
    ASR_LANGUAGE = os.getenv("ASR_LANGUAGE", "en")
    
    # Audio Configuration
    AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))
    AUDIO_CHUNK_SIZE = int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))
    
    # NLP Configuration
    NER_MODEL = os.getenv("NER_MODEL", "d4data/biomedical-ner-all")
    USE_GPU_FOR_NLP = os.getenv("USE_GPU_FOR_NLP", "false").lower() == "true"
    
    # UI Configuration
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # File handling
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "100"))  # MB
    ALLOWED_AUDIO_FORMATS = ["wav", "mp3", "m4a", "flac"]
    
    # Export settings
    PDF_EXPORT_ENABLED = os.getenv("PDF_EXPORT_ENABLED", "true").lower() == "true"
    JSON_EXPORT_ENABLED = os.getenv("JSON_EXPORT_ENABLED", "true").lower() == "true"
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get model configuration dictionary."""
        return {
            "asr": {
                "model_size": cls.ASR_MODEL_SIZE,
                "device": cls.ASR_DEVICE,
                "language": cls.ASR_LANGUAGE
            },
            "nlp": {
                "ner_model": cls.NER_MODEL,
                "use_gpu": cls.USE_GPU_FOR_NLP
            },
            "audio": {
                "sample_rate": cls.AUDIO_SAMPLE_RATE,
                "channels": cls.AUDIO_CHANNELS,
                "chunk_size": cls.AUDIO_CHUNK_SIZE
            }
        }
    
    @classmethod
    def get_ui_config(cls) -> Dict[str, Any]:
        """Get UI configuration dictionary."""
        return {
            "port": cls.STREAMLIT_PORT,
            "debug": cls.DEBUG_MODE,
            "max_upload_size": cls.MAX_UPLOAD_SIZE,
            "allowed_formats": cls.ALLOWED_AUDIO_FORMATS
        }


# Default configurations for different deployment scenarios
DEVELOPMENT_CONFIG = {
    "ASR_MODEL_SIZE": "base",
    "DEBUG_MODE": "true",
    "USE_GPU_FOR_NLP": "false"
}

PRODUCTION_CONFIG = {
    "ASR_MODEL_SIZE": "medium",
    "DEBUG_MODE": "false",
    "USE_GPU_FOR_NLP": "true"
}

LIGHTWEIGHT_CONFIG = {
    "ASR_MODEL_SIZE": "tiny",
    "DEBUG_MODE": "false",
    "USE_GPU_FOR_NLP": "false"
}
