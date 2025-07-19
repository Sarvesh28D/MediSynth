"""
SOAP Note Generator for clinical documentation.
"""

from datetime import datetime
from typing import Dict, List, Optional



# Gemini (Google Generative AI) integration
import os
import google.generativeai as genai

class SOAPGenerator:
    """Generate SOAP (Subjective, Objective, Assessment, Plan) notes from clinical data."""
    def __init__(self, use_gemini: bool = False, gemini_api_key: str = None):
        """Initialize SOAP generator. Optionally enable Gemini LLM."""
        self.use_gemini = use_gemini
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if self.use_gemini and self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel("gemini-pro")
        else:
            self.gemini_model = None
    
    def generate_soap_note(
        self,
        processed_data: Dict,
        patient_info: Optional[Dict] = None,
        provider_info: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate complete SOAP note from processed clinical data.
        Uses Gemini LLM if enabled, otherwise falls back to rule-based.
        """
        entities = processed_data.get("categorized_entities", {})
        conversation = processed_data.get("conversation_structure", {})
        raw_text = processed_data.get("raw_text", "")

        if self.use_gemini and self.gemini_model:
            # Compose prompt for Gemini
            prompt = self._build_gemini_prompt(raw_text, entities, conversation, patient_info, provider_info)
            try:
                response = self.gemini_model.generate_content(prompt)
                gemini_soap = self._parse_gemini_response(response.text)
                gemini_soap["metadata"] = self._generate_metadata(patient_info, provider_info)
                return gemini_soap
            except Exception as e:
                # Fallback to rule-based if Gemini fails
                print(f"Gemini LLM error: {e}. Falling back to rule-based generation.")

        soap_note = {
            "subjective": self._generate_subjective(entities, conversation, raw_text),
            "objective": self._generate_objective(entities),
            "assessment": self._generate_assessment(entities, raw_text),
            "plan": self._generate_plan(entities, conversation, raw_text),
            "metadata": self._generate_metadata(patient_info, provider_info)
        }
        return soap_note

    def _build_gemini_prompt(self, raw_text, entities, conversation, patient_info, provider_info):
        """Builds a prompt for Gemini to generate a SOAP note."""
        prompt = (
            "You are a medical documentation assistant. Generate a detailed SOAP note (Subjective, Objective, Assessment, Plan) "
            "from the following doctor-patient conversation and extracted clinical entities.\n"
            f"Conversation:\n{raw_text}\n"
            f"Entities:\n{entities}\n"
            f"Patient Info: {patient_info}\nProvider Info: {provider_info}\n"
            "Format your response as JSON with keys: subjective, objective, assessment, plan."
        )
        return prompt

    def _parse_gemini_response(self, response_text):
        """Parse Gemini's response into a SOAP note dict."""
        import json
        try:
            return json.loads(response_text)
        except Exception:
            # If not valid JSON, return as a single subjective section
            return {"subjective": response_text, "objective": "", "assessment": "", "plan": ""}
    
    def _generate_subjective(
        self,
        entities: Dict[str, List],
        conversation: Dict,
        raw_text: str
    ) -> str:
        """Generate Subjective section."""
        subjective_parts = []
        
        # Chief complaint
        chief_complaint = self._extract_chief_complaint(raw_text)
        if chief_complaint:
            subjective_parts.append(f"Chief Complaint: {chief_complaint}")
        
        # Patient's reported symptoms
        symptoms = entities.get("symptoms", [])
        if symptoms:
            symptom_text = ", ".join([s["text"] for s in symptoms])
            subjective_parts.append(f"Patient reports: {symptom_text}")
        
        # History of present illness from patient statements
        patient_statements = conversation.get("patient_statements", [])
        if patient_statements:
            # Take first few relevant statements
            hpi_statements = patient_statements[:3]
            for stmt in hpi_statements:
                if len(stmt) > 20:  # Filter out very short statements
                    subjective_parts.append(stmt)
        
        return "\n".join(subjective_parts) if subjective_parts else "Patient history to be documented."
    
    def _generate_objective(self, entities: Dict[str, List]) -> str:
        """Generate Objective section."""
        objective_parts = []
        
        # Vital signs
        vital_signs = entities.get("vital_signs", [])
        if vital_signs:
            vs_text = []
            for vs in vital_signs:
                vs_text.append(vs["text"])
            objective_parts.append(f"Vital Signs: {', '.join(vs_text)}")
        
        # Physical examination findings would go here
        # For now, add placeholder for common exam findings
        objective_parts.append("Physical Examination: [To be documented during exam]")
        
        return "\n".join(objective_parts) if objective_parts else "Physical examination findings to be documented."
    
    def _generate_assessment(self, entities: Dict[str, List], raw_text: str) -> str:
        """Generate Assessment section."""
        assessment_parts = []
        
        # Identified conditions
        conditions = entities.get("conditions", [])
        if conditions:
            for condition in conditions:
                assessment_parts.append(f"• {condition['text'].title()}")
        
        # Differential diagnoses based on symptoms
        symptoms = entities.get("symptoms", [])
        if symptoms and not conditions:
            # Generate likely diagnoses based on symptoms
            symptom_text = " ".join([s["text"] for s in symptoms])
            
            if "chest pain" in symptom_text.lower():
                assessment_parts.append("• Rule out angina/coronary artery disease")
                assessment_parts.append("• Consider musculoskeletal chest pain")
            elif "headache" in symptom_text.lower():
                assessment_parts.append("• Tension headache")
                assessment_parts.append("• Rule out migraine")
            elif "abdominal pain" in symptom_text.lower():
                assessment_parts.append("• Abdominal pain, etiology to be determined")
                assessment_parts.append("• Consider gastritis or gastroenteritis")
        
        if not assessment_parts:
            assessment_parts.append("Clinical assessment pending further evaluation")
        
        return "\n".join(assessment_parts)
    
    def _generate_plan(
        self,
        entities: Dict[str, List],
        conversation: Dict,
        raw_text: str
    ) -> str:
        """Generate Plan section."""
        plan_parts = []
        
        # Diagnostic tests/procedures mentioned
        procedures = entities.get("procedures", [])
        if procedures:
            plan_parts.append("Diagnostic Studies:")
            for proc in procedures:
                plan_parts.append(f"• Order {proc['text']}")
        
        # Medications mentioned
        medications = entities.get("medications", [])
        if medications:
            plan_parts.append("Medications:")
            for med in medications:
                plan_parts.append(f"• {med['text'].title()}")
        
        # Follow-up instructions from doctor statements
        doctor_statements = conversation.get("doctor_statements", [])
        followup_keywords = ["follow up", "come back", "return", "appointment", "see you"]
        
        for statement in doctor_statements:
            if any(keyword in statement.lower() for keyword in followup_keywords):
                plan_parts.append(f"Follow-up: {statement}")
                break
        
        # Add standard follow-up if none mentioned
        if not any("follow" in part.lower() for part in plan_parts):
            plan_parts.append("Follow-up: As needed or if symptoms worsen")
        
        return "\n".join(plan_parts) if plan_parts else "Treatment plan to be determined."
    
    def _extract_chief_complaint(self, text: str) -> Optional[str]:
        """Extract chief complaint from raw text."""
        # Look for first mention of patient's main concern
        lines = text.split('.')
        
        for line in lines[:5]:  # Check first few sentences
            line_lower = line.lower().strip()
            
            # Common chief complaint indicators
            if any(phrase in line_lower for phrase in [
                "i have", "i feel", "i'm experiencing", "my", "the pain",
                "it hurts", "since", "started", "complains of"
            ]):
                return line.strip()
        
        return None
    
    def _generate_metadata(
        self,
        patient_info: Optional[Dict],
        provider_info: Optional[Dict]
    ) -> Dict:
        """Generate metadata for the SOAP note."""
        metadata = {
            "generated_date": datetime.now().isoformat(),
            "note_type": "SOAP Note",
            "generated_by": "MediSynth AI Assistant"
        }
        
        if patient_info:
            metadata.update(patient_info)
        
        if provider_info:
            metadata.update(provider_info)
        
        return metadata
    
    def format_soap_note(self, soap_data: Dict[str, str]) -> str:
        """
        Format SOAP note as readable text.
        
        Args:
            soap_data: SOAP note dictionary
            
        Returns:
            Formatted SOAP note as string
        """
        formatted_note = []
        
        # Header
        metadata = soap_data.get("metadata", {})
        formatted_note.append("=" * 50)
        formatted_note.append("CLINICAL SOAP NOTE")
        formatted_note.append("=" * 50)
        formatted_note.append(f"Generated: {metadata.get('generated_date', 'N/A')}")
        formatted_note.append(f"Provider: {metadata.get('provider_name', 'N/A')}")
        formatted_note.append("")
        
        # SOAP sections
        sections = [
            ("SUBJECTIVE", soap_data.get("subjective", "")),
            ("OBJECTIVE", soap_data.get("objective", "")),
            ("ASSESSMENT", soap_data.get("assessment", "")),
            ("PLAN", soap_data.get("plan", ""))
        ]
        
        for section_name, section_content in sections:
            formatted_note.append(f"{section_name}:")
            formatted_note.append("-" * len(section_name))
            formatted_note.append(section_content)
            formatted_note.append("")
        
        return "\n".join(formatted_note)


# Factory function
def create_soap_generator() -> SOAPGenerator:
    """
    Factory function to create a SOAP generator.
    
    Returns:
        Configured SOAPGenerator instance
    """
    return SOAPGenerator()
