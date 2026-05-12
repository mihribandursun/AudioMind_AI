import streamlit as st
from backend import process_audio_full
import os

st.set_page_config(page_title="AudioMind AI Pro", page_icon="🎙️", layout="wide")

st.title("🎙️ AudioMind AI Pro")
st.write("Ses dosyalarınızı yükleyin, saniyeler içinde profesyonel analiz alın.")

mode = st.sidebar.selectbox("Analiz Modu", ["Genel", "Toplantı", "Akademi/Ders", "Röportaj"])

uploaded_file = st.file_uploader("Ses Dosyası Seçin (.m4a, .mp3, .wav)", type=["m4a", "mp3", "wav"])

if uploaded_file:
    # Geçici dosya oluşturma (Streamlit dosyayı RAM'de tutar, backend diskte ister)
    with open("temp_audio.m4a", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("Analizi Başlat"):
        with st.status("Analiz ediliyor...", expanded=True) as status:
            # Backend'i çağırıyoruz (update_ui yerine Streamlit'in status'unu kullanacağız)
            def st_callback(msg, progress):
                st.write(msg)
            
            result = process_audio_full("temp_audio.m4a", st_callback, mode)
            status.update(label="Analiz Tamamlandı!", state="complete", expanded=False)
        
        st.markdown("### ✨ Analiz Sonucu")
        st.write(result)
        st.download_button("Raporu İndir (.txt)", result, file_name="analiz_raporu.txt")