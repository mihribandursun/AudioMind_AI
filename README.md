# 🎙️ AudioMind AI: LLM tabanlı Dinamik Ses Analiz ve Raporlama Sistemi

Bu proje, **Gedik Üniversitesi BLMS431 Derin Öğrenme** dersi kapsamında geliştirilmiş; yüklenen dinamik ses kayıtlarını yapay zeka bulut servisleri kullanarak transkript eden, konuşmacıları ayrıştıran (Diarization) ve seçilen modlara göre profesyonel analiz raporu üreten uçtan uca bir derin öğrenme uygulamasıdır.

🌐 **Canlı Demo Adresi:** [https://audiomind-ai.streamlit.app](https://audiomind-ai.streamlit.app)

---

## 🚀 Projenin Öne Çıkan Özellikleri (Bonus Maddeleri)
* **Canlı Dağıtım (Deployment):** Proje, Streamlit Cloud üzerinde 7/24 aktif çalışacak şekilde deploy edilmiştir.
* **Hibrit & Hafif Mimari:** Sunucu kısıtlamalarını aşmak için ses işleme ve doğal dil işleme süreçleri tamamen API tabanlı (Groq Cloud & Llama-3.3-70B) bir asenkron mimariye taşınmıştır.
* **Oturum Bazlı Akıllı Sohbet (Session-Based Context-Aware Chat):** Sistem, veri gizliliği (Data Privacy) ve sunucu kaynaklarını optimize etmek amacıyla "Stateless" (Durumsuz) bir mimariye sahiptir; yüklenen ses dosyaları ve eski analizler sunucuda depolanmaz, oturum kapanınca temizlenir. Ancak aktif oturumda, üretilen rapor üzerinde `st.session_state` mimarisi kullanılarak ardışık soru-cevap (ChatGPT deneyimi) yapılabilir; yapay zeka önceki mesajların bağlamını hafızasında korur.
* **Dinamik Raporlama:** Üretilen yapay zeka raporları anında Türkçe karakter uyumlu PDF formatına dönüştürülüp indirilebilir.

---

## 📊 Model Mimarisi ve Karşılaştırma

Sistemde iki farklı mimari yaklaşım test edilmiş ve bulut tabanlı büyük dil modellerinin doğruluk/hız avantajı metriklerle rapora eklenmiştir:

| Metrik | Yerel Mimari (Local Model) | Bulut Tabanlı Hibrit Mimari (Önerilen) |
| :--- | :--- | :--- |
| **Kullanılan Modeller** | Whisper-Small + Pyannote 3.1 | Whisper-Large-v3 + Llama-3.3-70B |
| **Ortam / Altyapı** | CPU / Streamlit Cloud Server | Groq API Cloud Server |
| **Ortalama İşlem Süresi** | ~120 saniye | **~3-5 saniye** |
| **Diarization Başarısı** | Düşük (FFmpeg/Decoder Hatası) | **Yüksek** (LLM Context Parsing) |
| **Dil Halüsinasyonu** | Yok | **Yok** (Sıkı System Prompt Koruması) |

---

## 🛠️ Kurulum ve Yerel Çalıştırma

Projeyi kendi yerel bilgisayarınızda adım adım kurup çalıştırmak için aşağıdaki komutları sırasıyla uygulayabilirsiniz:

1. **Depoyu yerel bilgisayarınıza klonlayın ve klasöre girin:**
```bash
git clone https://github.com/KULLANICI_ADIN/REPONUN_ADI.git
cd REPONUN_ADI
```
Adım 2: Gerekli tüm bağımlılıkları ve kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```
Adım 3: Projenin kök dizininde bir .env dosyası oluşturup API anahtarlarınızı kaydedin:
```env
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here
```
Adım 4: Uygulamayı yerel sunucuda başlatın:
```bash
streamlit run streamlit_app.py
```
