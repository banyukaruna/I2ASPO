"""
=====================================================================
SIMULASI GUI - PERSIMPANGAN LAMPU LALU LINTAS CERDAS
Berbasis Computer Vision (4 kamera/lajur) + Sensor Suara Sirine
=====================================================================

CATATAN PENTING:
- File ini HANYA berisi GUI + logika simulasi. Belum terhubung ke
  kamera/sensor suara asli.
- Jumlah kendaraan per jenis dan status sirine masih diinput/disimulasikan
  lewat GUI (spinbox, checkbox, slider) agar logika sistem bisa diuji
  dahulu sebelum integrasi computer vision (mis. YOLO) dan mikrofon.
- Untuk integrasi nyata nanti, cukup ganti isi fungsi:
    - ambil_data_kamera(arah)   -> hasil deteksi YOLO per lajur
    - ambil_data_sirine(arah)   -> hasil klasifikasi sensor suara
  lalu panggil fungsi tersebut menggantikan pembacaan nilai dari
  widget GUI di dalam method `tick()`.

Dependensi: hanya Python standard library (tkinter).
=====================================================================
"""

import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime

# ---------------------------------------------------------------
# KONFIGURASI GLOBAL
# ---------------------------------------------------------------
ARAH = ["Utara", "Selatan", "Timur", "Barat"]

JENIS_KENDARAAN = {
    "motor": {"label": "Motor", "bobot": 1},
    "mobil": {"label": "Mobil", "bobot": 2},
    "truk":  {"label": "Truk",  "bobot": 3},
    "bus":   {"label": "Bus",   "bobot": 3},
}

JENIS_DARURAT = ["Ambulans", "Pemadam Kebakaran", "Mobil Polisi"]

WAKTU_HIJAU_MIN = 10     # detik, durasi hijau minimum
WAKTU_HIJAU_MAX = 40     # detik, durasi hijau maksimum
WAKTU_KUNING = 3         # detik
AMBANG_SIRINE = 60       # % confidence minimal sensor suara agar valid
SKOR_MAKS_UNTUK_SKALA = 60  # skor kepadatan yang dianggap "penuh" saat skala ke durasi hijau

WARNA_MERAH = "#e74c3c"
WARNA_KUNING = "#f1c40f"
WARNA_HIJAU = "#2ecc71"
WARNA_ABU = "#7f8c8d"


class LajurPanel:
    """Merepresentasikan satu lajur/pendekat persimpangan (1 kamera simulasi)."""

    def __init__(self, parent, arah, on_change):
        self.arah = arah
        self.on_change = on_change

        self.frame = ttk.LabelFrame(parent, text=f"Lajur {arah} (Kamera Simulasi)", padding=8)

        # --- Variabel jumlah kendaraan per jenis ---
        self.var_jumlah = {}
        for i, (kode, info) in enumerate(JENIS_KENDARAAN.items()):
            var = tk.IntVar(value=0)
            var.trace_add("write", lambda *a: self.on_change())
            self.var_jumlah[kode] = var

            ttk.Label(self.frame, text=info["label"] + ":").grid(row=i, column=0, sticky="w", pady=2)
            sp = ttk.Spinbox(self.frame, from_=0, to=99, width=5, textvariable=var)
            sp.grid(row=i, column=1, sticky="w", padx=4)

        baris_berikut = len(JENIS_KENDARAAN)

        # --- Kendaraan darurat (gabungan dgn hasil computer vision) ---
        self.var_darurat = tk.BooleanVar(value=False)
        self.var_darurat.trace_add("write", lambda *a: self.on_change())
        chk = ttk.Checkbutton(
            self.frame, text="Kendaraan darurat terdeteksi (CV)",
            variable=self.var_darurat
        )
        chk.grid(row=baris_berikut, column=0, columnspan=2, sticky="w", pady=(8, 2))

        self.var_jenis_darurat = tk.StringVar(value=JENIS_DARURAT[0])
        cb = ttk.Combobox(
            self.frame, textvariable=self.var_jenis_darurat,
            values=JENIS_DARURAT, state="readonly", width=16
        )
        cb.grid(row=baris_berikut + 1, column=0, columnspan=2, sticky="w")

        # --- Sensor suara sirine (confidence 0-100%) ---
        ttk.Label(self.frame, text="Confidence sensor sirine (%):").grid(
            row=baris_berikut + 2, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        self.var_sirine = tk.IntVar(value=0)
        self.var_sirine.trace_add("write", lambda *a: self.on_change())
        scale = ttk.Scale(
            self.frame, from_=0, to=100, orient="horizontal",
            variable=self.var_sirine, command=lambda v: self.on_change()
        )
        scale.grid(row=baris_berikut + 3, column=0, columnspan=2, sticky="we")
        self.lbl_sirine_val = ttk.Label(self.frame, text="0%")
        self.lbl_sirine_val.grid(row=baris_berikut + 4, column=0, sticky="w")

        # --- Info skor kepadatan (dihitung otomatis) ---
        self.lbl_skor = ttk.Label(self.frame, text="Skor kepadatan: 0", font=("TkDefaultFont", 9, "bold"))
        self.lbl_skor.grid(row=baris_berikut + 5, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # --- Tombol acak (simulasi kamera menangkap kondisi baru) ---
        btn_acak = ttk.Button(self.frame, text="Acak Deteksi", command=self.acak_deteksi)
        btn_acak.grid(row=baris_berikut + 6, column=0, columnspan=2, sticky="we", pady=(6, 0))

    def acak_deteksi(self):
        """Simulasi 'kamera' menangkap kondisi lalu lintas baru secara acak."""
        for var in self.var_jumlah.values():
            var.set(random.randint(0, 20))
        ada_darurat = random.random() < 0.15  # 15% peluang ada kendaraan darurat
        self.var_darurat.set(ada_darurat)
        if ada_darurat:
            self.var_jenis_darurat.set(random.choice(JENIS_DARURAT))
            self.var_sirine.set(random.randint(40, 100))
        else:
            self.var_sirine.set(random.randint(0, 30))

    def hitung_skor(self):
        return sum(self.var_jumlah[k].get() * v["bobot"] for k, v in JENIS_KENDARAAN.items())

    def darurat_valid(self):
        """Kendaraan darurat dianggap valid jika CV mendeteksi ADA
        DAN sensor suara sirine confidence-nya melewati ambang."""
        return self.var_darurat.get() and self.var_sirine.get() >= AMBANG_SIRINE

    def refresh_tampilan(self):
        self.lbl_sirine_val.config(text=f"{self.var_sirine.get()}%")
        self.lbl_skor.config(text=f"Skor kepadatan: {self.hitung_skor()}")


class SimulasiLampuLaluLintasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulasi Persimpangan Lampu Lalu Lintas Cerdas (CV + Sensor Sirine)")
        self.root.geometry("1050x760")

        self.running = False
        self.state = "HIJAU"       # "HIJAU" atau "KUNING"
        self.aktif = 0             # index lajur yang sedang hijau
        self.sisa = WAKTU_HIJAU_MIN
        self.antrian_darurat = None
        self.mode_var = tk.StringVar(value="OTOMATIS")

        self._build_ui()
        self.aktifkan_hijau(ARAH[0], log_pesan="Inisialisasi: mulai dari Utara")

    # ---------------------------------------------------------
    # PEMBANGUNAN UI
    # ---------------------------------------------------------
    def _build_ui(self):
        judul = ttk.Label(
            self.root,
            text="Simulasi Sistem Lampu Lalu Lintas Cerdas — 4 Kamera Simulasi + Sensor Suara Sirine",
            font=("TkDefaultFont", 13, "bold")
        )
        judul.pack(pady=8)

        # ---- Canvas persimpangan ----
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10)

        self.canvas = tk.Canvas(top_frame, width=320, height=320, bg="#1c1c1c", highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=10, pady=5)
        self._gambar_persimpangan()

        # ---- Panel kontrol simulasi ----
        kontrol = ttk.LabelFrame(top_frame, text="Kontrol Simulasi", padding=10)
        kontrol.grid(row=0, column=1, sticky="n", padx=10, pady=5)

        self.btn_start = ttk.Button(kontrol, text="Mulai Simulasi", command=self.mulai_simulasi)
        self.btn_start.grid(row=0, column=0, sticky="we", pady=3)
        self.btn_stop = ttk.Button(kontrol, text="Hentikan", command=self.hentikan_simulasi, state="disabled")
        self.btn_stop.grid(row=1, column=0, sticky="we", pady=3)
        ttk.Button(kontrol, text="Acak Semua Lajur", command=self.acak_semua).grid(row=2, column=0, sticky="we", pady=3)

        ttk.Label(kontrol, text="Mode:").grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Radiobutton(kontrol, text="Otomatis (skor + darurat)", variable=self.mode_var,
                         value="OTOMATIS").grid(row=4, column=0, sticky="w")
        ttk.Radiobutton(kontrol, text="Manual (paksa hijau)", variable=self.mode_var,
                         value="MANUAL").grid(row=5, column=0, sticky="w")

        self.lbl_status = ttk.Label(kontrol, text="", font=("TkDefaultFont", 10, "bold"), foreground="#2ecc71")
        self.lbl_status.grid(row=6, column=0, sticky="w", pady=(12, 0))
        self.lbl_waktu = ttk.Label(kontrol, text="", font=("TkDefaultFont", 20, "bold"))
        self.lbl_waktu.grid(row=7, column=0, sticky="w")

        # ---- Panel 4 lajur (2x2) ----
        grid_frame = ttk.Frame(self.root)
        grid_frame.pack(fill="both", expand=False, padx=10, pady=5)

        self.panel = {}
        posisi = {"Utara": (0, 0), "Selatan": (0, 1), "Timur": (1, 0), "Barat": (1, 1)}
        for arah in ARAH:
            p = LajurPanel(grid_frame, arah, on_change=self.refresh_semua_panel)
            r, c = posisi[arah]
            p.frame.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            self.panel[arah] = p

            # tombol paksa hijau (manual mode) diletakkan lewat kontrol tambahan
            btn_manual = ttk.Button(
                p.frame, text=f"Paksa Hijau {arah}",
                command=lambda a=arah: self.paksa_hijau_manual(a)
            )
            btn_manual.grid(row=99, column=0, columnspan=2, sticky="we", pady=(6, 0))

        # ---- Log kejadian ----
        log_frame = ttk.LabelFrame(self.root, text="Log Keputusan Sistem", padding=6)
        log_frame.pack(fill="both", expand=True, padx=10, pady=8)

        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        self.log_text = tk.Text(log_frame, height=8, yscrollcommand=scrollbar.set, state="disabled")
        self.log_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)

    def _gambar_persimpangan(self):
        c = self.canvas
        c.delete("all")
        # jalan
        c.create_rectangle(120, 0, 200, 320, fill="#333333", outline="")
        c.create_rectangle(0, 120, 320, 200, fill="#333333", outline="")
        # marka
        for y in range(0, 320, 20):
            c.create_line(160, y, 160, y + 10, fill="white")
        for x in range(0, 320, 20):
            c.create_line(x, 160, x + 10, 160, fill="white")

        # lampu tiap arah: (x, y, arah)
        self.lampu_pos = {
            "Utara": (160, 40),
            "Selatan": (160, 280),
            "Timur": (280, 160),
            "Barat": (40, 160),
        }
        self.lampu_id = {}
        self.label_id = {}
        for arah, (x, y) in self.lampu_pos.items():
            oid = c.create_oval(x - 14, y - 14, x + 14, y + 14, fill=WARNA_MERAH, outline="white")
            self.lampu_id[arah] = oid
            lid = c.create_text(x, y + 26, text=arah, fill="white", font=("TkDefaultFont", 9, "bold"))
            self.label_id[arah] = lid

    # ---------------------------------------------------------
    # LOGIKA SIMULASI
    # ---------------------------------------------------------
    def log(self, pesan):
        waktu = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{waktu}] {pesan}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def refresh_semua_panel(self):
        for p in self.panel.values():
            p.refresh_tampilan()

    def acak_semua(self):
        for p in self.panel.values():
            p.acak_deteksi()
        self.log("Deteksi kamera & sensor sirine diacak ulang untuk semua lajur.")

    def cari_lajur_darurat_valid(self, kecuali=None):
        """Cari lajur dengan kendaraan darurat yang tervalidasi CV + sirine."""
        for arah in ARAH:
            if arah == kecuali:
                continue
            if self.panel[arah].darurat_valid():
                return arah
        return None

    def pilih_lajur_prioritas_tertinggi(self, kecuali=None):
        kandidat = [a for a in ARAH if a != kecuali] or ARAH
        skor_list = [(a, self.panel[a].hitung_skor()) for a in kandidat]
        skor_list.sort(key=lambda t: t[1], reverse=True)
        return skor_list[0][0]

    def hitung_durasi_hijau(self, arah):
        skor = self.panel[arah].hitung_skor()
        proporsi = min(skor / SKOR_MAKS_UNTUK_SKALA, 1.0)
        durasi = WAKTU_HIJAU_MIN + proporsi * (WAKTU_HIJAU_MAX - WAKTU_HIJAU_MIN)
        return int(round(durasi))

    def aktifkan_hijau(self, arah, log_pesan=None):
        self.aktif = arah
        self.state = "HIJAU"
        self.sisa = self.hitung_durasi_hijau(arah)
        self._update_lampu()
        if log_pesan:
            self.log(log_pesan)
        else:
            skor = self.panel[arah].hitung_skor()
            self.log(f"Hijau -> {arah} (skor kepadatan={skor}, durasi={self.sisa}s)")

    def mulai_transisi_kuning(self, alasan=None):
        self.state = "KUNING"
        self.sisa = WAKTU_KUNING
        self._update_lampu()
        if alasan:
            self.log(alasan)

    def pindah_ke_lajur_berikutnya(self):
        if self.antrian_darurat is not None:
            arah_baru = self.antrian_darurat
            self.antrian_darurat = None
            self.aktifkan_hijau(
                arah_baru,
                log_pesan=f"🚨 PRIORITAS DARURAT: hijau diberikan ke {arah_baru} "
                          f"({self.panel[arah_baru].var_jenis_darurat.get()}, "
                          f"sirine {self.panel[arah_baru].var_sirine.get()}%)"
            )
        else:
            arah_baru = self.pilih_lajur_prioritas_tertinggi(kecuali=self.aktif)
            self.aktifkan_hijau(arah_baru)

    def paksa_hijau_manual(self, arah):
        if self.mode_var.get() != "MANUAL":
            self.log("Tombol 'Paksa Hijau' hanya aktif pada Mode Manual.")
            return
        self.mulai_transisi_kuning(alasan=f"[MANUAL] Transisi kuning sebelum memaksa hijau ke {arah}")
        self.antrian_darurat = arah
        # langsung terapkan setelah kuning selesai secara alami lewat tick()

    def _update_lampu(self):
        for arah in ARAH:
            if arah == self.aktif and self.state == "HIJAU":
                warna = WARNA_HIJAU
            elif arah == self.aktif and self.state == "KUNING":
                warna = WARNA_KUNING
            else:
                warna = WARNA_MERAH
            self.canvas.itemconfig(self.lampu_id[arah], fill=warna)

        self.lbl_status.config(text=f"Status: {self.state} @ {self.aktif}")
        self.update_tampilan_waktu()

    def update_tampilan_waktu(self):
        self.lbl_waktu.config(text=f"{max(self.sisa, 0)} dtk")

    # ---------------------------------------------------------
    # LOOP UTAMA (dipanggil tiap 1 detik lewat root.after)
    # ---------------------------------------------------------
    def tick(self):
        if not self.running:
            return

        # 1) Cek preemption darurat (hanya berlaku saat mode OTOMATIS)
        if self.mode_var.get() == "OTOMATIS" and self.state == "HIJAU":
            arah_darurat = self.cari_lajur_darurat_valid(kecuali=self.aktif)
            if arah_darurat is not None and self.antrian_darurat is None:
                self.antrian_darurat = arah_darurat
                self.mulai_transisi_kuning(
                    alasan=f"Kendaraan darurat terverifikasi (CV+sirine) di {arah_darurat} -> "
                          f"memulai transisi kuning untuk preemption"
                )
                self.root.after(1000, self.tick)
                return

        # 2) Hitung mundur normal
        self.sisa -= 1
        self.update_tampilan_waktu()

        if self.sisa <= 0:
            if self.state == "HIJAU":
                self.mulai_transisi_kuning()
            elif self.state == "KUNING":
                self.pindah_ke_lajur_berikutnya()

        self.root.after(1000, self.tick)

    def mulai_simulasi(self):
        if self.running:
            return
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.log("=== Simulasi dimulai ===")
        self.tick()

    def hentikan_simulasi(self):
        self.running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.log("=== Simulasi dihentikan ===")


# ---------------------------------------------------------------
# TITIK MASUK
# ---------------------------------------------------------------
def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass
    app = SimulasiLampuLaluLintasApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
