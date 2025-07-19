#!/usr/bin/env python3
"""
Setup script for MediSynth Agent.
"""

import subprocess
import sys
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.9 or higher."""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def download_models():
    """Download required AI models."""
    print("🤖 Downloading AI models...")
    
    try:
        # Download Whisper model
        import whisper
        print("📥 Downloading Whisper model...")
        whisper.load_model("base")
        print("✅ Whisper model downloaded!")
        
        # Download medical NER model (will be cached on first use)
        print("📥 Medical NLP models will be downloaded on first use.")
        
        return True
    except Exception as e:
        print(f"⚠️ Error downloading models: {e}")
        print("Models will be downloaded automatically when first used.")
        return True


def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    
    directories = ["temp", "data", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    print("✅ Directories created!")


def setup_environment():
    """Setup environment configuration."""
    print("⚙️ Setting up environment...")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# MediSynth Agent Configuration
ASR_MODEL_SIZE=base
ASR_DEVICE=cpu
DEBUG_MODE=true
USE_GPU_FOR_NLP=false
STREAMLIT_PORT=8501
"""
        env_file.write_text(env_content)
        print("✅ Created .env configuration file")
    else:
        print("✅ Configuration file already exists")


def run_tests():
    """Run basic tests to verify installation."""
    print("🧪 Running basic tests...")
    
    try:
        # Test imports
        print("Testing imports...")
        
        import streamlit
        print("✅ Streamlit imported")
        
        import whisper
        print("✅ Whisper imported")
        
        import transformers
        print("✅ Transformers imported")
        
        # Test our modules
        from config import Config
        print("✅ Config module imported")
        
        print("✅ All tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def main():
    """Main setup function."""
    print("🩺 MediSynth Agent Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Download models
    download_models()
    
    # Setup environment
    setup_environment()
    
    # Run tests
    if run_tests():
        print("\n🎉 Setup completed successfully!")
        print("\nTo start the application:")
        print("  streamlit run main.py")
        print("\nOr using Docker:")
        print("  docker-compose up")
    else:
        print("\n⚠️ Setup completed with warnings.")
        print("Some tests failed, but the application may still work.")


if __name__ == "__main__":
    main()
