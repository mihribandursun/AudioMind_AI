import streamlit as st
import os

st.set_page_config(page_title="AudioMind AI Pro", page_icon="🎙️", layout="wide")

# 🎨 TASARIM VE RENK DÜZELTMELERİ (CSS)
# streamlit_app.py içindeki CSS alanını SADECE bununla değiştir:
# streamlit_app.py dosyanın en üstündeki CSS alanını TAMAMEN bunla değiştir:
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }
    
    /* Sol Menü (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #f8fafc !important;
        font-weight: 600;
    }
    
    /* Canlı Ana Buton (✨ Analizi Başlat) */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 10px !important;
    }
    
    /* Analiz ve Rapor Kartları */
    .report-card {
        background-color: #ffffff !important;
        padding: 24px !important;
        border-radius: 14px !important;
        border: 1px solid #e2e8f0 !important;
        color: #0f172a !important;
    }
    .transcript-box {
        background-color: #0f172a !important;
        color: #38bdf8 !important;
        padding: 20px !important;
        border-radius: 14px !important;
    }
    
    /* Chat Kutuları */
    [data-testid="stChatMessage"] {
        color: #0f172a !important;
        background-color: #e2e8f0 !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
    }
    [data-testid="stChatMessage"] p { color: #0f172a !important; }
    h1, h2, h3 { color: #1e3a8a !important; font-weight: 800 !important; }
            
    /* Kendi özel buton tasarımımız */
    .custom-pdf-btn {
        display: block;
        width: 100%;
        text-align: center;
        background: linear-gradient(135deg, #059669, #047857) !important;
        color: #ffffff !important;
        font-weight: bold !important;
        padding: 12px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-size: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: background 0.2s ease;
    }
    .custom-pdf-btn:hover {
        background: linear-gradient(135deg, #047857, #065f46) !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ AudioMind AI Pro")
st.caption("Ses dosyalarınızı yükleyin, analiz edin ve akıllı raporunuzla doğrudan sohbet edin.")
st.markdown("---")

st.sidebar.markdown("## ⚙️ Kontrol Paneli")
mode = st.sidebar.selectbox("Analiz Modu", ["Genel", "Toplantı", "Akademi/Ders", "Röportaj"])

uploaded_file = st.file_uploader("Ses Dosyası Seçin (.m4a, .mp3, .wav)", type=["m4a", "mp3", "wav"])

if "report" not in st.session_state: st.session_state.report = ""
if "transcript" not in st.session_state: st.session_state.transcript = ""
if "chat_history" not in st.session_state: st.session_state.chat_history = []

if uploaded_file:
    with open("temp_audio.m4a", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button(" ANALİZİ BAŞLAT", use_container_width=True):
        with st.status("🚀 AudioMind AI motorları çalışıyor...", expanded=True) as status:
            def st_callback(msg, progress): st.write(msg)
            
            from backend import process_audio_full, save_as_pdf, GROQ_API_KEY
            from groq import Groq
            
            report, transcript = process_audio_full("temp_audio.m4a", st_callback, mode)
            st.session_state.report = report
            st.session_state.transcript = transcript
            status.update(label="✅ Analiz Kusursuz Tamamlandı!", state="complete")

if st.session_state.report:
    from backend import save_as_pdf, GROQ_API_KEY
    from groq import Groq
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 👥 1. Konuşma Akışı (Diarization)")
        st.markdown(f"<div class='transcript-box'><pre style='color:inherit; background:none; border:none; padding:0;'>{st.session_state.transcript}</pre></div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("### 📊 2. Yapay Zeka Analiz Raporu")
        st.markdown(f"<div class='report-card'>{st.session_state.report}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='download-btn-container'>", unsafe_allow_html=True)
        pdf_path = save_as_pdf(st.session_state.report, "analiz_raporu.pdf")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        import base64
        b64 = base64.b64encode(pdf_bytes).decode()
        
        # Streamlit'in sistemine takılmayan, yazısı her an beyaz kalan gerçek HTML butonu
        custom_btn_html = f'<a href="data:application/pdf;base64,{b64}" download="AudioMind_Rapor.pdf" class="custom-pdf-btn">📥 PDF RAPORU İNDİR</a>'
        st.markdown(custom_btn_html, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💬 3. AudioMind Chat (Rapora Dair Soru Sor)")
    
    # 🚨 GEÇMİŞİ EKRANA BASAN KESİN DÖNGÜ (Artık kaybolamaz)
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): 
            st.write(msg["content"])
        
    user_question = st.chat_input("Konuşmada geçen detaylar hakkında soru sorun...")
    
    if user_question:
        # 1. Kullanıcı mesajını anında hafızaya ekle ve ekranda göster
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)
        
        # 2. Yapay zekaya dökümle birlikte soruyu sor
        client = Groq(api_key=GROQ_API_KEY)
        chat_prompt = f"Aşağıdaki konuşma dökümüne göre kullanıcı sorusunu net bir şekilde yanıtla:\nDöküm:\n{st.session_state.transcript}\n\nSoru: {user_question}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "Sen profesyonel bir analiz asistanısın. Tamamen akıcı, kurallara uygun ve temiz bir Türkçe ile cevap vermelisin. 'himselfini', 'hiện', 'current' gibi yabancı veya uydurma kelimeleri asla kullanma. Cümlelerin net olsun."
                },
                {
                    "role": "user", 
                    "content": f"Aşağıdaki konuşma dökümüne göre kullanıcı sorusunu net bir şekilde yanıtla:\nDöküm:\n{st.session_state.transcript}\n\nSoru: {user_question}"
                }
            ],
            temperature=0.1 # Sıcaklığı düşük tutuyoruz ki kafasına göre kelime uydurmasın

        )
        answer = completion.choices[0].message.content
        
        # 3. Asistan cevabını hafızaya ekle ve ekranda göster
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)
            
        # Kilitlenmeye sebep olan st.rerun() komutunu kaldırdık, 
        # Streamlit artık doğal akışıyla mesajları üst üste biriktirecek!