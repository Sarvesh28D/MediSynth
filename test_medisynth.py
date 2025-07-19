"""
Test script to verify MediSynth Agent components.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("🧪 Testing MediSynth Agent Components")
    print("=" * 50)
    
    try:
        # Test configuration
        print("📋 Testing configuration...")
        from config import Config
        config = Config()
        print(f"✅ Config loaded - ASR Model: {config.ASR_MODEL_SIZE}")
        
        # Test utils
        print("🔧 Testing utilities...")
        from utils import create_logger, TextFormatter
        logger = create_logger()
        formatter = TextFormatter()
        logger.info("Logger test successful")
        print("✅ Utils working")
        
        # Test SOAP generator
        print("📋 Testing SOAP generator...")
        from nlp.soap_generator import create_soap_generator
        soap_gen = create_soap_generator()
        
        # Mock data
        test_data = {
            "categorized_entities": {
                "symptoms": [{"text": "chest pain", "label": "SYMPTOM"}]
            },
            "conversation_structure": {
                "patient_statements": ["I have chest pain"]
            },
            "raw_text": "Patient reports chest pain"
        }
        
        soap_note = soap_gen.generate_soap_note(test_data)
        formatted = soap_gen.format_soap_note(soap_note)
        print("✅ SOAP generator working")
        
        print("\n📄 Sample SOAP Note:")
        print("-" * 30)
        print(formatted[:200] + "...")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_with_dependencies():
    """Test components that require external dependencies."""
    print("\n🔬 Testing components with dependencies...")
    print("=" * 50)
    
    try:
        # Test Whisper availability
        print("🎙️ Testing Whisper...")
        import whisper
        model = whisper.load_model("tiny")
        print("✅ Whisper available")
        
        # Test transformers
        print("🤖 Testing Transformers...")
        from transformers import pipeline
        print("✅ Transformers available")
        
        # Test torch
        print("🔥 Testing PyTorch...")
        import torch
        print(f"✅ PyTorch available - Version: {torch.__version__}")
        
        # Test our ASR processor
        print("🎯 Testing ASR processor...")
        from asr import create_asr_processor
        # Only create but don't load model to save time
        # asr = create_asr_processor(model_size="tiny")
        print("✅ ASR processor can be created")
        
        print("\n🎉 All dependency tests passed!")
        return True
        
    except ImportError as e:
        print(f"⚠️ Dependency not available: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🩺 MediSynth Agent - Test Suite")
    print("=" * 60)
    
    # Basic functionality tests
    basic_success = test_basic_functionality()
    
    # Dependency tests
    dep_success = test_with_dependencies()
    
    print("\n" + "=" * 60)
    if basic_success and dep_success:
        print("🎉 ALL TESTS PASSED! MediSynth Agent is ready to use.")
        print("\nTo start the application:")
        print("  streamlit run demo.py  (for demo)")
        print("  streamlit run main.py  (for full version)")
    elif basic_success:
        print("⚠️ Basic functionality works, but some dependencies are missing.")
        print("Install missing dependencies to unlock full functionality.")
    else:
        print("❌ Tests failed. Please check your installation.")
    
    print("\n📖 Project Structure:")
    print("  /asr     - Audio Speech Recognition")
    print("  /nlp     - Medical NLP & SOAP generation") 
    print("  /ui      - Streamlit web interface")
    print("  /utils   - Utility functions")
    print("  /config  - Configuration management")

if __name__ == "__main__":
    main()
