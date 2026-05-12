import customtkinter as ctk
from tkinter import filedialog
import threading
from backend import process_audio_full

# Renk Teması (Modern AI Palette)
COLORS = {
    "bg": "#0f172a",       # Çok koyu lacivert
    "sidebar": "#1e293b",  # Sidebar gri-lacivert
    "accent": "#3b82f6",   # Canlı mavi
    "text": "#f8fafc",     # Parlak beyaz
    "gradient_start": "#6366f1", # Indigo
    "gradient_end": "#a855f7"    # Mor
}

class AudioMindApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AudioMind AI Pro - V3.0")
        self.geometry("1100x850")
        self.configure(fg_color=COLORS["bg"])

        # 1. Yan Panel (Sidebar)
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLORS["sidebar"])
        self.sidebar.pack(side="left", fill="y")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="🎙️ AudioMind", font=("Segoe UI", 24, "bold"), text_color=COLORS["accent"])
        self.logo_label.pack(pady=(40, 60))

        # Mod Seçimi Yan Panelde Daha Şık Durur
        self.mode_label = ctk.CTkLabel(self.sidebar, text="Analiz Modu", font=("Segoe UI", 14, "bold"))
        self.mode_label.pack(pady=(20, 10))
        
        self.mode_var = ctk.StringVar(value="Genel")
        modes = ["Genel", "Toplantı", "Akademi/Ders", "Röportaj"]
        for mode in modes:
            rb = ctk.CTkRadioButton(self.sidebar, text=mode, variable=self.mode_var, value=mode, 
                                     hover_color=COLORS["accent"], border_color=COLORS["accent"])
            rb.pack(pady=10, padx=20, anchor="w")

        # 2. Ana Panel (Main Content)
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", fill="both", expand=True, padx=40, pady=20)

        # Karşılama Başlığı
        self.welcome_label = ctk.CTkLabel(self.main_content, text="Hoş Geldin, Mihriban", font=("Segoe UI", 28, "bold"))
        self.welcome_label.pack(pady=(20, 5), anchor="w")
        
        self.sub_label = ctk.CTkLabel(self.main_content, text="Ses dosyalarını akıllı raporlara dönüştür.", font=("Segoe UI", 16), text_color="#94a3b8")
        self.sub_label.pack(pady=(0, 40), anchor="w")

        # İşlem Kartı (Upload Card)
        self.card = ctk.CTkFrame(self.main_content, fg_color=COLORS["sidebar"], corner_radius=15)
        self.card.pack(fill="x", pady=10)

        self.select_button = ctk.CTkButton(self.card, text="📁 SES DOSYASI YÜKLE", command=self.start_process, 
                                           height=55, font=("Segoe UI", 16, "bold"), fg_color=COLORS["accent"], 
                                           hover_color="#2563eb")
        self.select_button.pack(pady=30, padx=30)

        # Progress Alanı
        self.status_label = ctk.CTkLabel(self.main_content, text="Analiz için hazır.", font=("Segoe UI", 13))
        self.status_label.pack(pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(self.main_content, height=12, width=700, 
                                                progress_color=COLORS["accent"], fg_color="#334155")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        # Sonuç Kutusu (Modern Cam Görünümü Efekti)
        self.result_box = ctk.CTkTextbox(self.main_content, font=("Consolas", 14), corner_radius=15, 
                                          fg_color="#020617", border_color="#334155", border_width=2)
        self.result_box.pack(pady=30, fill="both", expand=True)

    def update_ui(self, message, progress):
        self.status_label.configure(text=message)
        self.progress_bar.set(progress)
        self.update_idletasks()

    def start_process(self):
        file_path = filedialog.askopenfilename(filetypes=[("Ses Dosyaları", "*.m4a *.mp3 *.wav")])
        if file_path:
            mode = self.mode_var.get()
            self.result_box.delete("1.0", "end")
            threading.Thread(target=self.run_backend, args=(file_path, mode), daemon=True).start()

    def run_backend(self, path, mode):
        result = process_audio_full(path, self.update_ui, mode)
        self.result_box.insert("1.0", result)

if __name__ == "__main__":
    app = AudioMindApp()
    app.mainloop()