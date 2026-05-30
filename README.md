# 🎙️ AudioMind AI

AudioMind AI is an advanced, production-ready audio transcription and intelligence tool that seamlessly combines **Speaker Diarization** and **Context-Aware Summarization**. 

The system features both a modern **Desktop UI (CustomTkinter)** and a scalable **Web UI (Streamlit)**.

## 🚀 Key Features
- **Speech-to-Text:** Powered by `Faster-Whisper (small)` for high-accuracy local and cloud transcription.
- **Speaker Diarization:** Integrates `Pyannote.audio 3.1` to separate speakers based on audio timestamps.
- **LLM Reasoning:** Utilizes `Llama 3.3 (70B)` via **Groq API** for sub-second, context-specific summaries.
- **Modular Framework:** Custom analytical insights for Meetings, Lectures, and Interviews.
- **Enterprise Ready:** One-click automated **PDF Report Generation**.

## 🛠️ Tech Stack
- **Core:** Python 3.12+, PyTorch (MPS/CPU)
- **GUI & Web:** CustomTkinter, Streamlit Cloud
- **AI Models:** Faster-Whisper, Pyannote 3.1, Llama 3.3

## 📦 System Architecture
1. Audio Preprocessing & Enhancement (`ffmpeg`)
2. Voice Activity Detection & Speaker Labeling (`Pyannote`)
3. Transcription & Semantic Segment Alignment (`Whisper`)
4. Prompt Engineering & Report Structuring (`Groq Cloud`)