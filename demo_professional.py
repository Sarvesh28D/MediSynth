"""
Professional Enterprise-Grade Demo of MediSynth Agent.
"""

import streamlit as st
import tempfile
import os
import time
import json
from datetime import datetime

# Configure page with professional settings
st.set_page_config(
    page_title="MediSynth Agent - Clinical Documentation",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional Enterprise CSS
st.markdown("""
<style>
/* Import Professional Fonts */
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* Global Professional Styles */
.main {
    font-family: 'Source Sans Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #fafbfc;
}

/* Professional Header */
.header-container {
    background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    border: 1px solid #dee2e6;
    border-bottom: 3px solid #0066cc;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

.header-title {
    color: #212529;
    font-size: 1.75rem;
    font-weight: 600;
    margin: 0;
    line-height: 1.2;
}

.header-subtitle {
    color: #6c757d;
    font-size: 0.875rem;
    margin-top: 0.25rem;
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Professional Cards */
.clinical-card {
    background: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.clinical-card:hover {
    border-color: #0066cc;
    box-shadow: 0 2px 8px rgba(0,102,204,0.15);
}

.clinical-card-header {
    color: #495057;
    font-size: 0.875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e9ecef;
}

/* Professional Status Indicators */
.status-indicator {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-completed {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.status-processing {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeaa7;
}

.status-pending {
    background-color: #f8f9fa;
    color: #6c757d;
    border: 1px solid #dee2e6;
}

/* Professional Entity Tags */
.entity-tag {
    display: inline-block;
    padding: 0.125rem 0.5rem;
    margin: 0.125rem;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: 500;
    font-family: 'IBM Plex Mono', monospace;
}

.entity-symptom {
    background-color: #e3f2fd;
    color: #0d47a1;
    border: 1px solid #bbdefb;
}

.entity-medication {
    background-color: #e8f5e8;
    color: #1b5e20;
    border: 1px solid #c8e6c9;
}

.entity-condition {
    background-color: #fff3e0;
    color: #e65100;
    border: 1px solid #ffcc02;
}

.entity-vital {
    background-color: #f3e5f5;
    color: #4a148c;
    border: 1px solid #e1bee7;
}

/* Professional Buttons */
.stButton > button {
    border-radius: 4px;
    border: 1px solid #0066cc;
    padding: 0.5rem 1rem;
    font-weight: 500;
    font-size: 0.875rem;
    background-color: #0066cc;
    color: white;
    transition: all 0.15s ease-in-out;
}

.stButton > button:hover {
    background-color: #0052a3;
    border-color: #0052a3;
    box-shadow: 0 2px 4px rgba(0,102,204,0.25);
}

/* Professional Metrics */
.metric-container {
    background: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 1rem;
    text-align: center;
    margin-bottom: 1rem;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 600;
    color: #0066cc;
    margin-bottom: 0.25rem;
}

.metric-label {
    font-size: 0.75rem;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Professional Progress */
.progress-step {
    display: flex;
    align-items: center;
    padding: 0.5rem 0;
    font-size: 0.875rem;
}

.progress-step-number {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background-color: #f8f9fa;
    border: 2px solid #dee2e6;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.75rem;
}

.progress-step-number.active {
    background-color: #0066cc;
    border-color: #0066cc;
    color: white;
}

.progress-step-number.completed {
    background-color: #28a745;
    border-color: #28a745;
    color: white;
}

/* Professional Alerts */
.alert-info {
    background-color: #e7f3ff;
    border: 1px solid #b3d9ff;
    border-left: 4px solid #0066cc;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    color: #004085;
    margin: 1rem 0;
}

/* Remove animations */
* {
    animation: none !important;
    transition: all 0.15s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# Mock professional classes
class ProfessionalASR:
    def __init__(self):
        self.model_info = "OpenAI Whisper Base Model"
    
    def transcribe(self, audio_file):
        # Professional progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stages = [
            "Initializing audio processor...",
            "Loading speech recognition model...",
            "Processing audio signal...",
            "Generating transcription..."
        ]
        
        for i, stage in enumerate(stages):
            status_text.text(stage)
            for j in range(25):
                time.sleep(0.005)
                progress_bar.progress(i * 25 + j + 1)
        
        status_text.empty()
        progress_bar.empty()
        
        return {
            "text": "Good morning, Doctor. I've been experiencing chest pain for the past 24 hours. The pain is sharp, located in the center of my chest, and worsens with deep inspiration. I also noticed some shortness of breath and mild nausea this morning. I have no known allergies and am currently taking lisinopril 10mg daily for hypertension.",
            "confidence": 0.89
        }

class ProfessionalNLP:
    def extract_entities(self, text):
        # Professional processing
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stages = [
            "Loading medical NLP models...",
            "Tokenizing clinical text...",
            "Identifying medical entities...",
            "Calculating confidence scores..."
        ]
        
        for i, stage in enumerate(stages):
            status_text.text(stage)
            for j in range(25):
                time.sleep(0.005)
                progress_bar.progress(i * 25 + j + 1)
        
        status_text.empty()
        progress_bar.empty()
        
        return [
            {"text": "chest pain", "label": "SYMPTOM", "confidence": 0.94, "start": 45, "end": 55},
            {"text": "sharp", "label": "SYMPTOM", "confidence": 0.87, "start": 70, "end": 75},
            {"text": "shortness of breath", "label": "SYMPTOM", "confidence": 0.91, "start": 180, "end": 199},
            {"text": "nausea", "label": "SYMPTOM", "confidence": 0.85, "start": 210, "end": 216},
            {"text": "lisinopril 10mg", "label": "MEDICATION", "confidence": 0.96, "start": 280, "end": 295},
            {"text": "hypertension", "label": "CONDITION", "confidence": 0.93, "start": 310, "end": 322}
        ]

class ProfessionalSOAP:
    def generate_note(self, transcription, entities):
        # Professional generation
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            status_text.text(f"Generating clinical documentation... {i+1}%")
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        
        status_text.empty()
        progress_bar.empty()
        
        return {
            "subjective": """Chief Complaint: Chest pain for 24 hours

History of Present Illness:
Patient reports acute onset of chest pain beginning 24 hours ago. Pain is described as sharp, centrally located, and exacerbated by deep inspiration. Associated symptoms include dyspnea and nausea observed this morning. 

Past Medical History: Hypertension
Current Medications: Lisinopril 10mg daily
Allergies: No known drug allergies""",

            "objective": """Vital Signs: [To be obtained]
Physical Examination: [To be performed]
Patient appears alert and cooperative
No acute distress at rest""",

            "assessment": """Primary Concerns:
1. Acute chest pain - differential diagnosis includes:
   - Pleuritic chest pain
   - Costochondritis  
   - Rule out cardiac etiology
2. Dyspnea - possibly related to chest pain
3. Hypertension - stable on current medication""",

            "plan": """Diagnostic Workup:
- 12-lead ECG
- Chest X-ray
- Basic metabolic panel
- Troponin levels

Treatment:
- Monitor vital signs
- Pain assessment and management
- Cardiology consultation if indicated

Follow-up:
- Primary care within 48 hours
- Return if symptoms worsen
- Continue current antihypertensive therapy"""
        }

# Initialize professional components
if 'demo_step' not in st.session_state:
    st.session_state.demo_step = 1
if 'transcription' not in st.session_state:
    st.session_state.transcription = ""
if 'entities' not in st.session_state:
    st.session_state.entities = []
if 'soap_note' not in st.session_state:
    st.session_state.soap_note = {}

asr = ProfessionalASR()
nlp = ProfessionalNLP()
soap = ProfessionalSOAP()

# Professional Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">MediSynth Agent</h1>
    <p class="header-subtitle">Clinical Documentation Assistant - Professional Demo</p>
</div>
""", unsafe_allow_html=True)

# System Status Dashboard
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-container">
        <div class="metric-value">ASR</div>
        <div class="metric-label">Speech Recognition</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-container">
        <div class="metric-value">NLP</div>
        <div class="metric-label">Entity Extraction</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-container">
        <div class="metric-value">SOAP</div>
        <div class="metric-label">Note Generation</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-container">
        <div class="metric-value">Ready</div>
        <div class="metric-label">System Status</div>
    </div>
    """, unsafe_allow_html=True)

# Workflow Progress
st.markdown("""
<div class="clinical-card">
    <div class="clinical-card-header">Workflow Status</div>
</div>
""", unsafe_allow_html=True)

steps = [
    {"num": 1, "title": "Audio Input", "status": "Upload audio file"},
    {"num": 2, "title": "Transcription", "status": "Speech-to-text processing"},
    {"num": 3, "title": "Entity Extraction", "status": "Medical entity identification"},
    {"num": 4, "title": "SOAP Generation", "status": "Clinical note creation"},
    {"num": 5, "title": "Documentation", "status": "Export and review"}
]

for step in steps:
    status_class = ""
    if step["num"] < st.session_state.demo_step:
        status_class = "completed"
    elif step["num"] == st.session_state.demo_step:
        status_class = "active"
    else:
        status_class = "pending"
    
    st.markdown(f"""
    <div class="progress-step">
        <div class="progress-step-number {status_class}">
            {step["num"]}
        </div>
        <div>
            <strong>{step["title"]}</strong><br>
            <small style="color: #6c757d;">{step["status"]}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Step 1: Audio Input
st.markdown("""
<div class="clinical-card">
    <div class="clinical-card-header">Step 1: Audio Input</div>
    <div class="alert-info">
        Professional Demo: Simulated doctor-patient consultation audio processing
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Load Sample Consultation Audio", type="primary", use_container_width=True):
    st.session_state.demo_step = 2
    st.success("✓ Audio file loaded: patient-consultation-20250718.wav (Duration: 3:42)")

# Step 2: Transcription
if st.session_state.demo_step >= 2:
    st.markdown("""
    <div class="clinical-card">
        <div class="clinical-card-header">Step 2: Speech Recognition</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Begin Transcription", type="primary", use_container_width=True):
        with st.container():
            result = asr.transcribe("audio_file")
            st.session_state.transcription = result["text"]
            st.session_state.demo_step = 3
            
            st.success(f"✓ Transcription completed (Confidence: {result['confidence']:.1%})")
    
    if st.session_state.transcription:
        st.text_area("Transcribed Text", value=st.session_state.transcription, height=120, disabled=True)

# Step 3: Entity Extraction
if st.session_state.demo_step >= 3:
    st.markdown("""
    <div class="clinical-card">
        <div class="clinical-card-header">Step 3: Medical Entity Extraction</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Extract Clinical Entities", type="primary", use_container_width=True):
        with st.container():
            entities = nlp.extract_entities(st.session_state.transcription)
            st.session_state.entities = entities
            st.session_state.demo_step = 4
            
            st.success(f"✓ Extracted {len(entities)} medical entities")
    
    if st.session_state.entities:
        # Professional entity display
        st.markdown("""
        <div class="clinical-card">
            <div class="clinical-card-header">Identified Clinical Entities</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Entity counts
        entity_counts = {}
        for entity in st.session_state.entities:
            label = entity["label"]
            entity_counts[label] = entity_counts.get(label, 0) + 1
        
        cols = st.columns(len(entity_counts))
        for i, (label, count) in enumerate(entity_counts.items()):
            with cols[i]:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{count}</div>
                    <div class="metric-label">{label.title()}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Professional entity tags
        for entity_type in ["SYMPTOM", "MEDICATION", "CONDITION"]:
            type_entities = [e for e in st.session_state.entities if e["label"] == entity_type]
            if type_entities:
                st.markdown(f"**{entity_type.title()}s:**")
                tags_html = ""
                for entity in type_entities:
                    css_class = f"entity-{entity_type.lower()}"
                    tags_html += f"""
                    <span class="entity-tag {css_class}" 
                          title="Confidence: {entity['confidence']:.1%}">
                        {entity['text']}
                    </span>
                    """
                st.markdown(tags_html, unsafe_allow_html=True)
                st.write("")

# Step 4: SOAP Generation
if st.session_state.demo_step >= 4:
    st.markdown("""
    <div class="clinical-card">
        <div class="clinical-card-header">Step 4: SOAP Note Generation</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Generate Clinical Documentation", type="primary", use_container_width=True):
        with st.container():
            soap_note = soap.generate_note(st.session_state.transcription, st.session_state.entities)
            st.session_state.soap_note = soap_note
            st.session_state.demo_step = 5
            
            st.success("✓ SOAP note generated successfully")
    
    if st.session_state.soap_note:
        st.markdown("""
        <div class="clinical-card">
            <div class="clinical-card-header">Generated SOAP Note</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Professional SOAP display
        sections = [
            ("subjective", "SUBJECTIVE"),
            ("objective", "OBJECTIVE"), 
            ("assessment", "ASSESSMENT"),
            ("plan", "PLAN")
        ]
        
        for key, title in sections:
            if key in st.session_state.soap_note:
                st.markdown(f"**{title}**")
                st.text_area(
                    f"{title} Section",
                    value=st.session_state.soap_note[key],
                    height=100,
                    key=f"soap_{key}",
                    label_visibility="collapsed"
                )

# Step 5: Export
if st.session_state.demo_step >= 5:
    st.markdown("""
    <div class="clinical-card">
        <div class="clinical-card-header">Step 5: Documentation Export</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export PDF", type="primary", use_container_width=True):
            st.success("✓ PDF documentation exported")
    
    with col2:
        if st.button("Export JSON", type="secondary", use_container_width=True):
            export_data = {
                "transcription": st.session_state.transcription,
                "entities": st.session_state.entities,
                "soap_note": st.session_state.soap_note,
                "timestamp": datetime.now().isoformat()
            }
            st.json(export_data)
    
    with col3:
        if st.button("Reset Demo", use_container_width=True):
            st.session_state.demo_step = 1
            st.session_state.transcription = ""
            st.session_state.entities = []
            st.session_state.soap_note = {}
            st.rerun()

# Professional Footer
st.markdown("""
<div style="background: #ffffff; border-top: 1px solid #dee2e6; padding: 1.5rem; margin-top: 2rem; text-align: center; color: #6c757d; font-size: 0.875rem;">
    <strong>MediSynth Agent</strong> - Clinical Documentation Assistant<br>
    <small>Professional demonstration environment. For educational purposes only.</small>
</div>
""", unsafe_allow_html=True)
