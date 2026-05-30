import os
import gc
from dotenv import load_dotenv
from groq import Groq
from fpdf import FPDF

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def process_audio_full(audio_path, progress_callback, mode="Genel"):
    client = Groq(api_key=GROQ_API_KEY)

    try:
        # 1. Aşama: Groq Cloud ile Ses Dönüştürme (Dinamik ve Genel)
        progress_callback("⏳ Ses dosyası Groq yapay zeka bulutuna yükleniyor...", 0.2)
        
        with open(audio_path, "rb") as file:
            # Bu fonksiyon yüklediğin her farklı sesi dinamik olarak metne çevirir
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), file.read()),
                model="whisper-large-v3",
                response_format="text",
                language="tr"
            )
        
        progress_callback("👥 Konuşmacılar analiz ediliyor ve ayrıştırılıyor...", 0.5)
        
        # Groq'tan gelen ham metni, içindeki konuşma akışına göre etiketlemesi için LLM'e veriyoruz.
        # Bu sayede sunucuda pyannote/torchaudio çökmesi yaşamadan diarization simüle edilmiş oluyor.
        diarization_prompt = f"""
        Aşağıdaki Türkçe ses dökümünü incele. Konuşmadaki ses geçişlerini ve bağlamı analiz ederek, 
        metni kronolojik bir konuşma akışına (Diarization) dönüştür. 
        Kimin ne zaman konuştuğunu tahmin ederek Speaker_00, Speaker_01 şeklinde satır satır ayır.

        METİN:
        {transcription}
        """
        
        diarization_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": diarization_prompt}],
            temperature=0.2
        )
        
        structured_text = diarization_completion.choices[0].message.content

        # 2. Aşama: Mod Raporlama
        progress_callback(f"🚀 Rapor {mode} moduna göre özelleştiriliyor...", 0.8)

        mode_prompts = {
            "Toplantı": "Bu bir toplantı dökümüdür. Kararları, alınan aksiyon maddelerini ve sorumluları bir liste halinde çıkar.",
            "Akademi/Ders": "Bu bir ders kaydıdır. Konudaki anahtar kavramları, tanımları ve önemli noktaları bir öğrenci notu gibi özetle.",
            "Röportaj": "Bu bir röportajdır. Soru-cevap dinamiğini koruyarak tarafların ana görüşlerini özetle.",
            "Genel": "Konuşmayı genel hatlarıyla özetle ve önemli noktaları belirt."
        }
        mode_instruction = mode_prompts.get(mode, mode_prompts["Genel"])
        
        report_prompt = f"""
        Aşağıdaki yapılandırılmış ses dökümünü "{mode}" moduna uygun olarak profesyonel bir rapora dönüştür.
        {mode_instruction}

        RAPOR ŞABLONU:
        1. KONUŞMACI ANALİZİ: (Konuşmacıların genel tavrını ve rollerini açıkla)
        2. KONUŞMA AKIŞI: (Kim, ne dedi? Kronolojik net özet)
        3. ÖNEMLİ KARARLAR/NOTLAR: (Varsa tarihler, kararlar ve önemli detaylar)

        DÖKÜM:
        {structured_text}
        """

        report_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Sen yardımcı bir analiz asistanısın."},
                      {"role": "user", "content": report_prompt}],
            temperature=0.1
        )

        final_response = report_completion.choices[0].message.content
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