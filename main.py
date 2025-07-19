"""
MediSynth Agent - Main Application Entry Point

An AI-powered multimodal assistant for automating healthcare documentation.
This application processes doctor-patient conversations and generates structured SOAP notes.
"""

import sys
import warnings
from pathlib import Path

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main application entry point."""
    try:
        # Import and run the Ultimate Streamlit UI
        from ui import create_ui
        ui = create_ui()
        ui.run()
        
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("\nPlease install dependencies with:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
