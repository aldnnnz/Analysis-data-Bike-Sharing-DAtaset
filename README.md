# Dashboard Analisis Penyewaan Sepeda

Dashboard interaktif Streamlit untuk menganalisis pola penyewaan sepeda dan pengaruh faktor cuaca terhadap jumlah penyewaan.

## Fitur Dashboard

### 📊 Overview
- Ringkasan KPI (Total penyewaan, rata-rata, minimum, maksimum)
- Tren penyewaan sepeda harian
- Distribusi dan statistik penyewaan

### ⏰ Analisis Pola Waktu
Menjawab pertanyaan: **Bagaimana pola jumlah penyewaan sepeda berdasarkan waktu?**

Mencakup analisis:
- **Per Jam**: Pola penyewaan setiap jam dalam sehari (peak hours)
- **Hari Kerja vs Akhir Pekan**: Perbandingan penyewaan antara hari kerja dan akhir pekan/libur
- **Per Musim**: Pengaruh musim terhadap jumlah penyewaan
- **Detail Pola Jam**: Perbandingan pola per jam antara hari kerja dan akhir pekan

**Key Insights:**
- Penyewaan tertinggi terjadi pada jam sibuk (08:00 dan 17:00-18:00) untuk commuting
- Working day memiliki rata-rata penyewaan lebih tinggi dibanding akhir pekan (~22%)
- Musim Fall dan Summer menunjukkan penyewaan tertinggi

### 🌤️ Analisis Pengaruh Cuaca
Menjawab pertanyaan: **Bagaimana pengaruh kondisi cuaca terhadap penyewaan sepeda?**

Mencakup analisis:
- **Kondisi Cuaca**: Pengaruh kondisi cuaca (Clear, Mist/Cloudy, Light Rain/Snow, Heavy Rain/Snow)
- **Faktor Cuaca Individual**: Analisis terpisah untuk suhu, kelembapan, dan kecepatan angin
- **Korelasi**: Nilai korelasi antara faktor cuaca dan jumlah penyewaan

**Key Insights:**
- Cuaca cerah menghasilkan penyewaan tertinggi, heavy rain terendah
- Suhu positif berkorelasi kuat dengan penyewaan
- Kelembapan tinggi mengurangi jumlah penyewaan

### 👥 Analisis User Casual vs Registered
Analisis mendalam tentang perilaku pengguna casual dan registered:
- **Per Jam**: Pola penyewaan casual vs registered per jam
- **Per Musim**: Perbedaan preferensi musiman
- **Perbandingan Proporsi**: Rasio casual vs registered

**Key Insights:**
- Registered users mendominasi (~80%) total penyewaan
- Registered users menunjukkan pola commuting yang jelas (peak di jam sibuk)
- Casual users cenderung menggunakan sepeda untuk rekreasi (siang hingga sore)

## Persiapan

### Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### Struktur File
```
dashboard/
├── dashboard.py          # File aplikasi Streamlit utama
├── requirements.txt      # Daftar dependensi Python
├── README.md             # File dokumentasi ini
├── main_data.csv         # Data harian (optional, untuk referensi)
└── data/
    ├── day.csv           # Data penyewaan per hari
    └── hour.csv          # Data penyewaan per jam
```

## Cara Menjalankan Dashboard

### 1. Navigasi ke folder dashboard
```bash
cd dashboard
```

### 2. Jalankan aplikasi Streamlit
```bash
streamlit run dashboard.py
```

### 3. Buka di browser
Aplikasi akan otomatis membuka di browser pada URL `http://localhost:8501`

## Navigasi Dashboard

Gunakan sidebar di sebelah kiri untuk memilih halaman:

1. **📊 Overview** - Ringkasan umum dan tren penyewaan
2. **⏰ Analisis Pola Waktu** - Analisis berbasis waktu dan musim
3. **🌤️ Analisis Pengaruh Cuaca** - Analisis faktor cuaca
4. **👥 Analisis User Casual vs Registered** - Perbandingan tipe pengguna

## Data Source

- **day.csv**: Data agregat harian (731 baris, 16 kolom)
- **hour.csv**: Data agregat per jam (17,379 baris, 17 kolom)
- **Periode**: 2011-2012

## Teknologi

- **Streamlit**: Framework untuk dashboard web interaktif
- **Pandas**: Data manipulation dan analysis
- **Matplotlib & Seaborn**: Data visualization
- **NumPy**: Numerical computing

## Author

Muhammad Aldyn Ismail Putra  
CDCC525D6Y0081  
cdcc525d6y0081@student.devacademy.id

## Notes

- Dashboard menggunakan caching untuk performa optimal
- Semua visualisasi interaktif dan responsif
- Data ditampilkan dalam berbagai format (charts, metrics, tables)
- Insights dan interpretasi disediakan di setiap section
