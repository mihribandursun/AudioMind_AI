import customtkinter as ctk
from tkinter import filedialog, messagebox # Mesaj kutusu ekledik
import threading
from backend import process_audio_full, save_as_pdf # save_as_pdf'i ekledik

# Renk Teması
COLORS = {
    "bg": "#f8fafc",       # Temiz soft beyaz
    "sidebar": "#0f172a",  # Sol panel koyu (kontrast için harika durur)
    "accent": "#3b82f6",   # Canlı mavi butonlar
    "text": "#1e293b"      # Okunabilir koyu gri metinler
}

class AudioMindApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AudioMind AI Pro - V3.1")
        self.geometry("1100x900")
        self.configure(fg_color=COLORS["bg"])

        # 1. Yan Panel (Sidebar)
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLORS["sidebar"])
        self.sidebar.pack(side="left", fill="y")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="🎙️ AudioMind", font=("Segoe UI", 24, "bold"), text_color=COLORS["accent"])
        self.logo_label.pack(pady=(40, 60))

        self.mode_label = ctk.CTkLabel(self.sidebar, text="Analiz Modu", font=("Segoe UI", 14, "bold"))
        self.mode_label.pack(pady=(20, 10))
        
        self.mode_var = ctk.StringVar(value="Genel")
        modes = ["Genel", "Toplantı", "Akademi/Ders", "Röportaj"]
        for mode in modes:
            rb = ctk.CTkRadioButton(self.sidebar, text=mode, variable=self.mode_var, value=mode, 
                                     hover_color=COLORS["accent"], border_color=COLORS["accent"])
            rb.pack(pady=10, padx=20, anchor="w")

        # 2. Ana Panel
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", fill="both", expand=True, padx=40, pady=20)

        self.welcome_label = ctk.CTkLabel(self.main_content, text="Hoş Geldin, Mihriban", font=("Segoe UI", 28, "bold"))
        self.welcome_label.pack(pady=(20, 5), anchor="w")
        
        self.sub_label = ctk.CTkLabel(self.main_content, text="Ses dosyalarını akıllı PDF raporlara dönüştür.", font=("Segoe UI", 16), text_color="#94a3b8")
        self.sub_label.pack(pady=(0, 40), anchor="w")

        self.card = ctk.CTkFrame(self.main_content, fg_color=COLORS["sidebar"], corner_radius=15)
        self.card.pack(fill="x", pady=10)

        self.select_button = ctk.CTkButton(self.card, text="📁 SES DOSYASI YÜKLE", command=self.start_process, 
                                           height=55, font=("Segoe UI", 16, "bold"), fg_color=COLORS["accent"])
        self.select_button.pack(pady=30, padx=30)

        self.status_label = ctk.CTkLabel(self.main_content, text="Analiz için hazır.")
        self.status_label.pack(pady=(10, 5))

        self.progress_bar = ctk.CTkProgressBar(self.main_content, height=12, width=700, progress_color=COLORS["accent"])
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.result_box = ctk.CTkTextbox(self.main_content, font=("Consolas", 14), corner_radius=15, 
                                          fg_color="#020617", border_color="#334155", border_width=2)
        self.result_box.pack(pady=20, fill="both", expand=True)

        # PDF Butonu (En Alta)
        self.download_button = ctk.CTkButton(self.main_content, text="📥 PDF OLARAK KAYDET", 
                                             command=self.download_report,
                                             fg_color=COLORS["success"], 
                                             hover_color="#059669",
                                             height=45,
                                             font=("Segoe UI", 14, "bold"))
        self.download_button.pack(pady=(0, 20))

    # FONKSİYONLAR (Doğru girinti seviyesi)
    
    def download_report(self):
        content = self.result_box.get("1.0", "end")
        if content.strip() and "🚀" not in content: # Boşsa veya henüz analiz başlamadıysa uyarı ver
            try:
                file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dosyası", "*.pdf")])
                if file_path:
                    save_as_pdf(content, file_path)
                    messagebox.showinfo("Başarılı", "Rapor PDF olarak kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"PDF oluşturulamadı: {e}")
        else:
            messagebox.showwarning("Uyarı", "Önce bir analiz yapmalısınız!")

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
        # backend artık 2 değer döndürdüğü için ikisini de karşılıyoruz
        result, structured_text = process_audio_full(path, self.update_ui, mode)
        
        # Önce arayüzdeki büyük kutuya yapay zeka raporunu yazdırıyoruz
        self.result_box.insert("1.0", result)
        
        # Durum çubuğunu güncelliyoruz
        self.status_label.configure(text="✅ Analiz ve Akış Başarıyla Tamamlandı!")

if __name__ == "__main__":
    app = AudioMindApp()
    app.mainloop()