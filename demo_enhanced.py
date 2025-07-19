"""
Enhanced demo version of MediSynth Agent with modern UI.
"""

import streamlit as st
import tempfile
import os
import time
import json
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="MediSynth Agent Demo",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS styling
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Styles */
.main {
    font-family: 'Inter', sans-serif;
}

/* Custom Header */
.header-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    animation: slideInDown 0.8s ease-out;
}

.header-title {
    color: white;
    font-size: 3rem;
    font-weight: 700;
    text-align: center;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.header-subtitle {
    color: rgba(255,255,255,0.9);
    font-size: 1.2rem;
    text-align: center;
    margin-top: 0.5rem;
    font-weight: 300;
}

/* Animated Cards */
.feature-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    border: 1px solid #e1e8ed;
    transition: all 0.3s ease;
    animation: fadeInUp 0.6s ease-out;
    margin-bottom: 1rem;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
}

/* Entity Pills */
.entity-pill {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    margin: 0.25rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
    animation: bounceIn 0.5s ease-out;
}

.entity-symptom {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeaa7;
}

.entity-vital {
    background-color: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
}

/* SOAP Note Styling */
.soap-section {
    background: #f8f9fa;
    padding: 1rem;
    border-left: 4px solid #667eea;
    margin: 1rem 0;
    border-radius: 0 8px 8px 0;
}

.soap-header {
    font-weight: 600;
    color: #667eea;
    margin-bottom: 0.5rem;
}

/* Success Messages */
.success-message {
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    animation: slideInDown 0.5s ease-out;
    margin: 1rem 0;
}

/* Animations */
@keyframes slideInDown {
    from {
        transform: translateY(-100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes fadeInUp {
    from {
        transform: translateY(30px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes bounceIn {
    0% {
        transform: scale(0.3);
        opacity: 0;
    }
    50% {
        transform: scale(1.05);
    }
    70% {
        transform: scale(0.9);
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}

/* Buttons */
.stButton > button {
    border-radius: 25px;
    border: none;
    padding: 0.5rem 2rem;
    font-weight: 600;
    transition: all 0.3s ease;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# Mock classes with animations
class MockASRProcessor:
    def __init__(self, model_size="base", device="cpu"):
        self.model_size = model_size
        self.device = device
    
    def transcribe(self, audio_path, language="en"):
        # Simulate processing with progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stages = ["Loading audio...", "Processing speech...", "Generating text..."]
        for i, stage in enumerate(stages):
            status_text.text(f"🔄 {stage}")
            for j in range(33):
                time.sleep(0.01)
                progress_bar.progress(i * 33 + j + 1)
        
        status_text.empty()
        progress_bar.empty()
        
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
        
        stages = ["Analyzing text...", "Extracting entities...", "Categorizing findings..."]
        for i, stage in enumerate(stages):
            status_text.text(f"🧠 {stage}")
            for j in range(33):
                time.sleep(0.01)
                progress_bar.progress(i * 33 + j + 1)
        
        status_text.empty()
        progress_bar.empty()
        
        entities = [
            {"text": "chest pain", "label": "SYMPTOM", "confidence": 0.92, "start": 45, "end": 55},
            {"text": "nauseous", "label": "SYMPTOM", "confidence": 0.85, "start": 150, "end": 158},
            {"text": "sharp pain", "label": "SYMPTOM", "confidence": 0.88, "start": 80, "end": 90},
            {"text": "trouble sleeping", "label": "SYMPTOM", "confidence": 0.78, "start": 170, "end": 186},
            {"text": "deep breath", "label": "VITAL_SIGN", "confidence": 0.75, "start": 120, "end": 131}
        ]
        
        return {
            "entities": entities,
            "categorized": {
                "symptoms": [e for e in entities if e["label"] == "SYMPTOM"],
                "vital_signs": [e for e in entities if e["label"] == "VITAL_SIGN"],
                "medications": [],
                "conditions": [],
                "procedures": []
            }
        }

class MockSOAPGenerator:
    def generate_soap_note(self, transcription, entities):
        # Simulate processing
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            status_text.text(f"📝 Generating SOAP note... {i+1}%")
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        
        status_text.empty()
        progress_bar.empty()
        
        return {
            "subjective": """Chief Complaint: Chest pain since last night

Patient reports experiencing chest pain that began around 10 PM yesterday evening. The pain is described as sharp in nature and occurs intermittently. Patient notes that the pain worsens with deep inspiration. Additionally, patient experienced nausea this morning and reports difficulty sleeping overnight.""",
            
            "objective": """Vital Signs: [To be documented during physical examination]
Physical Examination: [To be completed during encounter]
Patient appears alert and oriented, speaking in full sentences without apparent distress at rest.""",
            
            "assessment": """Primary Assessment:
• Acute chest pain, etiology to be determined
• Rule out cardiac causes (angina, myocardial infarction)
• Consider musculoskeletal etiology
• Anxiety-related chest pain possible

Differential Diagnosis:
• Coronary artery disease
• Costochondritis
• Gastroesophageal reflux disease
• Panic disorder""",
            
            "plan": """Diagnostic Studies:
• 12-lead ECG
• Basic metabolic panel
• Troponin I levels
• Chest X-ray

Treatment:
• Monitor vital signs
• Consider nitroglycerin trial if cardiac etiology suspected
• Pain management as appropriate

Follow-up:
• Return immediately if symptoms worsen
• Cardiology consultation if abnormal findings
• Primary care follow-up in 1-2 days"""
        }
    
    def format_soap_note(self, soap_note):
        return f"""SOAP NOTE
=========

SUBJECTIVE:
-----------
{soap_note['subjective']}

OBJECTIVE:
----------
{soap_note['objective']}

ASSESSMENT:
-----------
{soap_note['assessment']}

PLAN:
-----
{soap_note['plan']}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

# Initialize session state
if 'transcription' not in st.session_state:
    st.session_state.transcription = ""
if 'entities' not in st.session_state:
    st.session_state.entities = []
if 'soap_note' not in st.session_state:
    st.session_state.soap_note = {}
if 'demo_step' not in st.session_state:
    st.session_state.demo_step = 1

# Initialize processors
asr = MockASRProcessor()
nlp = MockClinicalProcessor()
soap = MockSOAPGenerator()

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🩺 MediSynth Agent</h1>
    <p class="header-subtitle">Enhanced AI-Powered Clinical Documentation Demo</p>
</div>
""", unsafe_allow_html=True)

# Feature cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #667eea; margin: 0;">🎤 Audio Input</h3>
        <p style="margin: 0.5rem 0 0 0; color: #6c757d;">Upload or Record</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #667eea; margin: 0;">🗣️ Speech-to-Text</h3>
        <p style="margin: 0.5rem 0 0 0; color: #6c757d;">AI Transcription</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #667eea; margin: 0;">🧠 Medical NLP</h3>
        <p style="margin: 0.5rem 0 0 0; color: #6c757d;">Entity Extraction</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #667eea; margin: 0;">📝 SOAP Notes</h3>
        <p style="margin: 0.5rem 0 0 0; color: #6c757d;">Auto Generation</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Demo workflow
st.header("🎭 Interactive Demo")

# Step 1: Audio Input Simulation
st.markdown("""
<div class="feature-card">
    <h3 style="color: #667eea; margin-bottom: 1rem;">🎤 Step 1: Audio Input</h3>
</div>
""", unsafe_allow_html=True)

st.info("💡 **Demo Mode**: Click the button below to simulate uploading a medical conversation audio file.")

if st.button("🎵 Simulate Audio Upload", type="primary", use_container_width=True):
    st.session_state.demo_step = 2
    st.markdown("""
    <div class="success-message">
        ✅ Audio file uploaded successfully! 
        Sample: doctor-patient-consultation.wav (2:34 duration)
    </div>
    """, unsafe_allow_html=True)

# Step 2: Transcription
if st.session_state.demo_step >= 2:
    st.divider()
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #667eea; margin-bottom: 1rem;">🗣️ Step 2: Speech-to-Text Transcription</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Start Transcription", type="primary", use_container_width=True):
        with st.container():
            result = asr.transcribe("demo_audio.wav")
            st.session_state.transcription = result["text"]
            st.session_state.demo_step = 3
            
            st.markdown("""
            <div class="success-message">
                ✅ Transcription completed with 87% confidence!
            </div>
            """, unsafe_allow_html=True)
    
    # Show transcription if available
    if st.session_state.transcription:
        st.subheader("📄 Transcribed Text")
        st.text_area("", value=st.session_state.transcription, height=100, disabled=True)

# Step 3: Entity Extraction
if st.session_state.demo_step >= 3:
    st.divider()
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #667eea; margin-bottom: 1rem;">🧠 Step 3: Medical Entity Extraction</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Extract Medical Entities", type="primary", use_container_width=True):
        with st.container():
            result = nlp.process_conversation(st.session_state.transcription)
            st.session_state.entities = result["entities"]
            st.session_state.demo_step = 4
            
            st.markdown("""
            <div class="success-message">
                ✅ Medical entities extracted successfully!
            </div>
            """, unsafe_allow_html=True)
    
    # Show entities if available
    if st.session_state.entities:
        st.subheader("🏷️ Detected Medical Entities")
        
        # Group entities by type
        symptoms = [e for e in st.session_state.entities if e["label"] == "SYMPTOM"]
        vitals = [e for e in st.session_state.entities if e["label"] == "VITAL_SIGN"]
        
        if symptoms:
            st.markdown("**Symptoms:**")
            pills_html = ""
            for entity in symptoms:
                pills_html += f"""
                <span class="entity-pill entity-symptom" title="Confidence: {entity['confidence']:.2%}">
                    {entity['text']}
                </span>
                """
            st.markdown(pills_html, unsafe_allow_html=True)
        
        if vitals:
            st.markdown("**Vital Signs:**")
            pills_html = ""
            for entity in vitals:
                pills_html += f"""
                <span class="entity-pill entity-vital" title="Confidence: {entity['confidence']:.2%}">
                    {entity['text']}
                </span>
                """
            st.markdown(pills_html, unsafe_allow_html=True)

# Step 4: SOAP Note Generation
if st.session_state.demo_step >= 4:
    st.divider()
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #667eea; margin-bottom: 1rem;">📝 Step 4: SOAP Note Generation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📋 Generate SOAP Note", type="primary", use_container_width=True):
        with st.container():
            soap_note = soap.generate_soap_note(st.session_state.transcription, st.session_state.entities)
            st.session_state.soap_note = soap_note
            st.session_state.demo_step = 5
            
            st.markdown("""
            <div class="success-message">
                ✅ SOAP note generated successfully!
            </div>
            """, unsafe_allow_html=True)
    
    # Show SOAP note if available
    if st.session_state.soap_note:
        st.subheader("📋 Generated SOAP Note")
        
        # Display each section
        sections = [
            ("subjective", "📝 SUBJECTIVE", "#667eea"),
            ("objective", "🔬 OBJECTIVE", "#28a745"),
            ("assessment", "🎯 ASSESSMENT", "#ffc107"),
            ("plan", "📋 PLAN", "#dc3545")
        ]
        
        for key, title, color in sections:
            st.markdown(f"""
            <div class="soap-section">
                <div class="soap-header">{title}</div>
            </div>
            """, unsafe_allow_html=True)
            st.text_area("", value=st.session_state.soap_note.get(key, ""), height=100, disabled=True, key=f"soap_{key}")

# Step 5: Export Options
if st.session_state.demo_step >= 5:
    st.divider()
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #667eea; margin-bottom: 1rem;">💾 Step 5: Export Documentation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export PDF", type="primary", use_container_width=True):
            st.success("✅ PDF export simulated!")
            
    with col2:
        if st.button("📊 Export JSON", type="secondary", use_container_width=True):
            export_data = {
                "transcription": st.session_state.transcription,
                "entities": st.session_state.entities,
                "soap_note": st.session_state.soap_note,
                "timestamp": datetime.now().isoformat()
            }
            st.json(export_data)
            
    with col3:
        if st.button("📋 Copy Format", use_container_width=True):
            formatted_note = soap.format_soap_note(st.session_state.soap_note)
            st.code(formatted_note, language="text")

# Reset demo
st.divider()
if st.button("🔄 Reset Demo", type="secondary"):
    st.session_state.demo_step = 1
    st.session_state.transcription = ""
    st.session_state.entities = []
    st.session_state.soap_note = {}
    st.rerun()

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px; margin-top: 2rem;">
    <h3 style="color: #667eea; margin: 0;">🩺 MediSynth Agent Demo</h3>
    <p style="margin: 0.5rem 0 0 0; color: #6c757d;">Enhanced AI-Powered Clinical Documentation</p>
    <p style="margin: 0.5rem 0 0 0; color: #dc3545; font-size: 0.875rem;">⚠️ Demo version with simulated data</p>
</div>
""", unsafe_allow_html=True)
