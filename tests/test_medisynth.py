"""
Unit tests for MediSynth Agent components.
"""

import pytest
import tempfile
import os
from pathlib import Path

# Import modules to test
try:
    from asr import create_asr_processor
    from nlp import create_clinical_processor
    from nlp.soap_generator import create_soap_generator
    from utils import create_file_handler, create_document_exporter
except ImportError:
    pytest.skip("Dependencies not installed", allow_module_level=True)


class TestASRProcessor:
    """Test ASR functionality."""
    
    def test_asr_processor_creation(self):
        """Test ASR processor can be created."""
        processor = create_asr_processor(model_size="tiny")
        assert processor is not None
        assert processor.model_size == "tiny"
    
    def test_audio_preprocessing(self):
        """Test audio preprocessing."""
        processor = create_asr_processor(model_size="tiny")
        
        # Create dummy audio data
        import numpy as np
        dummy_audio = np.random.randn(16000)  # 1 second of audio
        
        processed = processor.preprocess_audio(dummy_audio)
        assert len(processed) > 0
        assert isinstance(processed, np.ndarray)


class TestClinicalProcessor:
    """Test clinical NLP functionality."""
    
    def test_clinical_processor_creation(self):
        """Test clinical processor can be created."""
        processor = create_clinical_processor()
        assert processor is not None
    
    def test_entity_extraction(self):
        """Test medical entity extraction."""
        processor = create_clinical_processor()
        
        test_text = "Patient reports chest pain and high blood pressure 140/90"
        entities = processor.ner_extractor.extract_entities(test_text)
        
        assert len(entities) > 0
        # Should find chest pain and blood pressure
        entity_texts = [e["text"].lower() for e in entities]
        assert any("chest pain" in text or "pain" in text for text in entity_texts)
    
    def test_conversation_processing(self):
        """Test full conversation processing."""
        processor = create_clinical_processor()
        
        test_conversation = """
        Doctor: How are you feeling today?
        Patient: I have been experiencing chest pain since yesterday.
        Doctor: Can you describe the pain?
        Patient: It's a sharp pain that comes and goes.
        """
        
        result = processor.process_conversation(test_conversation)
        
        assert "entities" in result
        assert "categorized_entities" in result
        assert "conversation_structure" in result


class TestSOAPGenerator:
    """Test SOAP note generation."""
    
    def test_soap_generator_creation(self):
        """Test SOAP generator can be created."""
        generator = create_soap_generator()
        assert generator is not None
    
    def test_soap_note_generation(self):
        """Test SOAP note generation from processed data."""
        generator = create_soap_generator()
        
        # Mock processed data
        processed_data = {
            "categorized_entities": {
                "symptoms": [{"text": "chest pain", "label": "SYMPTOM"}],
                "vital_signs": [{"text": "BP 140/90", "label": "VITAL_SIGN"}]
            },
            "conversation_structure": {
                "patient_statements": ["I have chest pain"],
                "doctor_statements": ["Let me examine you"]
            },
            "raw_text": "Patient reports chest pain. BP 140/90."
        }
        
        soap_note = generator.generate_soap_note(processed_data)
        
        assert "subjective" in soap_note
        assert "objective" in soap_note
        assert "assessment" in soap_note
        assert "plan" in soap_note
        
        # Check content
        assert len(soap_note["subjective"]) > 0
        assert len(soap_note["objective"]) > 0


class TestFileHandler:
    """Test file handling utilities."""
    
    def test_file_handler_creation(self):
        """Test file handler can be created."""
        handler = create_file_handler()
        assert handler is not None
    
    def test_audio_file_validation(self):
        """Test audio file validation."""
        handler = create_file_handler()
        
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"dummy audio data")
            tmp_path = tmp.name
        
        try:
            # Test validation
            is_valid = handler.validate_audio_file(tmp_path, ["wav", "mp3"])
            assert is_valid is True
            
            # Test invalid format
            is_valid = handler.validate_audio_file(tmp_path, ["mp3"])
            assert is_valid is False
            
        finally:
            os.unlink(tmp_path)


class TestDocumentExporter:
    """Test document export functionality."""
    
    def test_document_exporter_creation(self):
        """Test document exporter can be created."""
        exporter = create_document_exporter()
        assert exporter is not None
    
    def test_json_export(self):
        """Test JSON export functionality."""
        exporter = create_document_exporter()
        
        test_data = {
            "subjective": "Patient reports chest pain",
            "objective": "BP 140/90",
            "assessment": "Possible angina",
            "plan": "Order ECG"
        }
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            try:
                output_path = exporter.export_to_json(test_data, tmp.name)
                assert os.path.exists(output_path)
                
                # Check file content
                with open(output_path, 'r') as f:
                    import json
                    loaded_data = json.load(f)
                    assert "subjective" in loaded_data
                    
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)


if __name__ == "__main__":
    pytest.main([__file__])
