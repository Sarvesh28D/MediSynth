"""
Medical Natural Language Processing module for entity extraction and clinical text analysis.

This module uses medical-domain NLP models to extract clinical entities from transcribed text
and prepare data for SOAP note generation.
"""

import re
from typing import Dict, List, Optional, Tuple, Union

import spacy
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    pipeline
)


class MedicalNERExtractor:
    """Medical Named Entity Recognition extractor using domain-specific models."""
    
    def __init__(self, model_name: str = "d4data/biomedical-ner-all"):
        """
        Initialize medical NER extractor.
        
        Args:
            model_name: HuggingFace model for biomedical NER
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.ner_pipeline = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the biomedical NER model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_name)
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple"
            )
            print(f"Loaded biomedical NER model: {self.model_name}")
        except Exception as e:
            print(f"Error loading NER model: {e}")
            print("Falling back to basic pattern matching...")
            self.ner_pipeline = None
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract medical entities from text.
        
        Args:
            text: Input clinical text
            
        Returns:
            List of extracted entities with labels and positions
        """
        entities = []
        
        if self.ner_pipeline:
            # Use transformer-based NER
            try:
                ner_results = self.ner_pipeline(text)
                for entity in ner_results:
                    entities.append({
                        "text": entity["word"].replace("##", ""),
                        "label": entity["entity_group"],
                        "confidence": entity["score"],
                        "start": entity["start"],
                        "end": entity["end"]
                    })
            except Exception as e:
                print(f"Error in NER extraction: {e}")
                # Fall back to pattern matching
                entities = self._pattern_based_extraction(text)
        else:
            # Use pattern-based extraction as fallback
            entities = self._pattern_based_extraction(text)
        
        return entities
    
    def _pattern_based_extraction(self, text: str) -> List[Dict]:
        """
        Fallback pattern-based entity extraction.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        # Medical patterns
        patterns = {
            "SYMPTOM": [
                r'\b(?:pain|ache|hurt|sore|tender|discomfort|burning|throbbing|sharp|dull|cramping)\b',
                r'\b(?:nausea|vomiting|dizziness|fatigue|weakness|tired|exhausted)\b',
                r'\b(?:fever|chills|sweating|headache|migraine)\b',
                r'\b(?:shortness of breath|SOB|dyspnea|wheezing|cough|congestion)\b',
                r'\b(?:chest pain|abdominal pain|back pain|joint pain)\b'
            ],
            "VITAL_SIGN": [
                r'\b(?:BP|blood pressure)\s*:?\s*(\d{2,3}\/\d{2,3})\b',
                r'\b(?:heart rate|HR|pulse)\s*:?\s*(\d{2,3})\s*(?:bpm)?\b',
                r'\b(?:temperature|temp)\s*:?\s*(\d{2,3}\.?\d?)\s*(?:°F|°C|F|C)?\b',
                r'\b(?:respiratory rate|RR)\s*:?\s*(\d{1,2})\b',
                r'\b(?:oxygen saturation|O2 sat|SpO2)\s*:?\s*(\d{2,3})%?\b'
            ],
            "MEDICATION": [
                r'\b(?:aspirin|ibuprofen|acetaminophen|tylenol|advil|motrin)\b',
                r'\b(?:atenolol|metoprolol|lisinopril|amlodipine|losartan)\b',
                r'\b(?:metformin|insulin|glipizide|glyburide)\b',
                r'\b(?:simvastatin|atorvastatin|pravastatin)\b',
                r'\b(?:omeprazole|lansoprazole|pantoprazole)\b'
            ],
            "CONDITION": [
                r'\b(?:hypertension|high blood pressure|HTN)\b',
                r'\b(?:diabetes|DM|diabetic)\b',
                r'\b(?:angina|chest pain|CAD|coronary artery disease)\b',
                r'\b(?:asthma|COPD|bronchitis)\b',
                r'\b(?:arthritis|osteoarthritis|rheumatoid arthritis)\b'
            ],
            "PROCEDURE": [
                r'\b(?:ECG|EKG|electrocardiogram)\b',
                r'\b(?:X-ray|radiograph|CT scan|MRI|ultrasound)\b',
                r'\b(?:blood test|lab work|CBC|BMP|lipid panel)\b'
            ]
        }
        
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        "text": match.group(0),
                        "label": entity_type,
                        "confidence": 0.8,  # Static confidence for pattern matching
                        "start": match.start(),
                        "end": match.end()
                    })
        
        return entities


class ClinicalTextProcessor:
    """Process clinical text and extract structured information."""
    
    def __init__(self):
        """Initialize clinical text processor."""
        self.ner_extractor = MedicalNERExtractor()
    
    def process_conversation(self, transcription: str) -> Dict:
        """
        Process doctor-patient conversation transcript.
        
        Args:
            transcription: Full conversation transcript
            
        Returns:
            Structured clinical information
        """
        # Extract entities
        entities = self.ner_extractor.extract_entities(transcription)
        
        # Categorize entities
        categorized = self._categorize_entities(entities)
        
        # Extract conversation structure
        conversation_structure = self._analyze_conversation_structure(transcription)
        
        return {
            "entities": entities,
            "categorized_entities": categorized,
            "conversation_structure": conversation_structure,
            "raw_text": transcription
        }
    
    def _categorize_entities(self, entities: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize extracted entities by type.
        
        Args:
            entities: List of extracted entities
            
        Returns:
            Dictionary with categorized entities
        """
        categories = {
            "symptoms": [],
            "vital_signs": [],
            "medications": [],
            "conditions": [],
            "procedures": []
        }
        
        for entity in entities:
            label = entity["label"].upper()
            
            if "SYMPTOM" in label:
                categories["symptoms"].append(entity)
            elif "VITAL" in label:
                categories["vital_signs"].append(entity)
            elif "MEDICATION" in label or "DRUG" in label:
                categories["medications"].append(entity)
            elif "CONDITION" in label or "DISEASE" in label:
                categories["conditions"].append(entity)
            elif "PROCEDURE" in label:
                categories["procedures"].append(entity)
        
        return categories
    
    def _analyze_conversation_structure(self, text: str) -> Dict:
        """
        Analyze conversation structure to identify speaker turns.
        
        Args:
            text: Conversation transcript
            
        Returns:
            Dictionary with conversation analysis
        """
        # Simple heuristics for speaker identification
        lines = text.split('\n')
        
        doctor_indicators = [
            "doctor", "dr", "physician", "let me", "i'm going to", "we need to",
            "i recommend", "take this medication", "come back", "follow up"
        ]
        
        patient_indicators = [
            "i feel", "i have", "it hurts", "since yesterday", "it started",
            "i'm experiencing", "i can't", "i've been"
        ]
        
        conversation = {
            "doctor_statements": [],
            "patient_statements": [],
            "total_turns": len(lines)
        }
        
        for line in lines:
            line_lower = line.lower()
            
            if any(indicator in line_lower for indicator in doctor_indicators):
                conversation["doctor_statements"].append(line.strip())
            elif any(indicator in line_lower for indicator in patient_indicators):
                conversation["patient_statements"].append(line.strip())
        
        return conversation
    
    def extract_chief_complaint(self, text: str) -> str:
        """
        Extract the chief complaint from conversation.
        
        Args:
            text: Conversation text
            
        Returns:
            Identified chief complaint
        """
        # Look for common chief complaint patterns
        cc_patterns = [
            r"chief complaint[:\s]+([^\.]+)",
            r"patient (?:reports|states|complains of)[:\s]+([^\.]+)",
            r"i (?:have|feel|am experiencing)[:\s]+([^\.]+)",
            r"the (?:main )?(?:problem|issue|concern) is[:\s]+([^\.]+)"
        ]
        
        for pattern in cc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: look for first symptom mentioned
        entities = self.ner_extractor.extract_entities(text)
        symptoms = [e for e in entities if "SYMPTOM" in e["label"].upper()]
        
        if symptoms:
            return symptoms[0]["text"]
        
        return "Not clearly specified"


# Factory function
def create_clinical_processor() -> ClinicalTextProcessor:
    """
    Factory function to create a clinical text processor.
    
    Returns:
        Configured ClinicalTextProcessor instance
    """
    return ClinicalTextProcessor()
