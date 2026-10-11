# GUI_coba.py
import customtkinter as ctk
import random
#BUAT PERUBAHAN
# ===============================================================
# KONFIGURASI SISTEM MURNI (ISOLATED GLOBAL)
# ===============================================================
DAFTAR_LAJUR = ["Utara", "Timur", "Selatan", "Barat"]

BOBOT_KENDARAAN = {
    "Motor": 0.25,
    "Mobil": 1.0,
    "Truk": 2.5,
    "Bus": 2.0
}

FASE_HIJAU_MIN = 10     # Batas minimal waktu hijau (detik)
FASE_HIJAU_MAX = 40     # Batas maksimal waktu hijau (detik)
FASE_KUNING = 3         # Durasi lampu kuning (detik)

# Kode Warna UI Hexadecimal
HEX_RED = "#e74c3c"
HEX_YELLOW = "#f1c40f"
HEX_GREEN = "#2ecc71"
HEX_DARK_BG = "#1e2530"

# ===============================================================
# SUBSISTEM: INPUT DATA KENDARAAN (LAJUR PANEL CLASS)
# ===============================================================
class PanelInputLajur(ctk.CTkFrame):
    def __init__(self, parent, nama_lajur):
        super().__init__(parent, fg_color="#2d2d2d")
        self.nama_lajur = nama_lajur
        
        # Label Title Lajur
        ctk.CTkLabel(self, text=f"Data Kendaraan - {nama_lajur}", font=("Arial", 11, "bold"), text_color="#FFCC00").pack(pady=2)
        
        # Frame Kontainer Kotak Input
        grid_input = ctk.CTkFrame(self, fg_color="transparent")
        grid_input.pack(fill="x", padx=10, pady=2)
        grid_input.columnconfigure((0, 1, 2, 3), weight=1)
        
        # Simpan objek widget entry ke dalam dictionary
        self.kolom_input = {}
        
        for indeks, jenis in enumerate(BOBOT_KENDARAAN.keys()):
            ctk.CTkLabel(grid_input, text=jenis, font=("Arial", 10)).grid(row=0, column=indeks, padx=2, pady=1)
            
            kotak_teks = ctk.CTkEntry(grid_input, width=45, justify="center")
            kotak_teks.insert(0, str(random.randint(0, 10)))  # Nilai acak awal
            kotak_teks.grid(row=1, column=indeks, padx=2, pady=2)
            self.kolom_input[jenis] = kotak_teks

    def ambil_skor_bobot(self):
        """Menghitung total beban PCU lajur dari angka input user."""
        total_skor = 0.0
        for jenis, bobot in BOBOT_KENDARAAN.items():
            try:
                jumlah = int(self.kolom_input[jenis].get())
                total_skor += jumlah * bobot
            except ValueError:
                total_skor += 0.0
        return round(total_skor, 2)

    def acak_jumlah_kendaraan(self):
        """Mengisi kolom input dengan angka tiruan acak baru."""
        for kotak_teks in self.kolom_input.values():
            kotak_teks.delete(0, "end")
            kotak_teks.insert(0, str(random.randint(0, 20)))


# ===============================================================
# APLIKASI UTAMA: ENGINE GUI & CORE LOGIC SIMULATION
# ===============================================================
class TrafficGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Setup Window Utama Aplikasi
        self.title("Smart Traffic Control System - Isolated Engine")
        self.geometry("1450x850")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # --- STATE ENGINE SIMULASI INTERNAL (Murni Baru & Terisolasi) ---
        self.simulasi_aktif = False
        self.fase_saat_ini = "HIJAU"     # Status: "HIJAU" atau "KUNING"
        self.lajur_aktif = "Utara"        # Menunjukkan lajur mana yang sedang hijau
        self.hitung_mundur = 10          # Durasi detik yang tersisa
        self.lajur_terpaksa = None       # Menyimpan antrean paksa lajur dari mode manual
        
        # Konfigurasi Master Grid Layout
        self.grid_columnconfigure(0, weight=0, minsize=360) # Kolom Kontrol Kiri
        self.grid_columnconfigure(1, weight=1)              # Kolom Grafik Tengah
        self.grid_columnconfigure(2, weight=1)              # Kolom Kamera & Data
        self.grid_columnconfigure(3, weight=1)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0, minsize=120)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0, minsize=120)
        
        # Bangun Komponen Tampilan
        self.bangun_panel_kontrol_kiri()
        self.bangun_grid_simulasi_kanan()
        
        # Visualisasi awal status lampu
        self.sinkronisasi_tampilan_ui()

    # -----------------------------------------------------------
    # TATA LETAK UI & WIDGET GENERATOR
    # -----------------------------------------------------------
    def bangun_panel_kontrol_kiri(self):
        """Membangun bilah kendali simulasi di area sebelah kiri."""
        panel_kiri = ctk.CTkFrame(self, width=340, corner_radius=0, fg_color="#1e1e1e")
        panel_kiri.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(panel_kiri, text="PANEL KENDALI UTAMA", font=("Arial", 16, "bold"), text_color="#FFCC00").pack(pady=15)
        
        # Wadah Indikator Fisik Lampu
        bingkai_lampu = ctk.CTkFrame(panel_kiri, fg_color="#2b2b2b", border_width=1)
        bingkai_lampu.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(bingkai_lampu, text="Status Lampu Lalu Lintas", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.visual_lampu = {}
        for lajur in DAFTAR_LAJUR:
            baris = ctk.CTkFrame(bingkai_lampu, fg_color="transparent")
            baris.pack(fill="x", padx=20, pady=4)
            
            ctk.CTkLabel(baris, text=f"Lajur {lajur}: ", width=100, anchor="w").pack(side="left")
            
            bulatan = ctk.CTkFrame(baris, width=20, height=20, corner_radius=10, fg_color=HEX_RED)
            bulatan.pack(side="left", padx=10)
            self.visual_lampu[lajur] = bulatan
            
        # Papan Informasi Countdown Status
        bingkai_info = ctk.CTkFrame(panel_kiri, fg_color="#151515", border_width=1, border_color="#333333")
        bingkai_info.pack(fill="x", padx=15, pady=15)
        
        self.txt_status = ctk.CTkLabel(bingkai_info, text="Status: Non-Aktif", font=("Arial", 14, "bold"), text_color="yellow")
        self.txt_status.pack(pady=5)
        
        self.txt_timer = ctk.CTkLabel(bingkai_info, text="-- dtk", font=("Arial", 28, "bold"), text_color="#ffffff")
        self.txt_timer.pack(pady=5)
        
        # Pilihan Mode Operasional
        self.var_mode = ctk.StringVar(value="OTOMATIS")
        bingkai_mode = ctk.CTkFrame(panel_kiri, fg_color="transparent")
        bingkai_mode.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(bingkai_mode, text="Mode Kendali:", font=("Arial", 11, "bold")).pack(anchor="w", padx=5)
        ctk.CTkRadioButton(bingkai_mode, text="Otomatis (Adaptif PCU)", variable=self.var_mode, value="OTOMATIS").pack(anchor="w", padx=10, pady=2)
        ctk.CTkRadioButton(bingkai_mode, text="Manual (Paksa Klik)", variable=self.var_mode, value="MANUAL").pack(anchor="w", padx=10, pady=2)
        
        # Tombol Aksi Kendali
        self.btn_mulai = ctk.CTkButton(panel_kiri, text="Mulai Simulasi", fg_color="#27ae60", hover_color="#1e8449", command=self.action_mulai_simulasi)
        self.btn_mulai.pack(fill="x", padx=15, pady=5)
        
        self.btn_stop = ctk.CTkButton(panel_kiri, text="Hentikan Simulasi", fg_color="#c0392b", hover_color="#962d22", command=self.action_hentikan_simulasi, state="disabled")
        self.btn_stop.pack(fill="x", padx=15, pady=5)
        
        self.btn_acak = ctk.CTkButton(panel_kiri, text="Acak Semua Lajur", fg_color="#2980b9", hover_color="#1f618d", command=self.action_acak_input_kendaraan)
        self.btn_acak.pack(fill="x", padx=15, pady=5)

    def bangun_grid_simulasi_kanan(self):
        """Membangun penempatan layout grid 4 kamera dan grafik suara."""
        # --- KOLOM 1: WADAH GRAFIK ANALISIS (FRAME POLOS) ---
        f_suara1 = ctk.CTkFrame(self, fg_color=HEX_DARK_BG, border_width=1)
        f_suara1.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(f_suara1, text="[ Frame Data Suara 1 ]\n(Spectrogram Audio)", text_color="#5dade2").pack(expand=True)
        
        f_akustik1 = ctk.CTkFrame(self, fg_color="#151a21")
        f_akustik1.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(f_akustik1, text="Data Akustik 1", text_color="gray").pack(expand=True)
        
        f_suara2 = ctk.CTkFrame(self, fg_color=HEX_DARK_BG, border_width=1)
        f_suara2.grid(row=2, column=1, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(f_suara2, text="[ Frame Data Suara 2 ]\n(Spectrogram Audio)", text_color="#5dade2").pack(expand=True)
        
        f_akustik2 = ctk.CTkFrame(self, fg_color="#151a21")
        f_akustik2.grid(row=3, column=1, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(f_akustik2, text="Data Akustik 2", text_color="gray").pack(expand=True)

        # --- KOLOM 2 & 3: BLOK MONITOR KAMERA & DATA INPUT LAJUR ---
        self.kumpulan_panel = {}
        
        # Kamera 1 - Utara
        self.buat_box_kamera_simulasi(row=0, col=2, nomor=1, nama="Utara")
        self.kumpulan_panel["Utara"] = PanelInputLajur(self, "Utara")
        self.kumpulan_panel["Utara"].grid(row=1, column=2, sticky="nsew", padx=4, pady=4)
        
        # Kamera 2 - Timur
        self.buat_box_kamera_simulasi(row=0, col=3, nomor=2, nama="Timur")
        self.kumpulan_panel["Timur"] = PanelInputLajur(self, "Timur")
        self.kumpulan_panel["Timur"].grid(row=1, column=3, sticky="nsew", padx=4, pady=4)
        
        # Kamera 3 - Selatan
        self.buat_box_kamera_simulasi(row=2, col=2, nomor=3, nama="Selatan")
        self.kumpulan_panel["Selatan"] = PanelInputLajur(self, "Selatan")
        self.kumpulan_panel["Selatan"].grid(row=3, column=2, sticky="nsew", padx=4, pady=4)
        
        # Kamera 4 - Barat
        self.buat_box_kamera_simulasi(row=2, col=3, nomor=4, nama="Barat")
        self.kumpulan_panel["Barat"] = PanelInputLajur(self, "Barat")
        self.kumpulan_panel["Barat"].grid(row=3, column=3, sticky="nsew", padx=4, pady=4)

        # Pasang Tombol Paksa Manual di bagian bawah tiap-tiap blok data lajur
        for lajur in DAFTAR_LAJUR:
            btn_paksa = ctk.CTkButton(
                self.kumpulan_panel[lajur],
                text=f"Paksa Hijau {lajur}",
                width=120, 
                height=22, 
                fg_color="#34495e",
                command=lambda l=lajur: self.action_pemicu_manual_lajur(l)
            )
            btn_paksa.pack(pady=4)

    def buat_box_kamera_simulasi(self, row, col, nomor, nama):
        f = ctk.CTkFrame(self, fg_color="#242424", border_width=2, border_color="#555555")
        f.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(f, text=f"CAMERA {nomor}\n(Lajur {nama})", font=("Arial", 14, "bold")).pack(expand=True)

    # -----------------------------------------------------------
    # ENGINE CORE SIMULATION LOGIC (MURNI INDEPENDEN)
    # -----------------------------------------------------------
    def hitung_durasi_fase_hijau(self, lajur_target):
        """Menghitung durasi lampu hijau. Jika bobot seimbang, otomatis diset 40 detik."""
        skor = {l: self.kumpulan_panel[l].ambil_skor_bobot() for l in DAFTAR_LAJUR}
        
        # Aturan Khusus Permintaan Anda: Jika bobot/skor semua simpang bernilai sama besar
        if skor["Utara"] == skor["Timur"] == skor["Selatan"] == skor["Barat"]:
            return 40
            
        # Alokasi adaptif proporsional jika beban kendaraan bervariasi
        skor_lajur = skor[lajur_target]
        rasio = min(skor_lajur / 60.0, 1.0)
        detik_hitung = FASE_HIJAU_MIN + rasio * (FASE_HIJAU_MAX - FASE_HIJAU_MIN)
        return int(round(detik_hitung))

    def tentukan_lajur_paling_padat(self, lajur_kecuali):
        """Mencari lajur dengan antrean kendaraan paling padat untuk giliran berikutnya."""
        kandidat = [l for l in DAFTAR_LAJUR if l != lajur_kecuali]
        skor_tertinggi = -1
        lajur_terpilih = kandidat[0]
        
        for lajur in kandidat:
            skor_sekarang = self.kumpulan_panel[lajur].ambil_skor_bobot()
            if skor_sekarang > skor_tertinggi:
                skor_tertinggi = skor_sekarang
                lajur_terpilih = lajur
        return lajur_terpilih

    def hitung_durasi_fase_hijau(self, lajur_target):
        """
        Menghitung durasi lampu hijau secara proporsional adaptif.
        Catatan:
        1. Waktu total dari keempat simpang pasti selalu 120 detik.
        2. Waktu masing-masing simpang ditentukan dari perhitungan value (skor) setiap simpang.
        """
        # 1. Ambil skor/value dari masing-masing simpang saat ini
        skor_simpang = {
            "Utara": self.kumpulan_panel["Utara"].ambil_skor_bobot(),
            "Timur": self.kumpulan_panel["Timur"].ambil_skor_bobot(),
            "Selatan": self.kumpulan_panel["Selatan"].ambil_skor_bobot(),
            "Barat": self.kumpulan_panel["Barat"].ambil_skor_bobot()
        }
        
        total_skor = sum(skor_simpang.values())
        TOTAL_WAKTU_SIKLUS = 120
        
        # KONDISI 1: Jika semua simpang memiliki value sama atau kosong total (0)
        if skor_simpang["Utara"] == skor_simpang["Timur"] == skor_simpang["Selatan"] == skor_simpang["Barat"] or total_skor == 0:
            return 30  # 30 dtk x 4 simpang = 120 detik bersih
            
        # KONDISI 2: Jika value bervariasi (Dihitung proporsional dari value masing-masing)
        alokasi_waktu = {}
        waktu_terdistribusi = 0
        
        # Urutan daftar simpang agar konsisten dengan perputaran
        simpang_list = ["Utara", "Timur", "Selatan", "Barat"]
        
        for i, lajur in enumerate(simpang_list):
            if i == len(simpang_list) - 1:
                # Simpang terakhir mengambil sisa waktu agar total siklus tepat 120 detik (anti-selisih desimal)
                alokasi_waktu[lajur] = TOTAL_WAKTU_SIKLUS - waktu_terdistribusi
            else:
                # Rumus utama: (Value Simpang / Total Value Seluruh Simpang) * 120 detik
                porsi_waktu = int(round((skor_simpang[lajur] / total_skor) * TOTAL_WAKTU_SIKLUS))
                
                # Proteksi keamanan: pastikan tidak 0 detik agar lampu tidak mati (min 5 detik)
                porsi_waktu = max(porsi_waktu, 5)
                
                alokasi_waktu[lajur] = porsi_waktu
                waktu_terdistribusi += porsi_waktu
                
        # Mengembalikan durasi spesifik untuk lajur yang sedang diminta oleh mesin simulasi
        return alokasi_waktu[lajur_target]




    def sinkronisasi_tampilan_ui(self):
        """Memperbarui visualisasi warna bulatan lampu dan teks countdown di layar."""
        for lajur, widget in self.visual_lampu.items():
            if lajur == self.lajur_aktif:
                warna = HEX_GREEN if self.fase_saat_ini == "HIJAU" else HEX_YELLOW
            else:
                warna = HEX_RED
            widget.configure(fg_color=warna)
            
        if self.simulasi_aktif:
            warna_teks = HEX_GREEN if self.fase_saat_ini == "HIJAU" else HEX_YELLOW
            self.txt_status.configure(text=f"Status: {self.fase_saat_ini} @ {self.lajur_aktif}", text_color=warna_teks)
            self.txt_timer.configure(text=f"{max(self.hitung_mundur, 0)} dtk", text_color="#ffffff")
        else:
            self.txt_status.configure(text="Simulasi Dihentikan", text_color="orange")
            self.txt_timer.configure(text="-- dtk", text_color="gray")

    # -----------------------------------------------------------
    # INTERACTION & TIMING EVENTS
    # -----------------------------------------------------------
    def engine_simulation_ticker(self):
        """Fungsi ticker mandiri yang berjalan mundur 1 detik secara periodik."""
        if not self.simulasi_aktif:
            return
            
        self.hitung_mundur -= 1
        
        if self.hitung_mundur <= 0:
            self.siklus_transisi_fase()
            
        self.sinkronisasi_tampilan_ui()
        
        # Panggil kembali fungsi ticker ini tepat setelah 1000ms (1 detik)
        self.after(1000, self.engine_simulation_ticker)

    def action_mulai_simulasi(self):
        if self.simulasi_aktif:
            return
        self.simulasi_aktif = True
        self.btn_mulai.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.btn_acak.configure(state="disabled")
        
        # Reset fase awal dan hitung durasi hijau lajur aktif dari data input saat ini
        self.fase_saat_ini = "HIJAU"
        self.hitung_mundur = self.hitung_durasi_fase_hijau(self.lajur_aktif)
        
        self.sinkronisasi_tampilan_ui()
        self.engine_simulation_ticker()

    def action_hentikan_simulasi(self):
        self.simulasi_aktif = False
        self.btn_mulai.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.btn_acak.configure(state="normal")
        self.sinkronisasi_tampilan_ui()

    def action_acak_input_kendaraan(self):
        for panel in self.kumpulan_panel.values():
            panel.acak_jumlah_kendaraan()
        if self.fase_saat_ini == "HIJAU" and self.simulasi_aktif:
            self.hitung_mundur = self.hitung_durasi_fase_hijau(self.lajur_aktif)
            self.txt_timer.configure(text=f"{self.hitung_mundur} dtk")

    def action_pemicu_manual_lajur(self, lajur_tujuan):
        """Memaksa sistem memindahkan lampu hijau ke lajur pilihan (Hanya berfungsi pada Mode Manual)."""
        if self.var_mode.get() != "MANUAL" or not self.simulasi_aktif:
            return
        
        # Jika lajur yang diklik sudah sedang hijau, abaikan
        if lajur_tujuan == self.lajur_aktif and self.fase_saat_ini == "HIJAU":
            return
            
        # Pemicu transisi kuning terlebih dahulu sebelum pindah
        self.fase_saat_ini = "KUNING"
        self.hitung_mundur = FASE_KUNING
        self.lajur_terpaksa = lajur_tujuan
        self.sinkronisasi_tampilan_ui()

# ===============================================================
# APLIKASI RUNNER (MAIN LAUNCHER)
# ===============================================================
if __name__ == "__main__":
    app = TrafficGUI()
    app.mainloop()
