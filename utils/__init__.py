"""
Utility functions for file handling, formatting, and logging.
"""

import json
import logging
import os
import platform
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


class FileHandler:
    """Handle file operations for audio and document processing."""
    
    @staticmethod
    def save_uploaded_file(uploaded_file, upload_dir: str = "temp") -> str:
        """
        Save uploaded file to temporary directory.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            upload_dir: Directory to save file
            
        Returns:
            Path to saved file
        """
        # Create upload directory if it doesn't exist
        Path(upload_dir).mkdir(exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{uploaded_file.name}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    
    @staticmethod
    def clean_temp_files(directory: str = "temp", max_age_hours: int = 24) -> None:
        """
        Clean up old temporary files.
        
        Args:
            directory: Directory to clean
            max_age_hours: Maximum age of files to keep
        """
        if not os.path.exists(directory):
            return
        
        current_time = datetime.now()
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                age_hours = (current_time - file_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    try:
                        os.remove(file_path)
                        print(f"Removed old temp file: {filename}")
                    except Exception as e:
                        print(f"Error removing file {filename}: {e}")
    
    @staticmethod
    def validate_audio_file(file_path: str, allowed_formats: list) -> bool:
        """
        Validate audio file format and size.
        
        Args:
            file_path: Path to audio file
            allowed_formats: List of allowed file extensions
            
        Returns:
            True if file is valid
        """
        # Check file extension
        file_ext = Path(file_path).suffix.lower().lstrip('.')
        if file_ext not in allowed_formats:
            return False
        
        # Check file exists and has content
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return False
        
        return True


class DocumentExporter:
    """Export SOAP notes and clinical data to various formats."""
    
    def __init__(self):
        """Initialize document exporter."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self) -> None:
        """Setup custom paragraph styles for medical documents."""
        self.styles.add(ParagraphStyle(
            name='SOAPHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            textColor='darkblue'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SOAPSection',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            textColor='black',
            fontName='Helvetica-Bold'
        ))
    
    def export_to_pdf(
        self,
        soap_note: Dict[str, str],
        output_path: str,
        patient_info: Optional[Dict] = None
    ) -> str:
        """
        Export SOAP note to PDF format.
        
        Args:
            soap_note: SOAP note dictionary
            output_path: Output file path
            patient_info: Optional patient information
            
        Returns:
            Path to generated PDF file
        """
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("Clinical SOAP Note", self.styles['SOAPHeader'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Metadata
        metadata = soap_note.get('metadata', {})
        if metadata:
            date_para = Paragraph(
                f"<b>Date:</b> {metadata.get('generated_date', 'N/A')[:10]}",
                self.styles['Normal']
            )
            story.append(date_para)
            
            if patient_info:
                patient_para = Paragraph(
                    f"<b>Patient:</b> {patient_info.get('name', 'N/A')}",
                    self.styles['Normal']
                )
                story.append(patient_para)
            
            story.append(Spacer(1, 12))
        
        # SOAP sections
        sections = [
            ('SUBJECTIVE', soap_note.get('subjective', '')),
            ('OBJECTIVE', soap_note.get('objective', '')),
            ('ASSESSMENT', soap_note.get('assessment', '')),
            ('PLAN', soap_note.get('plan', ''))
        ]
        
        for section_name, section_content in sections:
            # Section header
            header = Paragraph(section_name, self.styles['SOAPSection'])
            story.append(header)
            
            # Section content
            content = Paragraph(
                section_content.replace('\n', '<br/>'),
                self.styles['Normal']
            )
            story.append(content)
            story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def export_to_json(
        self,
        data: Dict[str, Any],
        output_path: str,
        include_metadata: bool = True
    ) -> str:
        """
        Export clinical data to JSON format.
        
        Args:
            data: Clinical data dictionary
            output_path: Output file path
            include_metadata: Include processing metadata
            
        Returns:
            Path to generated JSON file
        """
        export_data = data.copy()
        
        if include_metadata:
            export_data['export_metadata'] = {
                'exported_at': datetime.now().isoformat(),
                'exported_by': 'MediSynth Agent',
                'format_version': '1.0'
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return output_path


class Logger:
    """Custom logger for MediSynth application."""
    
    def __init__(self, name: str = "medisynth", log_level: str = "INFO"):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create console handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)


class TextFormatter:
    """Format and clean text for display and processing."""
    
    @staticmethod
    def clean_transcription(text: str) -> str:
        """
        Clean transcription text for better readability.
        
        Args:
            text: Raw transcription text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Add periods after sentences that don't have punctuation
        sentences = text.split('.')
        cleaned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not sentence.endswith(('.', '!', '?')):
                sentence += '.'
            if sentence:
                cleaned_sentences.append(sentence)
        
        return ' '.join(cleaned_sentences)
    
    @staticmethod
    def highlight_entities(text: str, entities: list) -> str:
        """
        Add HTML highlighting to entities in text.
        
        Args:
            text: Original text
            entities: List of entity dictionaries
            
        Returns:
            Text with HTML highlighting
        """
        # Sort entities by start position (reverse order for replacement)
        sorted_entities = sorted(entities, key=lambda x: x['start'], reverse=True)
        
        highlighted_text = text
        
        for entity in sorted_entities:
            start = entity['start']
            end = entity['end']
            entity_text = entity['text']
            label = entity['label']
            
            # Create highlighted span
            highlighted_span = f'<mark title="{label}">{entity_text}</mark>'
            
            # Replace in text
            highlighted_text = (
                highlighted_text[:start] + 
                highlighted_span + 
                highlighted_text[end:]
            )
        
        return highlighted_text


# Factory functions
def create_file_handler() -> FileHandler:
    """Create a file handler instance."""
    return FileHandler()

def create_document_exporter() -> DocumentExporter:
    """Create a document exporter instance."""
    return DocumentExporter()

def create_logger(name: str = "medisynth", level: str = "INFO") -> Logger:
    """Create a logger instance."""
    return Logger(name, level)
