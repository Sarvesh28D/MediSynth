"""
Audio helper utilities for the MediSynth application
"""

import os
import subprocess
import platform
import streamlit as st

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

def display_ffmpeg_instructions():
    """Display instructions for installing FFmpeg."""
    st.error("⚠️ FFmpeg is required for audio recording but isn't installed or found in PATH.")
    
    if platform.system() == 'Windows':
        st.markdown("""
        ### Steps to install FFmpeg on Windows:
        
        1. Download the FFmpeg build from [FFmpeg.org](https://ffmpeg.org/download.html) or [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
        2. Extract the ZIP file to a location like `C:\ffmpeg`
        3. Add the bin folder to your PATH:
           - Search for "Environment Variables" in Windows
           - Edit the PATH variable and add the bin folder path (e.g., `C:\ffmpeg\bin`)
        4. Restart your computer and relaunch the app
        """)
    elif platform.system() == 'Darwin':  # macOS
        st.markdown("""
        ### Install FFmpeg on macOS:
        
        Using Homebrew:
        ```
        brew install ffmpeg
        ```
        
        Or using MacPorts:
        ```
        sudo port install ffmpeg
        ```
        """)
    else:  # Linux
        st.markdown("""
        ### Install FFmpeg on Linux:
        
        Ubuntu/Debian:
        ```
        sudo apt update
        sudo apt install ffmpeg
        ```
        
        Fedora:
        ```
        sudo dnf install ffmpeg
        ```
        """)

def setup_audio_environment():
    """Set up the audio recording environment and check dependencies."""
    if not check_ffmpeg_installed():
        display_ffmpeg_instructions()
        return False
    return True
