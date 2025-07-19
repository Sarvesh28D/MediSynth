# MediSynth - AI-Powered Medical Transcription System

MediSynth is an advanced medical transcription system that combines real-time audio processing with clinical intelligence to streamline the healthcare documentation workflow.

## 🌟 Key Features

- **Real-Time Audio Processing** - Record and transcribe medical conversations in real-time
- **Clinical Entity Recognition** - Automatically identify symptoms, medications, conditions, and more
- **SOAP Note Generation** - Automatically generate structured clinical documentation
- **EHR Integration** - Seamlessly manage patient records and encounters
- **Modern UI** - Sleek, intuitive interface designed for healthcare professionals

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- FFmpeg (required for audio processing)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Sarvesh28D/MediSynth.git
cd MediSynth
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg:
   - Windows: Download from [FFmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` or equivalent

### Running the Application

```bash
streamlit run main.py
```

## 🏗️ Project Structure

```
MediSynth/
├── asr/                   # Automatic Speech Recognition modules
├── config/                # Configuration settings
├── data/                  # Sample data and resources
├── nlp/                   # Natural Language Processing modules
├── ui/                    # User interface components
├── utils/                # Utility functions
├── main.py               # Main application entry point
├── demo_*.py             # Various demo versions of the application
└── requirements.txt      # Python dependencies
```

## 🔧 Technologies Used

- **Streamlit** - Web application framework
- **audio-recorder-streamlit** - Real-time audio recording
- **Plotly** - Interactive data visualization
- **SQLite** - Embedded database for EHR management
- **Pandas & NumPy** - Data processing

## 🎨 UI Enhancements

The application features a modern, professional UI designed specifically for healthcare settings, with:

- Glassmorphism design elements
- Animated components
- Medical-specific color coding
- Responsive layout
- Interactive progress tracking

For more details on UI features, see [UI_ENHANCEMENTS.md](UI_ENHANCEMENTS.md).

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors

- Sarvesh D.

## 🙏 Acknowledgements

- OpenAI for AI development assistance
- Streamlit for the powerful app framework
- All the open-source libraries that made this project possible