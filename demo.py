"""
Enhanced demo version of MediSynth Agent with modern UI animations.
"""

import streamlit as st
import tempfile
import os
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Enhanced mock classes for testing with realistic animations
class MockASRProcessor:
    def __init__(self, model_size="base", device="cpu"):
        self.model_size = model_size
        self.device = device
    
    def transcribe(self, audio_path, language="en"):
        # Simulate processing with progress
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)  # Simulate processing time
            progress_bar.progress(i + 1)
        
        # Mock transcription result with realistic medical conversation
        return {
            "text": "Good morning doctor. I've been having chest pain since last night. It started around 10 PM and it's been bothering me. The pain is sharp and comes and goes. Sometimes it's worse when I take a deep breath. I also felt a bit nauseous this morning and had trouble sleeping."
        }
    
    def get_confidence_score(self, result):
        return 0.87

class MockClinicalProcessor:
    def process_conversation(self, text):
        # Simulate processing with progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, stage in enumerate(["Analyzing text...", "Extracting entities...", "Categorizing findings..."]):
            status_text.text(stage)
            for j in range(33):
                time.sleep(0.005)
                progress_bar.progress(i * 33 + j + 1)
        
        # Enhanced mock entity extraction
        entities = [
            {"text": "chest pain", "label": "SYMPTOM", "confidence": 0.92, "start": 45, "end": 55},
            {"text": "nauseous", "label": "SYMPTOM", "confidence": 0.85, "start": 150, "end": 158},
            {"text": "sharp pain", "label": "SYMPTOM", "confidence": 0.88, "start": 80, "end": 90},
            {"text": "trouble sleeping", "label": "SYMPTOM", "confidence": 0.78, "start": 170, "end": 186},
            {"text": "deep breath", "label": "VITAL_SIGN", "confidence": 0.75, "start": 120, "end": 131}
        ]
        
        categorized = {
            "symptoms": entities,
            "vital_signs": [],
            "medications": [],
            "conditions": [],
            "procedures": []
        }
        
        conversation_structure = {
            "patient_statements": [
                "I've been having chest pain since last night",
                "The pain is sharp and comes and goes",
                "I also felt a bit nauseous this morning"
            ],
            "doctor_statements": [
                "Good morning. What brings you in today?",
                "Can you describe the pain?"
            ]
        }
        
        return {
            "entities": entities,
            "categorized_entities": categorized,
            "conversation_structure": conversation_structure,
            "raw_text": text
        }

class MockSOAPGenerator:
    def generate_soap_note(self, processed_data, patient_info=None, provider_info=None):
        return {
            "subjective": "Chief Complaint: Chest pain since last night\nPatient reports sharp chest pain that started around 10 PM yesterday. Pain is intermittent and worsens with deep breathing. Patient also experienced nausea this morning.",
            
            "objective": "Vital Signs: [To be documented]\nPhysical Examination: [To be documented during exam]",
            
            "assessment": "• Rule out angina/coronary artery disease\n• Consider musculoskeletal chest pain\n• Gastroesophageal reflux possible given nausea",
            
            "plan": "Diagnostic Studies:\n• Order ECG\n• Consider chest X-ray\n\nMedications:\n• Consider antacid trial\n\nFollow-up: Return if symptoms worsen or if new symptoms develop",
            
            "metadata": {
                "generated_date": datetime.now().isoformat(),
                "generated_by": "MediSynth AI Assistant"
            }
        }
    
    def format_soap_note(self, soap_data):
        formatted = []
        formatted.append("=" * 50)
        formatted.append("CLINICAL SOAP NOTE")
        formatted.append("=" * 50)
        formatted.append(f"Generated: {soap_data.get('metadata', {}).get('generated_date', 'N/A')}")
        formatted.append("")
        
        sections = [
            ("SUBJECTIVE", soap_data.get("subjective", "")),
            ("OBJECTIVE", soap_data.get("objective", "")),
            ("ASSESSMENT", soap_data.get("assessment", "")),
            ("PLAN", soap_data.get("plan", ""))
        ]
        
        for section_name, section_content in sections:
            formatted.append(f"{section_name}:")
            formatted.append("-" * len(section_name))
            formatted.append(section_content)
            formatted.append("")
        
        return "\n".join(formatted)

def main():
    st.set_page_config(
        page_title="MediSynth Agent - Demo",
        page_icon="🩺",
        layout="wide"
    )
    
    st.title("🩺 MediSynth Agent - Demo Version")
    st.markdown("""
    **AI-Powered Clinical Documentation Assistant**
    
    This is a demonstration version showing the core functionality.
    Upload an audio file to see how the system processes doctor-patient conversations.
    """)
    
    # Initialize session state
    if 'transcription' not in st.session_state:
        st.session_state.transcription = ""
    if 'entities' not in st.session_state:
        st.session_state.entities = []
    if 'soap_note' not in st.session_state:
        st.session_state.soap_note = {}
    
    # Initialize mock processors
    asr_processor = MockASRProcessor()
    clinical_processor = MockClinicalProcessor()
    soap_generator = MockSOAPGenerator()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.write("**Demo Mode Active**")
        st.write("Using mock data for demonstration")
        
        st.divider()
        
        st.header("👤 Patient Information")
        patient_name = st.text_input("Patient Name (Optional)")
        patient_id = st.text_input("Patient ID (Optional)")
        
        st.header("👨‍⚕️ Provider Information")
        provider_name = st.text_input("Provider Name (Optional)")
    
    # Main content
    st.header("🎤 Audio Input")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file (Demo will use sample data)",
        type=["wav", "mp3", "m4a"],
        help="In demo mode, any uploaded file will trigger sample processing"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        st.info("🔄 Processing with sample medical conversation...")
        
        # Process transcription
        with st.spinner("🎯 Transcribing audio..."):
            result = asr_processor.transcribe("dummy_path")
            st.session_state.transcription = result["text"]
            confidence = asr_processor.get_confidence_score(result)
        
        st.success(f"✅ Transcription completed! Confidence: {confidence:.2%}")
        
        # Process NLP
        with st.spinner("🧠 Analyzing clinical content..."):
            processed_data = clinical_processor.process_conversation(st.session_state.transcription)
            st.session_state.entities = processed_data["entities"]
            
            # Generate SOAP note
            soap_note = soap_generator.generate_soap_note(
                processed_data,
                patient_info={"name": patient_name, "id": patient_id},
                provider_info={"name": provider_name}
            )
            st.session_state.soap_note = soap_note
        
        st.success("✅ Clinical analysis completed!")
    
    # Display results
    if st.session_state.transcription:
        st.divider()
        st.header("📝 Transcription")
        st.text_area(
            "Transcribed conversation:",
            value=st.session_state.transcription,
            height=150,
            disabled=True
        )
        
        # Entity analysis
        if st.session_state.entities:
            st.divider()
            st.header("🔍 Medical Entity Analysis")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("📊 Detected Entities")
                for entity in st.session_state.entities:
                    st.metric(
                        entity["label"].replace("_", " ").title(),
                        entity["text"],
                        f"{entity['confidence']:.1%}"
                    )
            
            with col2:
                st.subheader("🎯 Highlighted Text")
                highlighted_text = st.session_state.transcription
                
                # Simple highlighting
                for entity in st.session_state.entities:
                    text = entity["text"]
                    highlighted_text = highlighted_text.replace(
                        text, 
                        f'<mark style="background-color: #ffcccb; padding: 2px 4px; border-radius: 3px;">{text}</mark>'
                    )
                
                st.markdown(highlighted_text, unsafe_allow_html=True)
        
        # SOAP Note
        if st.session_state.soap_note:
            st.divider()
            st.header("📋 Generated SOAP Note")
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                ["📝 Subjective", "🔬 Objective", "🎯 Assessment", "📋 Plan", "📄 Full Note"]
            )
            
            with tab1:
                st.text_area(
                    "Subjective:",
                    value=st.session_state.soap_note.get("subjective", ""),
                    height=150
                )
            
            with tab2:
                st.text_area(
                    "Objective:",
                    value=st.session_state.soap_note.get("objective", ""),
                    height=150
                )
            
            with tab3:
                st.text_area(
                    "Assessment:",
                    value=st.session_state.soap_note.get("assessment", ""),
                    height=150
                )
            
            with tab4:
                st.text_area(
                    "Plan:",
                    value=st.session_state.soap_note.get("plan", ""),
                    height=150
                )
            
            with tab5:
                formatted_note = soap_generator.format_soap_note(st.session_state.soap_note)
                st.text(formatted_note)
                
                # Download functionality
                st.download_button(
                    label="📥 Download SOAP Note",
                    data=formatted_note,
                    file_name=f"soap_note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    # Footer
    st.divider()
    st.markdown("""
    **MediSynth Agent Demo** - This demonstration shows the core workflow of the system.
    
    **Next Steps for Full Implementation:**
    - Install complete dependencies (whisper, transformers, etc.)
    - Integrate real ASR models
    - Add medical NER models
    - Implement audio recording functionality
    - Add export to PDF
    - Deploy for production use
    
    ⚠️ **For educational/research purposes only**
    """)

if __name__ == "__main__":
    main()
