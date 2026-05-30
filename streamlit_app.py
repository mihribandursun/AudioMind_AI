import streamlit as st
from backend import process_audio_full, save_as_pdf, GROQ_API_KEY
from groq import Groq

st.set_page_config(page_title="AudioMind AI Pro", page_icon="🎙️", layout="wide")

# Modern, İç Karartmayan CSS Dokunuşları
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    .stButton>button { background-color: #3b82f6; color: white; border-radius: 8px; }
    .report-box { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ AudioMind AI Pro")
st.caption("Ses dosyalarınızı yükleyin, analiz edin ve akıllı raporunuzla doğrudan sohbet edin.")

mode = st.sidebar.selectbox("Analiz Modu", ["Genel", "Toplantı", "Akademi/Ders", "Röportaj"])
uploaded_file = st.file_uploader("Ses Dosyası Seçin (.m4a, .mp3, .wav)", type=["m4a", "mp3", "wav"])

# State yönetimi (Chat hafızası için)
if "report" not in st.session_state: st.session_state.report = ""
if "transcript" not in st.session_state: st.session_state.transcript = ""
if "chat_history" not in st.session_state: st.session_state.chat_history = []

if uploaded_file:
    with open("temp_audio.m4a", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("✨ Analizi ve Akışı Başlat", use_container_width=True):
        with st.status("İşlemler yürütülüyor...", expanded=True) as status:
            def st_callback(msg, progress): st.write(msg)
            # Backend'den hem raporu hem de ham diyalog akışını dönecek şekilde güncelleyeceğiz
            report, transcript = process_audio_full("temp_audio.m4a", st_callback, mode)
            st.session_state.report = report
            st.session_state.transcript = transcript
            status.update(label="Tamamlandı!", state="complete")

if st.session_state.report:
    # Yan yana iki panel: Sol tarafta Kimin ne dediği (Diarization), Sağ tarafta Yapay Zeka Raporu
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 1. Konuşma Akışı (Diarization)")
        st.text_area("Kimin ne dediği kronolojik sıra:", st.session_state.transcript, height=400)
        
    with col2:
        st.markdown("### 📊 2. Yapay Zeka Analiz Raporu")
        st.markdown(f"<div class='report-box'>{st.session_state.report}</div>", unsafe_allow_html=True)
        
        # PDF İndirme Butonu
        pdf_path = save_as_pdf(st.session_state.report, "analiz_raporu.pdf")
        with open(pdf_path, "rb") as f:
            st.download_button("📥 PDF Raporu İndir", data=f, file_name="AudioMind_Rapor.pdf", mime="application/pdf")

    st.markdown("---")
    
    # 🔥 YENİ ÖZELLİK: RAPORLA KONUŞ (AI CHAT)
    st.markdown("### 💬 3. AudioMind Chat (Rapora Dair Soru Sor)")
    st.write("Rapor veya konuşma akışı hakkında merak ettiğiniz detayları yapay zekaya sorun.")
    
    # Eski konuşmaları göster
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.write(msg["content"])
        
    user_question = st.chat_input("Konuşmada geçen detaylar hakkında soru sorun... (Örn: Büşra sınav için ne dedi?)")
    
    if user_question:
        with st.chat_message("user"): st.write(user_question)
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        # Groq ile chat yanıtı üretme (Dökümü bağlam olarak veriyoruz)
        client = Groq(api_key=GROQ_API_KEY)
        chat_prompt = f"Aşağıdaki konuşma dökümüne göre şu soruyu yanıtla:\nDöküm:\n{st.session_state.transcript}\n\nSoru: {user_question}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": chat_prompt}]
        )
        answer = completion.choices[0].message.content
        
        with st.chat_message("assistant"): st.write(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})