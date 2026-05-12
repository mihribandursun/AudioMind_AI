# 🎙️ AudioMind AI 
**AI-Powered Speech Transcription & Smart Analysis System**

AudioMind AI, ses kayıtlarını metne dönüştüren ve ardından **Llama 3.3** kullanarak bağlamsal analiz yapan uçtan uca bir sistemdir.

## 🚀 Özellikler
- **Speaker Diarization:** Kimin ne zaman konuştuğunu ayırt eder.
- **Smart Transcription:** Faster-Whisper ile düşük kaynak tüketimli, yüksek doğruluklu döküm.
- **Context-Aware Analysis:** Groq API üzerinden Llama 3.3 ile modlara özel (Toplantı, Akademi, Röportaj) özetleme.
- **Hybrid UI:** Hem macOS/Windows (CustomTkinter) hem de Web (Streamlit) arayüzü.

## 🛠️ Teknoloji Stack'i
- **Models:** Pyannote/Speaker-Diarization, Faster-Whisper
- **LLM:** Meta Llama 3.3 (via Groq Cloud)
- **Frameworks:** CustomTkinter (Desktop), Streamlit (Web)
- **Processing:** Apple Silicon (MPS) & CPU optimization

## 📖 Nasıl Kullanılır?
1. API anahtarlarınızı `.env` dosyasına ekleyin.
2. `pip install -r requirements.txt` komutuyla bağımlılıkları yükleyin.
3. `python main.py` ile masaüstü uygulamasını başlatın.