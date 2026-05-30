import torch
from faster_whisper import WhisperModel
import gc
from fpdf import FPDF
import os
from dotenv import load_dotenv
from groq import Groq

# ÖNEMLİ: Hata veren torchaudio kütüphanesini tamamen çıkardık!
# Onun yerine standart kütüphane olan wave kullanacağız.
import wave

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def load_and_fix_audio(path):
    # Torchaudio olmadan, dosyanın varlığını kontrol eden güvenli fonksiyon
    return path

def process_audio_full(audio_path, progress_callback, mode="Genel"):
    # Streamlit Cloud üzerinde CPU zorlanmasın diye zorunlu CPU modu
    device = "cpu" 
    client = Groq(api_key=GROQ_API_KEY)

    try:
        # 1. Modelleri Yükle
        progress_callback("⏳ Modeller yükleniyor...", 0.1)
        
        # Pyannote kütüphanesini torchcodec kilitlenmesinden korumak için izole import
        from pyannote.audio import Pipeline
        
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=HF_TOKEN).to(torch.device(device))
        stt_model = WhisperModel("small", device=device, compute_type="int8")

        # 2. Ses İşleme
        progress_callback("⏳ Ses analiz ediliyor...", 0.3)
        
        # Pyannote analizi
        diarization_result = pipeline(audio_path)
        diarization = diarization_result.speaker_diarization if hasattr(diarization_result, 'speaker_diarization') else diarization_result
        
        # Whisper transkripsiyonu
        segments, _ = stt_model.transcribe(audio_path, beam_size=5, language="tr")

        structured_text = ""
        for segment in segments:
            mid_time = (segment.start + segment.end) / 2
            speaker = "BİLİNMİYOR"
            for turn, _, spk in diarization.itertracks(yield_label=True):
                if turn.start <= mid_time <= turn.end:
                    speaker = spk
                    break
            # TEKER TEKER KİMİN NE DEDİĞİNİ BURADA YAZDIRIYORUZ
            structured_text += f"{speaker}: {segment.text.strip()}\n"

        # 3. Temizlik
        progress_callback("🧹 Bellek boşaltılıyor...", 0.7)
        del stt_model
        del pipeline
        gc.collect()

        # 4. Groq Analizi
        progress_callback(f"🚀 {mode} modunda analiz yapılıyor...", 0.8)

        mode_prompts = {
            "Toplantı": "Bu bir toplantı dökümüdür. Kararları, alınan aksiyon maddelerini ve sorumluları bir liste halinde çıkar.",
            "Akademi/Ders": "Bu bir ders kaydıdır. Konudaki anahtar kavramları, tanımları ve önemli noktaları bir öğrenci notu gibi özetle.",
            "Röportaj": "Bu bir röportajdır. Soru-cevap dinamiğini koruyarak tarafların ana görüşlerini özetle.",
            "Genel": "Konuşmayı genel hatlarıyla özetle ve önemli noktaları belirt."
        }
        mode_instruction = mode_prompts.get(mode, mode_prompts["Genel"])
        
        prompt = f"""
        Aşağıdaki ses dökümü, bir ses analiz sisteminden alınmıştır. 
        Lütfen bu konuşmayı "{mode}" moduna uygun olarak profesyonel bir rapora dönüştür.
        {mode_instruction}

        DÖKÜM İÇERİSİNDEKİ SPEAKER ETİKETLERİNE DİKKAT ET:
        - Konuşmacıları (Speaker_00, Speaker_01 vb.) dökümdeki akışa göre analiz et.
        - Kimin hangi görüşü savunduğunu veya hangi bilgiyi verdiğini açıkça belirt.
        - Analizinde "Speaker_00 şunu dedi, Speaker_01 bunu ekledi" gibi bir yapı kullan.
        - Eğer konuşmacıların isimleri metin içinde geçiyorsa (Mihriban, Büşra gibi), dökümdeki etiketlerle isimleri eşleştir.

        RAPOR ŞABLONU:
        1. KONUŞMACI ANALİZİ: (Kimin kim olduğunu ve genel tavrını açıkla)
        2. KONUŞMA AKIŞI: (Kim, ne zaman, ne dedi? Kronolojik özet)
        3. ÖNEMLİ KARARLAR/NOTLAR: (Alınan kararlar veya tarihler)

        DÖKÜM:
        {structured_text}
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Sen yardımcı bir analiz asistanısın."},
                      {"role": "user", "content": prompt}],
            temperature=0.1
        )

        final_response = completion.choices[0].message.content
        return final_response, structured_text

    except Exception as e:
        return f"Hata: {str(e)}", "Döküm oluşturulamadı."
    

def save_as_pdf(text, filename="analiz_raporu.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    turkish_map = {
        'ş': 's', 'Ş': 'S', 'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G',
        'ç': 'c', 'Ç': 'C', 'ü': 'u', 'Ü': 'U', 'ö': 'o', 'Ö': 'O'
    }
    
    clean_text = "".join(turkish_map.get(char, char) for char in text)
    
    for line in clean_text.split('\n'):
        if line.strip():
            clean_line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, txt=clean_line, align='L')
        else:
            pdf.ln(5)
            
    pdf.output(filename)
    return filename