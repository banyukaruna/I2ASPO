# simulasi_chart.py
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

print("=== TAHAP 1: MEMBUAT DATA DUMMY KENDARAAN ===")
# Kita simulasikan pencatatan data kemacetan (PCU) setiap 10 menit
waktu_sekarang = datetime.now()
data_persimpangan = []

for i in range(10): # Membuat 10 data historis
    waktu_log = waktu_sekarang + timedelta(minutes=i*10)
    waktu_str = waktu_log.strftime("%H:%M")
    
    # Acak nilai beban jalan (Skor PCU) untuk Lajur Utara dan Lajur Timur
    pcu_utara = round(random.uniform(10.0, 50.0), 2)
    pcu_timur = round(random.uniform(10.0, 50.0), 2)
    
    data_persimpangan.append({
        "Jam": waktu_str,
        "PCU_Utara": pcu_utara,
        "PCU_Timur": pcu_timur
    })

print("Data dummy berhasil dibuat di memori.")


print("\n=== TAHAP 2: MENGOLAH DATA DENGAN PANDAS ===")
# Mengubah list data menjadi DataFrame (Tabel Pandas)
df = pd.DataFrame(data_persimpangan)

# Menampilkan tabel data di terminal agar bisa kita cek
print("\nTampilan Tabel DataFrame Pandas:")
print(df)

# Menyimpan tabel tersebut menjadi file CSV (Bisa dibuka di Excel)
df.to_csv("log_kepadatan.csv", index=False)
print("\nData berhasil diekspor menjadi file 'log_kepadatan.csv'.")


print("\n=== TAHAP 3: VISUALISASI GRAFIK DENGAN MATPLOTLIB ===")
# 1. Membuat kanvas grafik dengan ukuran (lebar=8 inci, tinggi=4 inci)
plt.figure(figsize=(8, 4))

# 2. Menggambar garis tren untuk Lajur Utara (Warna Biru, bentuk titik bulat 'o')
plt.plot(df["Jam"], df["PCU_Utara"], marker='o', color='b', linestyle='-', label='Lajur Utara')

# 3. Menggambar garis tren untuk Lajur Timur (Warna Merah, bentuk segitiga '^')
plt.plot(df["Jam"], df["PCU_Timur"], marker='^', color='r', linestyle='--', label='Lajur Timur')

# 4. Memberikan dekorasi teks pada grafik
plt.title("Tren Kepadatan Persimpangan Jalan (Skala PCU)", fontdict={'fontsize': 14, 'weight': 'bold'})
plt.xlabel("Waktu Log (Jam:Menit)")
plt.ylabel("Beban Jalan (Skala PCU)")

# 5. Mengaktifkan Grid (Garis-garis kotak latar belakang) dan Legenda (Keterangan warna garis)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend() # Memunculkan kotak label 'Lajur Utara' dan 'Lajur Timur'

# 6. Merapikan tata letak agar tidak terpotong
plt.tight_layout()

# 7. MENYIMPAN GRAFIK MENJADI GAMBAR PNG
plt.savefig("grafik_tren_kepadatan.png", dpi=150)
print("Grafik sukses digambar dan disimpan sebagai file 'grafik_tren_kepadatan.png'.")

# 8. Menampilkan jendela grafik ke layar komputer Anda
print("\nMenampilkan grafik ke layar... (Tutup jendela grafik untuk mengakhiri program)")
plt.show()
