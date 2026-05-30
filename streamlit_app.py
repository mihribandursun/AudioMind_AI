import streamlit as st
from backend import process_audio_full, save_as_pdf # save_as_pdf'i ekledik
import os

st.set_page_config(page_title="AudioMind AI Pro", page_icon="🎙️", layout="wide")

st.title("🎙️ AudioMind AI Pro")
st.write("Ses dosyalarınızı yükleyin, profesyonel PDF raporları oluşturun.")

# Yan Panel
mode = st.sidebar.selectbox("Analiz Modu", ["Genel", "Toplantı", "Akademi/Ders", "Röportaj"])

uploaded_file = st.file_uploader("Ses Dosyası Seçin (.m4a, .mp3, .wav)", type=["m4a", "mp3", "wav"])

if uploaded_file:
    with open("temp_audio.m4a", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("Analizi Başlat"):
        with st.status("Analiz ediliyor...", expanded=True) as status:
            def st_callback(msg, progress):
                st.write(msg)
            
            result = process_audio_full("temp_audio.m4a", st_callback, mode)
            status.update(label="Analiz Tamamlandı!", state="complete", expanded=False)
        
        st.markdown("### ✨ Analiz Sonucu")
        st.write(result)
        
        # --- PDF OLUŞTURMA VE İNDİRME BÖLÜMÜ ---
        # Önce arka planda PDF'i oluşturuyoruz
        pdf_path = save_as_pdf(result, "web_analiz_raporu.pdf")
        
        # Dosyayı Streamlit üzerinden kullanıcıya sunuyoruz
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 PDF Raporunu İndir",
                data=f,
                file_name="AudioMind_Analiz_Raporu.pdf",
                mime="application/pdf"
            )