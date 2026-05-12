import torch
from faster_whisper import WhisperModel
import torchaudio
from pyannote.audio import Pipeline
from groq import Groq
import gc


import os
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri sisteme yükle
load_dotenv()

# API ANAHTARLARINI SİSTEMDEN AL
# Artık kodun içinde şifre yazmıyor, sistem '.env' dosyasının içine bakıyor.
HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def load_and_fix_audio(path):
    waveform, sample_rate = torchaudio.load(path)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
        waveform = resampler(waveform)
    return {"waveform": waveform, "sample_rate": 16000}

# ANA FONKSİYON: Arayüz (main.py) bunu çağıracak
def process_audio_full(audio_path, progress_callback, mode="Genel"): # 'mode' eklendi
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    client = Groq(api_key=GROQ_API_KEY)

    try:
        # 1. Modelleri Yükle
        progress_callback("⏳ Modeller yükleniyor...", 0.1)
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=HF_TOKEN).to(device)
        stt_model = WhisperModel("small", device="cpu", compute_type="int8")

        # 2. Ses İşleme
        progress_callback("⏳ Ses analiz ediliyor...", 0.3)
        fixed_audio = load_and_fix_audio(audio_path)
        
        diarization_result = pipeline(fixed_audio)
        diarization = diarization_result.speaker_diarization if hasattr(diarization_result, 'speaker_diarization') else diarization_result
        segments, _ = stt_model.transcribe(audio_path, beam_size=5, language="tr")

        structured_text = ""
        for segment in segments:
            mid_time = (segment.start + segment.end) / 2
            speaker = "BİLİNMİYOR"
            for turn, _, spk in diarization.itertracks(yield_label=True):
                if turn.start <= mid_time <= turn.end:
                    speaker = spk
                    break
            structured_text += f"{speaker}: {segment.text.strip()}\n"

        # 3. Temizlik
        progress_callback("🧹 Bellek boşaltılıyor...", 0.7)
        del stt_model
        del pipeline
        gc.collect()

        # 4. Groq Analizi
        progress_callback(f" {mode} modunda analiz yapılıyor...", 0.8)

        # MODLARA GÖRE ÖZEL TALİMATLAR
        mode_prompts = {
            "Toplantı": "Bu bir toplantı dökümüdür. Kararları, alınan aksiyon maddelerini ve sorumluları bir liste halinde çıkar.",
            "Akademi/Ders": "Bu bir ders kaydıdır. Konudaki anahtar kavramları, tanımları ve önemli noktaları bir öğrenci notu gibi özetle.",
            "Röportaj": "Bu bir röportajdır. Soru-cevap dinamiğini koruyarak tarafların ana görüşlerini özetle.",
            "Genel": "Konuşmayı genel hatlarıyla özetle ve önemli noktaları belirt."
        }

        mode_instruction = mode_prompts.get(mode, mode_prompts["Genel"])
        
        # PROMPT İÇİNE mode_instruction'ı yerleştiriyoruz!
        prompt = f"""
        Sen profesyonel bir analiz uzmanısın.
        ÖZEL TALİMAT: {mode_instruction}
        
        KURALLAR:
        1. İSİM EŞLEŞTİRME: Metinden isimleri bul ve SPEAKER etiketlerini kaldır.
        2. HATA DÜZELTME: 'İlirden' -> 'İleri Derin Öğrenme' gibi hataları düzelt.
        3. AKIŞ: 'BİLİNMİYOR' kısımlarını akışa göre doğru kişiye ata.
        4. TARİH: 14 Nisan'da konuşuluyorsa ve 'gelecek ay' deniyorsa 23 Mayıs olduğunu belirt.

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
        return final_response

    except Exception as e:
        return f"Hata: {str(e)}"