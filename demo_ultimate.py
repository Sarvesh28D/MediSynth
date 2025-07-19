"""
MediSynth - Ultimate Next-Generation Interface
=============================================
Ultra-modern medical transcription with cutting-edge UI components
"""

import streamlit as st
try:
    import streamlit_lottie as st_lottie
    from streamlit_option_menu import option_menu
    import streamlit_extras.add_vertical_space as avs
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.metric_cards import style_metric_cards
    from streamlit_extras.stylable_container import stylable_container
    HAS_EXTRAS = True
except ImportError:
    HAS_EXTRAS = False
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import sys

# Add the parent directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from nlp.soap_generator import SOAPGenerator
    from asr.processor import AudioProcessor
    from utils.helpers import generate_test_audio_data, format_timestamp
    HAS_MEDICAL_MODULES = True
except ImportError:
    HAS_MEDICAL_MODULES = False
    # Dummy classes for demo purposes
    class SOAPGenerator:
        @staticmethod
        def generate_soap_note(text, specialty="General Medicine"):
            return f"""
SOAP NOTE - {specialty}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUBJECTIVE:
{text[:200]}...

OBJECTIVE:
Vital signs stable. Physical examination findings within normal limits.

ASSESSMENT:
Clinical assessment based on subjective and objective findings.

PLAN:
Treatment plan will be determined based on assessment.
            """
    
    class AudioProcessor:
        @staticmethod
        def process_audio(file):
            return "Sample transcription text for demo purposes."

# Page config with wide layout
st.set_page_config(
    page_title="MediSynth - Ultimate Interface",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ultimate futuristic CSS with animations and glassmorphism
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
    animation: audioWave 1.5s ease-in-out infinite;
}

.audio-bar:nth-child(2n) { animation-delay: 0.1s; }
.audio-bar:nth-child(3n) { animation-delay: 0.2s; }
.audio-bar:nth-child(4n) { animation-delay: 0.3s; }

@keyframes audioWave {
    0%, 100% { height: 10px; opacity: 0.3; }
    50% { height: 80px; opacity: 1; }
}

/* Progress ring */
.progress-ring {
    width: 120px;
    height: 120px;
    margin: 20px auto;
}

.progress-ring circle {
    stroke: var(--success-gradient);
    stroke-width: 8;
    stroke-linecap: round;
    fill: transparent;
    animation: progressSpin 2s linear infinite;
}

@keyframes progressSpin {
    0% { stroke-dasharray: 0 251; }
    50% { stroke-dasharray: 125 125; transform: rotate(90deg); }
    100% { stroke-dasharray: 251 0; transform: rotate(180deg); }
}

/* Holographic text effects */
.holo-text {
    color: #00ffff;
    text-shadow: 
        0 0 5px #00ffff,
        0 0 10px #00ffff,
        0 0 15px #00ffff;
    animation: holoFlicker 3s ease-in-out infinite;
}

@keyframes holoFlicker {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--glass-bg);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: var(--primary-gradient);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--secondary-gradient);
}

/* Status indicators */
.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 10px;
    animation: statusPulse 2s infinite;
}

.status-online { background: #00ff88; }
.status-processing { background: #ffaa00; }
.status-offline { background: #ff4444; }

@keyframes statusPulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Floating action button */
.fab {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    background: var(--secondary-gradient);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    cursor: pointer;
    box-shadow: var(--shadow-glow);
    transition: all 0.3s ease;
    z-index: 1000;
}

.fab:hover {
    transform: scale(1.1) rotate(90deg);
    box-shadow: var(--hover-glow);
}

/* Data flow animation */
.data-flow {
    position: relative;
    height: 200px;
    overflow: hidden;
    border-radius: 15px;
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
}

.data-particle {
    position: absolute;
    width: 6px;
    height: 6px;
    background: var(--success-gradient);
    border-radius: 50%;
    animation: dataFlow 3s linear infinite;
}

@keyframes dataFlow {
    0% { transform: translateX(-100px) translateY(0); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateX(calc(100vw + 100px)) translateY(-20px); opacity: 0; }
}

/* Loading shimmer */
.loading-shimmer {
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}

</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = 'idle'
if 'transcription_history' not in st.session_state:
    st.session_state.transcription_history = []

# Lottie animation for header
def load_lottie_animation():
    """Load a simple animation data"""
    return {
        "v": "4.8.0",
        "meta": {"g": "LottieFiles AE ", "a": "", "k": "", "d": "", "tc": ""},
        "fr": 30,
        "ip": 0,
        "op": 60,
        "w": 512,
        "h": 512,
        "nm": "Medical Animation",
        "ddd": 0,
        "assets": [],
        "layers": [
            {
                "ddd": 0,
                "ind": 1,
                "ty": 4,
                "nm": "Circle",
                "sr": 1,
                "ks": {
                    "o": {"a": 0, "k": 100, "ix": 11},
                    "r": {"a": 1, "k": [
                        {"i": {"x": [0.833], "y": [0.833]}, "o": {"x": [0.167], "y": [0.167]}, "t": 0, "s": [0]},
                        {"t": 59, "s": [360]}
                    ], "ix": 10},
                    "p": {"a": 0, "k": [256, 256, 0], "ix": 2},
                    "a": {"a": 0, "k": [0, 0, 0], "ix": 1},
                    "s": {"a": 0, "k": [100, 100, 100], "ix": 6}
                }
            }
        ]
    }

# Header with animation
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="holo-header">🏥 MediSynth Ultimate</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #b0b0b0; font-size: 1.2rem;">Next-Generation Medical Transcription AI</p>', unsafe_allow_html=True)

# Navigation
with st.container():
    if HAS_EXTRAS:
        # Use advanced option menu if available
        selected = option_menu(
            menu_title=None,
            options=["🎙️ Transcribe", "📊 Analytics", "📋 History", "⚙️ Settings"],
            icons=['mic', 'graph-up', 'clock-history', 'gear'],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#00ffff", "font-size": "18px"}, 
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "center", 
                    "margin": "0px", 
                    "--hover-color": "rgba(255, 255, 255, 0.1)",
                    "background-color": "rgba(255, 255, 255, 0.05)",
                    "border-radius": "15px",
                    "backdrop-filter": "blur(10px)"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                }
            }
        )
    else:
        # Fallback to simple radio buttons
        selected = st.radio(
            "Navigation",
            ["🎙️ Transcribe", "📊 Analytics", "📋 History", "⚙️ Settings"],
            horizontal=True,
            label_visibility="collapsed"
        )

if HAS_EXTRAS:
    avs.add_vertical_space(2)
else:
    st.markdown("<br>", unsafe_allow_html=True)

# Main content based on selection
if selected == "🎙️ Transcribe":
    # Real-time status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="status-indicator status-online"></div>
            <div class="metric-value">ONLINE</div>
            <div class="metric-label">System Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">98.7%</div>
            <div class="metric-label">Accuracy Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">0.3s</div>
            <div class="metric-label">Avg Response</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">2,847</div>
            <div class="metric-label">Transcriptions</div>
        </div>
        """, unsafe_allow_html=True)

    avs.add_vertical_space(3) if HAS_EXTRAS else st.markdown("<br><br>", unsafe_allow_html=True)

    # Main transcription interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if HAS_EXTRAS:
            with stylable_container(
                key="transcription_container",
                css_styles="""
                {
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    padding: 30px;
                    margin: 20px 0;
                }
                """
            ):
                st.markdown("### 🎤 Audio Input")
        else:
            st.markdown("### 🎤 Audio Input")
            
            # Recording controls
            col_rec1, col_rec2, col_rec3 = st.columns(3)
            
            with col_rec1:
                if st.button("🔴 Start Recording", use_container_width=True):
                    st.session_state.is_recording = True
                    st.session_state.processing_status = 'recording'
            
            with col_rec2:
                if st.button("⏹️ Stop Recording", use_container_width=True):
                    st.session_state.is_recording = False
                    st.session_state.processing_status = 'processing'
            
            with col_rec3:
                if st.button("🔄 Process Audio", use_container_width=True):
                    st.session_state.processing_status = 'transcribing'
            
            # Audio visualization
            if st.session_state.is_recording:
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
                <p class="holo-text" style="text-align: center;">🎙️ RECORDING IN PROGRESS...</p>
                """, unsafe_allow_html=True)
            
            # File upload option
            st.markdown("### 📁 Upload Audio File")
            uploaded_file = st.file_uploader(
                "Choose an audio file", 
                type=['wav', 'mp3', 'm4a', 'flac'],
                help="Upload your medical audio recording for transcription"
            )
            
            if uploaded_file is not None:
                st.audio(uploaded_file, format='audio/wav')
                
                if st.button("🚀 Transcribe Uploaded File", use_container_width=True):
                    with st.spinner("🧠 AI Processing..."):
                        # Simulate processing
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        # Generate sample transcription
                        sample_transcription = """
                        Patient presents with chief complaint of chest pain that started approximately 2 hours ago. 
                        Pain is described as sharp, 7 out of 10 in intensity, radiating to the left arm. 
                        Patient denies shortness of breath, nausea, or diaphoresis. 
                        Vital signs stable. Heart rate 88, blood pressure 128/82, oxygen saturation 98% on room air.
                        """
                        
                        st.success("✅ Transcription completed!")
                        st.markdown("### 📝 Transcription Result")
                        st.text_area("", sample_transcription, height=200)

    with col2:
        with st.container():
            st.markdown("### ⚙️ AI Settings")
            
            # Model selection
            model_choice = st.selectbox(
                "🤖 AI Model",
                ["MediGPT-4 Turbo", "HealthLLM-Pro", "MedicalWhisper-V3"],
                help="Select the AI model for transcription"
            )
            
            # Language settings
            language = st.selectbox(
                "🌐 Language",
                ["English (US)", "English (UK)", "Spanish", "French", "German"],
                help="Select transcription language"
            )
            
            # Specialty focus
            specialty = st.selectbox(
                "🏥 Medical Specialty",
                ["General Medicine", "Cardiology", "Neurology", "Orthopedics", "Pediatrics"],
                help="Optimize for specific medical specialty"
            )
            
            # Real-time toggle
            real_time = st.checkbox(
                "Real-time Processing",
                value=True,
                help="Enable real-time transcription processing"
            )
            
            # Confidence threshold
            confidence = st.slider(
                "🎯 Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.85,
                step=0.05,
                help="Minimum confidence for transcription acceptance"
            )
            
            # Auto-save
            auto_save = st.checkbox("💾 Auto-save transcriptions", value=True)
            
            # SOAP note generation
            generate_soap = st.checkbox("📋 Generate SOAP notes", value=True)
            
            st.markdown("### 🔊 Audio Quality")
            # Audio quality meter (simulated)
            quality_value = np.random.randint(85, 100)
            st.metric("Signal Quality", f"{quality_value}%", "2%")

elif selected == "📊 Analytics":
    if HAS_EXTRAS:
        colored_header(
            label="📊 Analytics Dashboard",
            description="Comprehensive insights into your transcription activities",
            color_name="blue-70"
        )
    else:
        st.markdown("# 📊 Analytics Dashboard")
        st.markdown("*Comprehensive insights into your transcription activities*")
    
    # Create sample data for charts
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    transcriptions_data = pd.DataFrame({
        'Date': dates,
        'Transcriptions': np.random.poisson(15, len(dates)),
        'Accuracy': np.random.normal(95, 3, len(dates)),
        'Processing_Time': np.random.exponential(2, len(dates))
    })
    
    # Metrics grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎯 Total Transcriptions",
            value="5,247",
            delta="247 this month"
        )
    
    with col2:
        st.metric(
            label="📈 Average Accuracy",
            value="97.3%",
            delta="1.2%"
        )
    
    with col3:
        st.metric(
            label="⚡ Avg Processing Time",
            value="1.8s",
            delta="-0.3s"
        )
    
    with col4:
        st.metric(
            label="💾 Storage Used",
            value="2.1 GB",
            delta="150 MB"
        )
    
    if HAS_EXTRAS:
        style_metric_cards()
    
    avs.add_vertical_space(2) if HAS_EXTRAS else st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Transcription volume chart
        fig_volume = px.line(
            transcriptions_data.tail(30), 
            x='Date', 
            y='Transcriptions',
            title='📈 Daily Transcription Volume (Last 30 Days)',
            color_discrete_sequence=['#667eea']
        )
        fig_volume.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig_volume, use_container_width=True)
    
    with col2:
        # Accuracy distribution
        fig_accuracy = px.histogram(
            transcriptions_data.tail(100),
            x='Accuracy',
            title='🎯 Accuracy Distribution',
            nbins=20,
            color_discrete_sequence=['#f093fb']
        )
        fig_accuracy.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig_accuracy, use_container_width=True)
    
    # Specialty breakdown
    specialty_data = {
        'Specialty': ['General Medicine', 'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics'],
        'Count': [1250, 850, 650, 450, 300],
        'Accuracy': [97.2, 98.1, 96.8, 97.5, 98.3]
    }
    
    fig_specialty = px.sunburst(
        values=specialty_data['Count'],
        names=specialty_data['Specialty'],
        title='🏥 Transcriptions by Medical Specialty'
    )
    fig_specialty.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig_specialty, use_container_width=True)

elif selected == "📋 History":
    if HAS_EXTRAS:
        colored_header(
            label="📋 Transcription History",
            description="View and manage your past transcriptions",
            color_name="green-70"
        )
    else:
        st.markdown("# 📋 Transcription History")
        st.markdown("*View and manage your past transcriptions*")
    
    # Search and filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("🔍 Search transcriptions", "")
    
    with col2:
        date_filter = st.date_input("📅 Date Range", datetime.now() - timedelta(days=30))
    
    with col3:
        specialty_filter = st.selectbox(
            "🏥 Filter by Specialty",
            ["All", "General Medicine", "Cardiology", "Neurology", "Orthopedics"]
        )
    
    avs.add_vertical_space(2) if HAS_EXTRAS else st.markdown("<br>", unsafe_allow_html=True)
    
    # Sample history data
    history_data = [
        {
            "Date": "2024-01-15 14:30",
            "Patient": "J.D. (ID: 12345)",
            "Specialty": "Cardiology",
            "Duration": "15:32",
            "Accuracy": "98.2%",
            "Status": "✅ Completed"
        },
        {
            "Date": "2024-01-15 13:15",
            "Patient": "M.S. (ID: 12346)",
            "Specialty": "General Medicine",
            "Duration": "08:45",
            "Accuracy": "97.8%",
            "Status": "✅ Completed"
        },
        {
            "Date": "2024-01-15 11:20",
            "Patient": "R.K. (ID: 12347)",
            "Specialty": "Neurology",
            "Duration": "22:18",
            "Accuracy": "96.9%",
            "Status": "📝 Review Required"
        }
    ]
    
    # Display history
    def _display_history_item(item, i):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        
        with col1:
            st.markdown(f"**📅 {item['Date']}**")
            st.markdown(f"👤 {item['Patient']}")
            st.markdown(f"🏥 {item['Specialty']}")
        
        with col2:
            st.markdown("**Duration**")
            st.markdown(f"⏱️ {item['Duration']}")
        
        with col3:
            st.markdown("**Accuracy**")
            st.markdown(f"🎯 {item['Accuracy']}")
        
        with col4:
            st.markdown("**Status**")
            st.markdown(item['Status'])
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                st.button("👁️ View", key=f"view_{i}")
            with col_btn2:
                st.button("📥 Export", key=f"export_{i}")
    
    for i, item in enumerate(history_data):
        if HAS_EXTRAS:
            with stylable_container(
                key=f"history_item_{i}",
                css_styles="""
                {
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(15px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 15px 0;
                    transition: all 0.3s ease;
                }
                """
            ):
                _display_history_item(item, i)
        else:
            _display_history_item(item, i)

else:  # Settings
    if HAS_EXTRAS:
        colored_header(
            label="⚙️ System Settings",
            description="Configure your MediSynth experience",
            color_name="violet-70"
        )
    else:
        st.markdown("# ⚙️ System Settings")
        st.markdown("*Configure your MediSynth experience*")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 General", "🤖 AI Models", "🔐 Security", "🎨 Appearance"])
    
    with tab1:
        st.subheader("🔧 General Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_language = st.selectbox(
                "🌐 Default Language",
                ["English (US)", "English (UK)", "Spanish", "French"]
            )
            
            auto_save_interval = st.slider(
                "💾 Auto-save Interval (minutes)",
                min_value=1,
                max_value=30,
                value=5
            )
            
            max_file_size = st.slider(
                "📁 Max File Size (MB)",
                min_value=10,
                max_value=500,
                value=100
            )
        
        with col2:
            notification_sounds = st.checkbox("🔔 Notification Sounds", value=True)
            email_notifications = st.checkbox("📧 Email Notifications", value=False)
            desktop_notifications = st.checkbox("💻 Desktop Notifications", value=True)
    
    with tab2:
        st.subheader("🤖 AI Model Configuration")
        
        st.markdown("### Primary Models")
        
        transcription_model = st.selectbox(
            "🎙️ Transcription Model",
            ["Whisper-Large-V3", "Wav2Vec2-XLSR", "SpeechT5"],
            help="Select the primary model for audio transcription"
        )
        
        nlp_model = st.selectbox(
            "📝 NLP Processing Model",
            ["GPT-4-Turbo", "Claude-3-Opus", "PaLM-2"],
            help="Select model for text processing and SOAP generation"
        )
        
        st.markdown("### Model Performance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🚀 Inference Speed", "0.3s", "-0.1s")
        
        with col2:
            st.metric("🎯 Model Accuracy", "98.7%", "0.5%")
        
        with col3:
            st.metric("💾 Memory Usage", "2.1 GB", "-0.3 GB")
    
    with tab3:
        st.subheader("🔐 Security & Privacy")
        
        st.markdown("### Data Protection")
        
        encryption_enabled = st.checkbox("🔒 Enable End-to-End Encryption", value=True)
        data_retention = st.slider(
            "📅 Data Retention Period (days)",
            min_value=30,
            max_value=365,
            value=90
        )
        
        st.markdown("### Access Control")
        
        two_factor_auth = st.checkbox("🔐 Two-Factor Authentication", value=True)
        session_timeout = st.slider(
            "⏰ Session Timeout (minutes)",
            min_value=15,
            max_value=480,
            value=60
        )
        
        st.markdown("### Compliance")
        
        hipaa_mode = st.checkbox("🏥 HIPAA Compliance Mode", value=True)
        audit_logging = st.checkbox("📊 Audit Logging", value=True)
    
    with tab4:
        st.subheader("🎨 Appearance & UI")
        
        col1, col2 = st.columns(2)
        
        with col1:
            theme_choice = st.selectbox(
                "🎨 Theme",
                ["Ultimate Dark", "Professional Light", "High Contrast", "Retro Terminal"]
            )
            
            animation_speed = st.slider(
                "⚡ Animation Speed",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.1
            )
        
        with col2:
            show_particles = st.checkbox("✨ Particle Effects", value=True)
            show_glassmorphism = st.checkbox("🌟 Glassmorphism Effects", value=True)
            show_animations = st.checkbox("🎬 UI Animations", value=True)

# Floating action button for quick actions
st.markdown("""
<div class="fab" onclick="alert('Quick Action!')">
    ⚡
</div>
""", unsafe_allow_html=True)

# Footer with status
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("🏥 **MediSynth Ultimate** - v3.0.0")

with col2:
    st.markdown("🚀 **Status:** All Systems Operational")

with col3:
    st.markdown(f"🕒 **Last Updated:** {datetime.now().strftime('%H:%M:%S')}")

# Footer info
st.markdown("*Next-generation medical transcription powered by advanced AI*")
