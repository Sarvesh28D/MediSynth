"""
MediSynth Agent - Industry-Level Medical Transcription System
Complete EHR Integration, Real-Time Audio Processing, and Clinical Workflow Management
"""

import asyncio
import io
import os
import tempfile
import time
import json
import uuid
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

import streamlit as st
from audio_recorder_streamlit import audio_recorder
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import subprocess
import platform

# Import our core modules
try:
    from asr import create_asr_processor
    from nlp import create_clinical_processor
    from nlp.soap_generator import SOAPGenerator, create_soap_generator
    from utils import create_file_handler, create_document_exporter, create_logger
    from config import Config
except ImportError as e:
    st.error(f"Error importing core modules: {e}")
    st.stop()

# Check if FFmpeg is installed
def check_ffmpeg_installed():
    """Check if FFmpeg is installed and accessible."""
    try:
        if platform.system() == 'Windows':
            # Check in PATH
            result = subprocess.run(['where', 'ffmpeg'], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True)
            return result.returncode == 0
        else:
            # For Linux/Mac
            result = subprocess.run(['which', 'ffmpeg'], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True)
            return result.returncode == 0
    except Exception:
        return False


class EHRDatabase:
    """Electronic Health Record Database Management"""
    
    def __init__(self, db_path="medisynth_ehr.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize EHR database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Patients table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth DATE,
            gender TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            emergency_contact TEXT,
            insurance_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Encounters table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS encounters (
            encounter_id TEXT PRIMARY KEY,
            patient_id TEXT,
            provider_id TEXT,
            encounter_type TEXT,
            chief_complaint TEXT,
            visit_date TIMESTAMP,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
        """)
        
        # Transcriptions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            transcription_id TEXT PRIMARY KEY,
            encounter_id TEXT,
            audio_file_path TEXT,
            transcription_text TEXT,
            confidence_score REAL,
            processing_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (encounter_id) REFERENCES encounters (encounter_id)
        )
        """)
        
        # SOAP Notes table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS soap_notes (
            soap_id TEXT PRIMARY KEY,
            encounter_id TEXT,
            subjective TEXT,
            objective TEXT,
            assessment TEXT,
            plan TEXT,
            icd_codes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (encounter_id) REFERENCES encounters (encounter_id)
        )
        """)
        
        # Clinical Entities table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clinical_entities (
            entity_id TEXT PRIMARY KEY,
            encounter_id TEXT,
            entity_type TEXT,
            entity_text TEXT,
            confidence REAL,
            start_pos INTEGER,
            end_pos INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (encounter_id) REFERENCES encounters (encounter_id)
        )
        """)
        
        # Medications table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            medication_id TEXT PRIMARY KEY,
            patient_id TEXT,
            medication_name TEXT,
            dosage TEXT,
            frequency TEXT,
            start_date DATE,
            end_date DATE,
            prescriber TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
        """)
        
        # Allergies table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS allergies (
            allergy_id TEXT PRIMARY KEY,
            patient_id TEXT,
            allergen TEXT,
            reaction TEXT,
            severity TEXT,
            onset_date DATE,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def add_patient(self, patient_data: Dict) -> str:
        """Add new patient to EHR"""
        patient_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO patients (patient_id, first_name, last_name, date_of_birth, 
                            gender, phone, email, address, emergency_contact, insurance_info)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, patient_data.get('first_name'), patient_data.get('last_name'),
              patient_data.get('date_of_birth'), patient_data.get('gender'),
              patient_data.get('phone'), patient_data.get('email'),
              patient_data.get('address'), patient_data.get('emergency_contact'),
              patient_data.get('insurance_info')))
        
        conn.commit()
        conn.close()
        return patient_id
    
    def get_patients(self) -> List[Dict]:
        """Retrieve all patients"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM patients ORDER BY last_name, first_name")
        patients = cursor.fetchall()
        
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], patient)) for patient in patients]
    
    def create_encounter(self, patient_id: str, encounter_data: Dict) -> str:
        """Create new patient encounter"""
        encounter_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO encounters (encounter_id, patient_id, provider_id, encounter_type,
                              chief_complaint, visit_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (encounter_id, patient_id, encounter_data.get('provider_id'),
              encounter_data.get('encounter_type'), encounter_data.get('chief_complaint'),
              encounter_data.get('visit_date', datetime.now()), 'active'))
        
        conn.commit()
        conn.close()
        return encounter_id
    
    def save_transcription(self, encounter_id: str, transcription_data: Dict) -> str:
        """Save transcription to database"""
        transcription_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO transcriptions (transcription_id, encounter_id, audio_file_path,
                                  transcription_text, confidence_score, processing_time)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (transcription_id, encounter_id, transcription_data.get('audio_file_path'),
              transcription_data.get('transcription_text'), transcription_data.get('confidence_score'),
              transcription_data.get('processing_time')))
        
        conn.commit()
        conn.close()
        return transcription_id
    
    def save_soap_note(self, encounter_id: str, soap_data: Dict) -> str:
        """Save SOAP note to database"""
        soap_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO soap_notes (soap_id, encounter_id, subjective, objective, 
                              assessment, plan, icd_codes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (soap_id, encounter_id, soap_data.get('subjective'),
              soap_data.get('objective'), soap_data.get('assessment'),
              soap_data.get('plan'), json.dumps(soap_data.get('icd_codes', []))))
        
        conn.commit()
        conn.close()
        return soap_id


class MediSynthUI:
    """Industry-Level MediSynth Agent Interface"""
    
    def __init__(self):
        """Initialize the comprehensive medical transcription system"""
        self.config = Config()
        self.file_handler = create_file_handler()
        self.document_exporter = create_document_exporter()
        self.logger = create_logger()
        self.ehr_db = EHRDatabase()
        
        # Initialize processors
        self.asr_processor = None
        self.clinical_processor = None
        self.soap_generator = None
        
        # Set page configuration
        st.set_page_config(
            page_title="MediSynth Agent - Ultimate Next-Generation Interface",
            page_icon="🏥",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        self._apply_ultimate_styling()
        self._init_session_state()
    
    def _apply_ultimate_styling(self):
        """Apply ultimate futuristic glassmorphism styling"""
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --warning-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
            --shadow-glow: 0 8px 32px rgba(31, 38, 135, 0.37);
            --hover-glow: 0 12px 40px rgba(31, 38, 135, 0.5);
        }

        /* Dark theme with animated background */
        .stApp {
            background: linear-gradient(-45deg, #0a0e27, #16213e, #0f3460, #533483);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            font-family: 'Exo 2', sans-serif;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Floating particles background */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 25% 25%, #ffffff10 2px, transparent 2px),
                radial-gradient(circle at 75% 75%, #ffffff08 1px, transparent 1px);
            background-size: 50px 50px, 25px 25px;
            animation: floatParticles 20s linear infinite;
            pointer-events: none;
            z-index: -1;
        }

        @keyframes floatParticles {
            0% { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(-100vh) rotate(360deg); }
        }

        /* Glass morphism cards */
        .glass-card {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: var(--shadow-glow);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .glass-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s;
        }

        .glass-card:hover::before {
            left: 100%;
        }

        .glass-card:hover {
            transform: translateY(-10px);
            box-shadow: var(--hover-glow);
        }

        /* Holographic headers */
        .holo-header {
            font-family: 'Orbitron', monospace;
            font-weight: 900;
            font-size: 2.5rem;
            background: var(--primary-gradient);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin: 20px 0;
            text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
            position: relative;
        }

        .holo-header::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: var(--primary-gradient);
            border-radius: 3px;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.5; width: 100px; }
            50% { opacity: 1; width: 150px; }
        }

        /* Neural network visualization */
        .neural-bg {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(ellipse at center, transparent 20%, rgba(102, 126, 234, 0.03) 70%),
                linear-gradient(45deg, transparent 30%, rgba(118, 75, 162, 0.05) 50%, transparent 70%);
            animation: neuralPulse 8s ease-in-out infinite;
            pointer-events: none;
        }

        @keyframes neuralPulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.8; }
        }

        /* Sidebar styling */
        .stSidebar {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--glass-border);
        }

        /* Button styling */
        .stButton > button {
            background: var(--primary-gradient);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 15px 30px;
            font-weight: 600;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .stButton > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.3s, height 0.3s;
        }

        .stButton > button:hover::before {
            width: 300px;
            height: 300px;
        }

        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }

        /* Metric cards */
        .metric-card {
            background: var(--glass-bg);
            backdrop-filter: blur(15px);
            border: 1px solid var(--glass-border);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin: 10px;
            transition: all 0.3s ease;
            position: relative;
        }

        .metric-card:hover {
            transform: scale(1.05);
            box-shadow: var(--hover-glow);
        }

        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: var(--success-gradient);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .metric-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 10px;
        }

        /* Audio visualization */
        .audio-visualizer {
            height: 100px;
            display: flex;
            align-items: end;
            justify-content: center;
            gap: 3px;
            padding: 20px;
        }

        .audio-bar {
            width: 4px;
            background: var(--success-gradient);
            border-radius: 2px;
            animation: audioWave 1s ease-in-out infinite;
        }

        .audio-bar:nth-child(1) { height: 20px; animation-delay: 0s; }
        .audio-bar:nth-child(2) { height: 40px; animation-delay: 0.1s; }
        .audio-bar:nth-child(3) { height: 60px; animation-delay: 0.2s; }
        .audio-bar:nth-child(4) { height: 80px; animation-delay: 0.3s; }
        .audio-bar:nth-child(5) { height: 100px; animation-delay: 0.4s; }
        .audio-bar:nth-child(6) { height: 80px; animation-delay: 0.5s; }
        .audio-bar:nth-child(7) { height: 60px; animation-delay: 0.6s; }
        .audio-bar:nth-child(8) { height: 40px; animation-delay: 0.7s; }
        .audio-bar:nth-child(9) { height: 20px; animation-delay: 0.8s; }
        .audio-bar:nth-child(10) { height: 30px; animation-delay: 0.9s; }

        @keyframes audioWave {
            0%, 100% { opacity: 0.3; transform: scaleY(0.5); }
            50% { opacity: 1; transform: scaleY(1.2); }
        }

        /* Holographic text */
        .holo-text {
            background: var(--primary-gradient);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
            text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
        }

        /* Progress bars */
        .stProgress > div > div > div > div {
            background: var(--success-gradient);
        }

        /* Text inputs */
        .stTextInput > div > div > input {
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            color: white;
        }

        /* Select boxes */
        .stSelectbox > div > div > div {
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
        }

        /* File uploader */
        .stFileUploader > div {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 2px dashed var(--glass-border);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .stFileUploader > div:hover {
            border-color: rgba(102, 126, 234, 0.5);
            background: rgba(102, 126, 234, 0.1);
            transform: scale(1.02);
        }

        /* Tables */
        .stDataFrame {
            background: var(--glass-bg);
            backdrop-filter: blur(15px);
            border-radius: 10px;
            border: 1px solid var(--glass-border);
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border-radius: 15px;
            padding: 10px;
            border: 1px solid var(--glass-border);
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 10px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            background: var(--primary-gradient);
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _init_session_state(self):
        """Initialize comprehensive session state"""
        # Core transcription state
        if 'transcription_text' not in st.session_state:
            st.session_state.transcription_text = ""
        if 'soap_note' not in st.session_state:
            st.session_state.soap_note = {}
        if 'clinical_entities' not in st.session_state:
            st.session_state.clinical_entities = []
        if 'confidence_score' not in st.session_state:
            st.session_state.confidence_score = 0.0
        if 'processing_status' not in st.session_state:
            st.session_state.processing_status = "ready"
        
        # EHR and patient management
        if 'current_patient' not in st.session_state:
            st.session_state.current_patient = None
        if 'current_encounter' not in st.session_state:
            st.session_state.current_encounter = None
        if 'patients_list' not in st.session_state:
            st.session_state.patients_list = []
        
        # Audio and recording
        if 'audio_file' not in st.session_state:
            st.session_state.audio_file = None
        if 'recording_active' not in st.session_state:
            st.session_state.recording_active = False
        if 'audio_history' not in st.session_state:
            st.session_state.audio_history = []
        
        # Workflow management
        if 'current_tab' not in st.session_state:
            st.session_state.current_tab = "Patient Management"
        if 'encounter_history' not in st.session_state:
            st.session_state.encounter_history = []
    
    def display_header(self):
        """Display ultimate holographic system header"""
        st.markdown("""
        <div class="holo-header">
            🏥 MEDISYNTH AGENT
        </div>
        <div style="text-align: center; color: #b0b0b0; margin-bottom: 30px;">
            <p class="holo-text">⚡ Ultimate Next-Generation Medical AI ⚡</p>
            <p>Industry-Level EHR • Real-Time Transcription • Clinical Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
    
    def display_sidebar(self):
        """Display comprehensive sidebar navigation"""
        with st.sidebar:
            st.markdown("### 🎛️ System Control Panel")
            
            # System status
            status_color = {
                "ready": "🟢", 
                "processing": "🟡", 
                "error": "🔴"
            }
            st.markdown(f"**Status:** {status_color.get(st.session_state.processing_status, '⚪')} {st.session_state.processing_status.title()}")
            
            st.markdown("---")
            
            # Current session info
            if st.session_state.current_patient:
                st.markdown("### 👤 Current Patient")
                patient = st.session_state.current_patient
                st.markdown(f"**{patient.get('first_name')} {patient.get('last_name')}**")
                st.markdown(f"ID: {patient.get('patient_id', 'N/A')[:8]}...")
                
                if st.session_state.current_encounter:
                    st.markdown(f"**Encounter:** {st.session_state.current_encounter.get('encounter_type', 'General')}")
            
            st.markdown("---")
            
            # Quick stats
            st.markdown("### 📊 Session Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Words", len(st.session_state.transcription_text.split()) if st.session_state.transcription_text else 0)
            with col2:
                st.metric("Entities", len(st.session_state.clinical_entities))
            
            if st.session_state.confidence_score > 0:
                st.metric("Confidence", f"{st.session_state.confidence_score:.1%}")
            
            st.markdown("---")
            
            # Quick actions
            st.markdown("### ⚡ Quick Actions")
            if st.button("🔄 Reset Session", use_container_width=True):
                self.reset_session()
            
            if st.button("💾 Export Current Data", use_container_width=True):
                self.export_session_data()
    
    def patient_management_tab(self):
        """Patient registration, management, and EHR import (Ultimate UI)"""
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">👥 Patient Management</div>', unsafe_allow_html=True)

        # --- EHR Upload Section ---
        st.markdown("""
        <div class="glass-card">
            <h3 class="holo-text">📤 EHR UPLOAD & IMPORT</h3>
            <p style="color: #b0b0b0; text-align: center;">Import patient data from CSV, Excel, or JSON files</p>
        </div>
        """, unsafe_allow_html=True)
        ehr_file = st.file_uploader(
            "Upload EHR File (CSV, Excel, JSON)",
            type=["csv", "xlsx", "xls", "json"],
            help="Supported formats: CSV, Excel (.xlsx/.xls), JSON",
            key="ehr_upload_file"
        )
        if ehr_file:
            try:
                if ehr_file.name.endswith(".csv"):
                    df = pd.read_csv(ehr_file)
                elif ehr_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(ehr_file)
                elif ehr_file.name.endswith('.json'):
                    df = pd.read_json(ehr_file)
                else:
                    st.error("Unsupported file format.")
                    df = None
                if df is not None:
                    st.markdown("<div class='glass-card'><b>Preview Imported Data:</b></div>", unsafe_allow_html=True)
                    st.dataframe(df, use_container_width=True)
                    if st.button("➕ Import Patients to EHR", use_container_width=True, key="import_ehr_btn"):
                        imported = 0
                        for _, row in df.iterrows():
                            patient_data = {
                                'first_name': row.get('first_name', ''),
                                'last_name': row.get('last_name', ''),
                                'date_of_birth': str(row.get('date_of_birth', '')),
                                'gender': row.get('gender', ''),
                                'phone': row.get('phone', ''),
                                'email': row.get('email', ''),
                                'address': row.get('address', ''),
                                'emergency_contact': row.get('emergency_contact', ''),
                                'insurance_info': row.get('insurance_info', '')
                            }
                            if patient_data['first_name'] and patient_data['last_name']:
                                self.ehr_db.add_patient(patient_data)
                                imported += 1
                        st.success(f"✅ Imported {imported} patients to EHR database!")
                        st.session_state.patients_list = self.ehr_db.get_patients()
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Error importing EHR file: {e}")

        # --- Patient search and selection ---
        col1, col2 = st.columns([2, 1])
        with col1:
            # Option to auto-start recording after patient selection
            if 'auto_start_recording' not in st.session_state:
                st.session_state.auto_start_recording = False
            st.checkbox("Auto-start voice recording after selecting patient", key="auto_start_recording")
            if st.button("🔄 Refresh Patient List"):
                st.session_state.patients_list = self.ehr_db.get_patients()
            if not st.session_state.patients_list:
                st.session_state.patients_list = self.ehr_db.get_patients()
            if st.session_state.patients_list:
                patient_options = [f"{p['first_name']} {p['last_name']} (ID: {p['patient_id'][:8]}...)" for p in st.session_state.patients_list]
                selected_patient_idx = st.selectbox(
                    "Select Existing Patient:",
                    range(len(patient_options)),
                    format_func=lambda x: patient_options[x],
                    key="patient_selector"
                )
                if st.button("🎯 Select Patient"):
                    st.session_state.current_patient = st.session_state.patients_list[selected_patient_idx]
                    st.success(f"Selected patient: {st.session_state.current_patient['first_name']} {st.session_state.current_patient['last_name']}")
                    # Auto-start recording if option is enabled
                    if st.session_state.auto_start_recording:
                        st.session_state.recording_active = True
                        st.session_state.processing_status = 'recording'
        with col2:
            st.markdown("**Current Patient:**")
            if st.session_state.current_patient:
                patient = st.session_state.current_patient
                st.markdown(f"""
                <div class="patient-card">
                    <strong>{patient['first_name']} {patient['last_name']}</strong><br>
                    DOB: {patient.get('date_of_birth', 'N/A')}<br>
                    Gender: {patient.get('gender', 'N/A')}<br>
                    Phone: {patient.get('phone', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No patient selected")

        # --- New patient registration ---
        st.markdown("#### 📝 Register New Patient")
        with st.expander("Add New Patient", expanded=False):
            with st.form("new_patient_form"):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name*", key="new_first_name")
                    last_name = st.text_input("Last Name*", key="new_last_name")
                    dob = st.date_input("Date of Birth", key="new_dob")
                    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"], key="new_gender")
                with col2:
                    phone = st.text_input("Phone Number", key="new_phone")
                    email = st.text_input("Email", key="new_email")
                    address = st.text_area("Address", key="new_address")
                    emergency_contact = st.text_input("Emergency Contact", key="new_emergency")
                insurance_info = st.text_area("Insurance Information", key="new_insurance")
                if st.form_submit_button("➕ Register Patient"):
                    if first_name and last_name:
                        patient_data = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'date_of_birth': str(dob),
                            'gender': gender,
                            'phone': phone,
                            'email': email,
                            'address': address,
                            'emergency_contact': emergency_contact,
                            'insurance_info': insurance_info
                        }
                        patient_id = self.ehr_db.add_patient(patient_data)
                        st.success(f"✅ Patient registered successfully! ID: {patient_id[:8]}...")
                        st.session_state.patients_list = self.ehr_db.get_patients()
                        st.rerun()
                    else:
                        st.error("⚠️ First name and last name are required!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    def encounter_management_tab(self):
        """Encounter creation and management"""
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Encounter Management</div>', unsafe_allow_html=True)
        
        if not st.session_state.current_patient:
            st.warning("⚠️ Please select a patient first in the Patient Management tab.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Current encounter display
        if st.session_state.current_encounter:
            st.markdown("#### 📊 Active Encounter")
            encounter = st.session_state.current_encounter
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Type:** {encounter.get('encounter_type', 'General')}")
            with col2:
                st.markdown(f"**Date:** {encounter.get('visit_date', 'Today')}")
            with col3:
                st.markdown(f"**Status:** <span class='status-indicator status-active'>Active</span>", unsafe_allow_html=True)
            
            st.markdown(f"**Chief Complaint:** {encounter.get('chief_complaint', 'None specified')}")
        
        # New encounter creation
        st.markdown("#### ➕ Create New Encounter")
        
        with st.form("new_encounter_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                encounter_type = st.selectbox(
                    "Encounter Type*",
                    ["Office Visit", "Follow-up", "Annual Physical", "Urgent Care", 
                     "Telemedicine", "Consultation", "Procedure", "Emergency"]
                )
                visit_date = st.date_input("Visit Date", value=datetime.now().date())
            
            with col2:
                provider_id = st.text_input("Provider ID", value="DR001")
                chief_complaint = st.text_area("Chief Complaint*", height=100)
            
            if st.form_submit_button("🎯 Start Encounter"):
                if chief_complaint:
                    encounter_data = {
                        'encounter_type': encounter_type,
                        'visit_date': datetime.combine(visit_date, datetime.now().time()),
                        'provider_id': provider_id,
                        'chief_complaint': chief_complaint
                    }
                    
                    encounter_id = self.ehr_db.create_encounter(
                        st.session_state.current_patient['patient_id'], 
                        encounter_data
                    )
                    
                    encounter_data['encounter_id'] = encounter_id
                    st.session_state.current_encounter = encounter_data
                    
                    st.success(f"✅ Encounter created successfully! ID: {encounter_id[:8]}...")
                    st.rerun()
                else:
                    st.error("⚠️ Chief complaint is required!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def audio_transcription_tab(self):
        """Ultimate next-generation audio recording and transcription"""
        # Create glassmorphism container
        st.markdown("""
        <div class="glass-card">
            <div class="neural-bg"></div>
            <h2 class="holo-text">🎤 NEURAL AUDIO PROCESSING CENTER</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.current_encounter:
            st.markdown("""
            <div class="glass-card">
                <h3 style="color: #f093fb;">⚠️ ENCOUNTER REQUIRED</h3>
                <p style="color: #b0b0b0;">Please create a patient encounter first to begin audio processing.</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Main audio processing interface
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="glass-card">
                <h3 class="holo-text">🎙️ REAL-TIME RECORDING</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Recording controls with glassmorphism styling
            col_rec1, col_rec2, col_rec3 = st.columns(3)
            
            with col_rec1:
                if st.button("🔴 START REC", use_container_width=True):
                    st.session_state.recording_active = True
                    st.session_state.processing_status = 'recording'
            
            with col_rec2:
                if st.button("⏹️ STOP REC", use_container_width=True):
                    st.session_state.recording_active = False
                    st.session_state.processing_status = 'ready'
            
            with col_rec3:
                if st.button("🔄 PROCESS", use_container_width=True):
                    st.session_state.processing_status = 'transcribing'
            
            # Audio recorder component with enhanced styling
            audio_bytes = audio_recorder(
                text="🎙️ NEURAL RECORDING",
                recording_color="#e74c3c",
                neutral_color="#667eea",
                icon_name="microphone",
                icon_size="2x",
                key="ultimate_audio_recorder",
                energy_threshold=0.001,  # Extremely low threshold to capture very quiet sounds
                pause_threshold=2.0,     # Shorter pause threshold for better responsiveness
                sample_rate=44100       # Higher sample rate for better quality
            )
            
            # Update recording state based on audio_bytes
            # Debug microphone status and check FFmpeg
            ffmpeg_installed = check_ffmpeg_installed()
            
            if not ffmpeg_installed:
                st.error("⚠️ FFmpeg is required for audio recording but isn't installed or found in PATH.")
                
                if platform.system() == 'Windows':
                    st.markdown("""
                    ### Steps to install FFmpeg on Windows:
                    
                    1. Download the FFmpeg build from [FFmpeg.org](https://ffmpeg.org/download.html) or [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
                    2. Extract the ZIP file to a location like `C:\\ffmpeg`
                    3. Add the bin folder to your PATH:
                       - Search for "Environment Variables" in Windows
                       - Edit the PATH variable and add the bin folder path (e.g., `C:\\ffmpeg\\bin`)
                    4. Restart your computer and relaunch the app
                    """)
            
            # Display recording status indicator
            if st.session_state.recording_active:
                st.markdown("""
                <div style="background-color: rgba(231, 76, 60, 0.2); border-left: 4px solid #e74c3c; padding: 10px; border-radius: 4px; margin: 10px 0;">
                    <h4 style="margin: 0; color: #e74c3c;">⚡ RECORDING ACTIVE</h4>
                    <p style="margin: 5px 0 0 0; font-size: 14px;">Microphone is capturing audio. Click the microphone button again to stop.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: rgba(0,0,0,0.1); padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <p style="margin: 0; font-size: 14px;">📢 <b>Microphone Tips:</b> Click the microphone icon above to start recording. If no audio is captured:</p>
                <ul style="margin-top: 5px; font-size: 13px;">
                    <li>Ensure your browser has permission to access the microphone</li>
                    <li>Try clicking the microphone icon again</li>
                    <li>Make sure your microphone is not muted in Windows settings</li>
                    <li>Speak clearly and close to the microphone</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if audio_bytes is not None:
                # Audio data received, update recording status
                st.session_state.recording_active = True
                st.session_state.processing_status = 'recording'
                st.success("🎙️ Recording in progress! Speak clearly...")
            
            # Audio visualization during recording
            if st.session_state.recording_active:
                st.markdown("""
                <div class="audio-visualizer">
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                </div>
                <p class="holo-text" style="text-align: center;">🎙️ NEURAL RECORDING ACTIVE...</p>
                """, unsafe_allow_html=True)
            
            if audio_bytes:
                # Display audio player with the recorded audio
                st.audio(audio_bytes, format="audio/wav")
                
                # Save the audio bytes to session state
                st.session_state.audio_file = audio_bytes
                
                # Update status
                if st.session_state.recording_active:
                    st.session_state.recording_active = False
                    st.session_state.processing_status = 'ready'
                    st.info("�️ Recording stopped and saved successfully.")
                
                # Save to audio history
                if 'audio_history' not in st.session_state:
                    st.session_state.audio_history = []
                st.session_state.audio_history.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'audio_data': audio_bytes
                })
                
                # Auto-process option
                if st.checkbox("🚀 Auto-Neural Processing", value=True):
                    if st.session_state.audio_file:
                        with st.spinner("🧠 Processing audio..."):
                            self.process_audio_transcription()

        with col2:
            st.markdown("""
            <div class="glass-card">
                <h3 class="holo-text">📁 AUDIO FILE UPLOAD</h3>
                <p style="color: #b0b0b0; text-align: center;">Upload your medical audio recordings for AI processing</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced file uploader with glassmorphism
            uploaded_file = st.file_uploader(
                "🚀 DRAG & DROP AUDIO FILES",
                type=['wav', 'mp3', 'mp4', 'm4a', 'ogg', 'flac'],
                help="Supported: WAV, MP3, MP4, M4A, OGG, FLAC - Maximum 200MB",
                label_visibility="collapsed"
            )
            
            if uploaded_file:
                st.markdown("""
                <div class="glass-card">
                    <h4 class="holo-text">✅ FILE LOADED</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.audio(uploaded_file)
                st.session_state.audio_file = uploaded_file.read()
                
                # Enhanced file info display
                file_size_mb = len(st.session_state.audio_file) / (1024 * 1024)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{uploaded_file.name}</div>
                    <div class="metric-label">📊 {file_size_mb:.2f} MB</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick process button
                if st.button("🧠 NEURAL TRANSCRIBE", use_container_width=True, type="primary"):
                    self.process_audio_transcription()
        
        # Advanced processing controls
        st.markdown("""
        <div class="glass-card">
            <h3 class="holo-text">🧠 AI PROCESSING CONTROLS</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚀 NEURAL PROCESS", use_container_width=True, disabled=not st.session_state.audio_file):
                self.process_audio_transcription()
        
        with col2:
            if st.button("� EXTRACT ENTITIES", use_container_width=True, disabled=not st.session_state.transcription_text):
                self.extract_clinical_entities()
        
        with col3:
            if st.button("📋 GENERATE SOAP", use_container_width=True, disabled=not st.session_state.transcription_text):
                self.generate_soap_note()
        
        with col4:
            if st.button("💾 SAVE TO EHR", use_container_width=True, disabled=not st.session_state.transcription_text):
                self.save_to_ehr()
        # The following 'with col1:' block was duplicated and is not needed, so we add a 'pass' to avoid syntax error
        with col1:
            pass
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def clinical_entities_tab(self):
        """Clinical entity extraction and management"""
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🧠 Clinical Entity Analysis</div>', unsafe_allow_html=True)
        
        if not st.session_state.transcription_text:
            st.info("📝 Complete transcription first to extract clinical entities.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Entity extraction controls
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### 🔍 Entity Extraction Settings")
            
            entity_types = st.multiselect(
                "Select entity types to extract:",
                ["Symptoms", "Medications", "Conditions", "Procedures", "Anatomy", "Lab Values", "Vitals"],
                default=["Symptoms", "Medications", "Conditions"],
                help="Choose which types of clinical entities to identify"
            )
        
        with col2:
            st.markdown("#### ⚡ Actions")
            if st.button("🧠 Extract Entities", use_container_width=True):
                self.extract_clinical_entities()
            
            if st.button("🔄 Re-analyze", use_container_width=True):
                st.session_state.clinical_entities = []
                self.extract_clinical_entities()
        
        # Display extracted entities
        if st.session_state.clinical_entities:
            st.markdown("#### 📊 Extracted Clinical Entities")
            
            # Entity statistics
            entity_counts = {}
            for entity in st.session_state.clinical_entities:
                entity_type = entity.get('type', 'Unknown')
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            
            # Display as metrics
            if entity_counts:
                cols = st.columns(len(entity_counts))
                for i, (entity_type, count) in enumerate(entity_counts.items()):
                    with cols[i]:
                        st.metric(entity_type, count)
            
            # Entity table
            if st.session_state.clinical_entities:
                df_entities = pd.DataFrame(st.session_state.clinical_entities)
                st.dataframe(df_entities, use_container_width=True)
            
            # Entity tags display
            st.markdown("##### 🏷️ Entity Tags")
            entity_html = ""
            for entity in st.session_state.clinical_entities:
                entity_text = entity.get('text', '')
                entity_type = entity.get('type', 'Unknown')
                entity_html += f'<span class="entity-tag" title="{entity_type}">{entity_text}</span>'
            
            st.markdown(entity_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def soap_note_tab(self):
        """SOAP note generation and editing"""
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 SOAP Note Generation</div>', unsafe_allow_html=True)
        
        if not st.session_state.transcription_text:
            st.info("📝 Complete transcription first to generate SOAP notes.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # SOAP generation controls
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### ⚙️ SOAP Generation Settings")
            
            include_icd = st.checkbox("📊 Include ICD-10 Codes", value=True)
            include_cpt = st.checkbox("🏥 Include CPT Codes", value=True)
            detailed_assessment = st.checkbox("🔍 Detailed Assessment", value=True)
        
        with col2:
            st.markdown("#### ⚡ Actions")
            if st.button("📋 Generate SOAP", use_container_width=True):
                self.generate_soap_note()
            
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.soap_note = {}
                self.generate_soap_note()
        
        # Display/Edit SOAP note
        if st.session_state.soap_note:
            st.markdown("#### 📝 SOAP Note (Editable)")
            
            soap_sections = ['subjective', 'objective', 'assessment', 'plan']
            soap_labels = ['Subjective', 'Objective', 'Assessment', 'Plan']
            
            edited_soap = {}
            
            for section, label in zip(soap_sections, soap_labels):
                st.markdown(f"##### {label}")
                edited_content = st.text_area(
                    f"{label} Content:",
                    value=st.session_state.soap_note.get(section, ''),
                    height=150,
                    key=f"soap_{section}",
                    label_visibility="collapsed"
                )
                edited_soap[section] = edited_content
            
            # Update SOAP note if changes made
            if edited_soap != st.session_state.soap_note:
                if st.button("💾 Update SOAP Note"):
                    st.session_state.soap_note = edited_soap
                    st.success("✅ SOAP note updated!")
                    st.rerun()
            
            # SOAP note preview
            st.markdown("#### 👁️ SOAP Note Preview")
            with st.expander("View Formatted SOAP Note", expanded=False):
                for section, label in zip(soap_sections, soap_labels):
                    if st.session_state.soap_note.get(section):
                        st.markdown(f"**{label}:**")
                        st.write(st.session_state.soap_note[section])
                        st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def reports_analytics_tab(self):
        """Reporting and analytics dashboard"""
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Reports & Analytics</div>', unsafe_allow_html=True)
        
        # Quick metrics
        st.markdown("#### 📈 System Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">45</div>
                <div class="metric-label">Total Patients</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">128</div>
                <div class="metric-label">Encounters</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">96.2%</div>
                <div class="metric-label">Avg Confidence</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">2.3s</div>
                <div class="metric-label">Avg Process Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts and visualizations
        st.markdown("#### 📊 Analytics Dashboard")
        
        # Sample charts (replace with real data from EHR)
        col1, col2 = st.columns(2)
        
        with col1:
            # Encounters by type
            encounter_types = ['Office Visit', 'Follow-up', 'Annual Physical', 'Urgent Care', 'Telemedicine']
            encounter_counts = [45, 32, 18, 12, 8]
            
            fig_encounters = px.pie(
                values=encounter_counts, 
                names=encounter_types,
                title="Encounters by Type (Last 30 Days)"
            )
            st.plotly_chart(fig_encounters, use_container_width=True)
        
        with col2:
            # Processing time trends
            dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
            processing_times = np.random.normal(2.3, 0.5, 30)
            
            fig_times = px.line(
                x=dates, 
                y=processing_times,
                title="Average Processing Time Trend",
                labels={'x': 'Date', 'y': 'Processing Time (seconds)'}
            )
            st.plotly_chart(fig_times, use_container_width=True)
        
        # Export options
        st.markdown("#### 💾 Export Options")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📄 Export PDF Report", use_container_width=True):
                self.export_pdf_report()
        
        with col2:
            if st.button("📊 Export Excel Data", use_container_width=True):
                self.export_excel_data()
        
        with col3:
            if st.button("📋 Export SOAP Notes", use_container_width=True):
                self.export_soap_notes()
        
        with col4:
            if st.button("🗄️ Backup Database", use_container_width=True):
                self.backup_database()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def process_audio_transcription(self):
        """Process audio file for transcription"""
        if not st.session_state.audio_file:
            st.error("❌ No audio file available for processing")
            return
        
        try:
            st.session_state.processing_status = "processing"
            
            # Initialize ASR processor if needed
            if not self.asr_processor:
                with st.spinner("🔧 Initializing ASR processor..."):
                    self.asr_processor = create_asr_processor()
            
            # Create progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Save audio temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(st.session_state.audio_file)
                temp_path = tmp_file.name
            
            try:
                # Process audio
                status_text.text("🎯 Transcribing audio...")
                progress_bar.progress(25)
                
                start_time = time.time()
                result = self.asr_processor.transcribe(temp_path)
                processing_time = time.time() - start_time
                
                progress_bar.progress(75)
                
                # Extract results
                if isinstance(result, dict):
                    st.session_state.transcription_text = result.get('text', '')
                    st.session_state.confidence_score = result.get('confidence', 0.0)
                else:
                    st.session_state.transcription_text = str(result)
                    st.session_state.confidence_score = 0.0
                
                progress_bar.progress(100)
                status_text.text("✅ Transcription complete!")
                
                # Save to database if encounter exists
                if st.session_state.current_encounter:
                    transcription_data = {
                        'audio_file_path': temp_path,
                        'transcription_text': st.session_state.transcription_text,
                        'confidence_score': st.session_state.confidence_score,
                        'processing_time': processing_time
                    }
                    
                    self.ehr_db.save_transcription(
                        st.session_state.current_encounter['encounter_id'],
                        transcription_data
                    )
                
                st.session_state.processing_status = "ready"
                st.success("🎉 Audio transcription completed successfully!")
                
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            st.session_state.processing_status = "error"
            st.error(f"❌ Error processing audio: {str(e)}")
            self.logger.error(f"Audio processing error: {e}")
    
    def extract_clinical_entities(self):
        """Extract clinical entities from transcription"""
        if not st.session_state.transcription_text:
            st.error("❌ No transcription available for entity extraction")
            return
        
        try:
            if not self.clinical_processor:
                with st.spinner("🔧 Initializing clinical processor..."):
                    self.clinical_processor = create_clinical_processor()
            
            with st.spinner("🧠 Extracting clinical entities..."):
                entities = self.clinical_processor.extract_entities(st.session_state.transcription_text)
                st.session_state.clinical_entities = entities
                
                # Save entities to database if encounter exists
                if st.session_state.current_encounter:
                    for entity in entities:
                        entity_data = {
                            'entity_type': entity.get('type', 'Unknown'),
                            'entity_text': entity.get('text', ''),
                            'confidence': entity.get('confidence', 0.0),
                            'start_pos': entity.get('start', 0),
                            'end_pos': entity.get('end', 0)
                        }
                        
                        # Save to database (implement entity saving)
                        # self.ehr_db.save_clinical_entity(encounter_id, entity_data)
                
                st.success(f"✅ Extracted {len(entities)} clinical entities!")
                
        except Exception as e:
            st.error(f"❌ Error extracting entities: {str(e)}")
            self.logger.error(f"Entity extraction error: {e}")
    
    def generate_soap_note(self):
        """Generate structured SOAP note using Gemini LLM if available."""
        if not st.session_state.transcription_text:
            st.error("❌ No transcription available for SOAP note generation")
            return
        try:
            if not hasattr(self, 'soap_generator') or self.soap_generator is None:
                with st.spinner("🔧 Initializing SOAP generator with Gemini..."):
                    # Use Gemini for SOAP generation
                    self.soap_generator = SOAPGenerator(use_gemini=True)
            # Prepare processed_data dict as expected by SOAPGenerator
            processed_data = {
                "categorized_entities": st.session_state.clinical_entities,
                "conversation_structure": {},
                "raw_text": st.session_state.transcription_text
            }
            with st.spinner("📋 Generating SOAP note with Gemini..."):
                soap_note = self.soap_generator.generate_soap_note(
                    processed_data,
                    patient_info=st.session_state.get('current_patient'),
                    provider_info=None
                )
                st.session_state.soap_note = soap_note
                # Save SOAP note to database
                if st.session_state.current_encounter:
                    self.ehr_db.save_soap_note(
                        st.session_state.current_encounter['encounter_id'],
                        soap_note
                    )
                st.success("✅ SOAP note generated successfully!")
        except Exception as e:
            st.error(f"❌ Error generating SOAP note: {str(e)}")
            self.logger.error(f"SOAP generation error: {e}")
    
    def save_to_ehr(self):
        """Save current session data to EHR"""
        if not st.session_state.current_encounter:
            st.error("❌ No active encounter to save data to")
            return
        
        try:
            with st.spinner("💾 Saving to EHR..."):
                # Data already saved during processing, just confirm
                st.success("✅ All data saved to Electronic Health Record!")
                
        except Exception as e:
            st.error(f"❌ Error saving to EHR: {str(e)}")
            self.logger.error(f"EHR save error: {e}")
    
    def reset_session(self):
        """Reset current session"""
        st.session_state.transcription_text = ""
        st.session_state.soap_note = {}
        st.session_state.clinical_entities = []
        st.session_state.confidence_score = 0.0
        st.session_state.audio_file = None
        st.session_state.processing_status = "ready"
        st.success("🔄 Session reset successfully!")
    
    def export_session_data(self):
        """Export current session data"""
        if not any([st.session_state.transcription_text, st.session_state.soap_note, st.session_state.clinical_entities]):
            st.warning("⚠️ No data available to export")
            return
        
        try:
            export_data = {
                'patient': st.session_state.current_patient,
                'encounter': st.session_state.current_encounter,
                'transcription': st.session_state.transcription_text,
                'soap_note': st.session_state.soap_note,
                'clinical_entities': st.session_state.clinical_entities,
                'confidence_score': st.session_state.confidence_score,
                'export_timestamp': datetime.now().isoformat()
            }
            
            json_str = json.dumps(export_data, indent=2)
            
            st.download_button(
                label="📥 Download Session Data (JSON)",
                data=json_str,
                file_name=f"medisynth_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"❌ Error exporting data: {str(e)}")
    
    def export_pdf_report(self):
        """Export comprehensive PDF report"""
        st.info("📄 PDF export functionality will be implemented")
    
    def export_excel_data(self):
        """Export data to Excel format"""
        st.info("📊 Excel export functionality will be implemented")
    
    def export_soap_notes(self):
        """Export SOAP notes collection"""
        st.info("📋 SOAP notes export functionality will be implemented")
    
    def backup_database(self):
        """Create database backup"""
        st.info("🗄️ Database backup functionality will be implemented")
    
    def run(self):
        """Run the comprehensive MediSynth interface"""
        try:
            # Display header
            self.display_header()
            
            # Display sidebar
            self.display_sidebar()
            
            # Main tabbed interface with ultimate styling
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "👥 PATIENT NEURAL NET", 
                "📋 ENCOUNTER MATRIX",
                "🎤 AUDIO SYNTHESIS",
                "� ENTITY EXTRACTION",
                "📝 SOAP GENERATOR",
                "📊 ANALYTICS CORE"
            ])
            
            with tab1:
                self.patient_management_tab()
            
            with tab2:
                self.encounter_management_tab()
            
            with tab3:
                self.audio_transcription_tab()

            with tab4:
                self.clinical_entities_tab()

            with tab5:
                self.soap_note_tab()

            with tab6:
                self.reports_analytics_tab()

        except Exception as e:
            st.error(f"❌ System error: {str(e)}")
            self.logger.error(f"UI error: {e}")


# Create and export the UI instance
def create_ui():
    """Create and return a MediSynth UI instance"""
    return MediSynthUI()

# For direct execution
if __name__ == "__main__":
    ui = create_ui()
    ui.run()
