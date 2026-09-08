# 🏝️ SultraTravel — Sistem Informasi & Manajemen Pariwisata Sulawesi Tenggara

Aplikasi web berbasis **Streamlit** untuk menjelajahi, merencanakan, dan mengelola data
pariwisata Provinsi Sulawesi Tenggara dalam satu platform terpadu.

## ✨ Fitur Utama

| Fitur | Deskripsi |
|---|---|
| 🏠 **Beranda** | Ringkasan statistik pariwisata, kartu kategori yang bisa diklik langsung ke Direktori terfilter, grafik sebaran per kabupaten/kota, destinasi unggulan dengan foto, dan peta sebaran. |
| 🗺️ **Direktori & Peta ala Google Maps** | Pencarian, penyaringan, **pengurutan** (rating/nama/kabupaten), dan **pagination** untuk menjelajah puluhan destinasi dengan nyaman, lengkap dengan peta interaktif kustom (Leaflet): pencarian destinasi, tombol lokasi saya, **rute jalan sungguhan** (bukan garis lurus) via OSRM, mode tampilan Jalan/Satelit/Topografi, dan layar penuh. |
| 📷 **Foto Destinasi** | Destinasi unggulan menampilkan foto asli berlisensi bebas (Wikimedia Commons, dengan atribusi). Destinasi lain menampilkan ilustrasi placeholder bergradasi sesuai kategori — Admin dapat menambahkan foto asli kapan saja. |
| 💬 **Chatbot AI** | Asisten percakapan yang memahami maksud pertanyaan (pencarian, budget, keluarga, rute) menggunakan deteksi intent + pencarian TF-IDF/fuzzy matching, dengan kartu foto hasil pencarian. |
| 🧭 **AI Itinerary Planner** | Menyusun rencana perjalanan multi-hari otomatis berdasarkan durasi, minat, budget, dan titik keberangkatan, dengan rute yang dioptimalkan dan peta interaktif. |
| 🔐 **Panel Admin** | CRUD data destinasi (tambah/ubah/nonaktifkan/hapus) termasuk pengelolaan foto, dashboard statistik, log aktivitas, dan ekspor data ke CSV. |

## 📁 Struktur Proyek

```
sultra_tourism_app/
├── app.py                          # Entrypoint utama: konfigurasi global + st.navigation
├── views/
│   ├── beranda.py
│   ├── direktori.py
│   ├── chatbot_ai.py
│   ├── itinerary_planner.py
│   └── admin_panel.py
├── utils/
│   ├── database.py                 # Lapisan data (SQLite) + CRUD (termasuk foto)
│   ├── search_engine.py            # Mesin pencarian TF-IDF + fuzzy matching
│   ├── chatbot_engine.py           # Deteksi intent & generator respons
│   ├── itinerary_engine.py         # Algoritma penyusun itinerary
│   ├── leaflet_map.py              # Peta interaktif ala Google Maps (Leaflet + OSRM)
│   ├── photo_utils.py              # Manajemen foto (Wikimedia Commons + placeholder SVG)
│   ├── map_utils.py                # Utilitas perhitungan jarak (Haversine)
│   ├── styling.py                  # Tema visual (CSS) terpusat
│   └── auth.py                     # Autentikasi Panel Admin
├── data/
│   └── seed_wisata_sultra.csv      # Dataset awal (100 destinasi)
├── .streamlit/
│   ├── config.toml                 # Tema warna aplikasi
│   └── secrets.toml.example        # Contoh kredensial admin
└── requirements.txt
```

> **Catatan teknis penting:** navigasi antar halaman menggunakan `st.navigation()` /
> `st.Page()` (bukan folder ajaib `pages/` bawaan Streamlit). Ini disengaja — nama
> file di folder `views/` sengaja dibuat tanpa emoji/karakter khusus. Pendekatan lama
> yang menaruh emoji di NAMA FILE (mis. `1_🗺️_Direktori.py`) rawan menampilkan
> karakter rusak (mojibake) di sidebar ketika di-zip/unzip atau di-deploy di lingkungan
> dengan encoding berbeda, karena label navigasi otomatis Streamlit diambil dari nama
> file tersebut. Dengan `st.Page(..., title=..., icon=...)`, label dan ikon sidebar
> didefinisikan eksplisit di kode `app.py`, bukan dari nama file — sehingga tampilannya
> konsisten di semua platform.

## 🚀 Cara Menjalankan

1. **Instal dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

2. **(Opsional) Atur kredensial admin sendiri**, salin `.streamlit/secrets.toml.example`
   menjadi `.streamlit/secrets.toml`, lalu isi `admin_username` dan `admin_password_hash`.
   Untuk membuat hash password baru:
   ```bash
   python -c "import hashlib; print(hashlib.sha256('PASSWORD_ANDA'.encode()).hexdigest())"
   ```
   Jika `secrets.toml` tidak dibuat, aplikasi memakai kredensial default:
   **username: `admin`** / **password: `sultra2026`** — ganti sebelum deploy publik.

3. **Jalankan aplikasi:**
   ```bash
   streamlit run app.py
   ```

4. Database SQLite (`data/sultra_tourism.db`) akan otomatis dibuat dan diisi dari
   dataset awal saat pertama kali dijalankan.

## 📊 Tentang Dataset

Dataset berisi **100 destinasi** nyata di Sulawesi Tenggara yang mencakup **seluruh 17
kabupaten/kota** di provinsi ini, mencakup 5 kategori: bahari (38), alam (31), sejarah &
budaya (16), kuliner (9), dan religi (6). Sebagian besar dikompilasi dan ditulis ulang
dari informasi publik **Dinas Pariwisata Provinsi Sulawesi Tenggara**
(pariwisata.sultraprov.go.id) per kabupaten/kota dan kategori wisata, sebagai titik awal
yang jauh lebih lengkap dari sekadar destinasi populer.

**Catatan jujur soal cakupan:** situs resmi Dispar Sultra memblokir crawling otomatis
(robots.txt), sehingga data dikumpulkan secara manual & bertahap dari hasil pencarian,
bukan hasil crawl penuh seluruh halaman arsip situs (yang jumlahnya bisa ratusan artikel).
Koordinat sebagian bersifat **perkiraan** berdasarkan kecamatan/desa yang disebutkan
sumber, dan disarankan diverifikasi dengan GPS akurat melalui **Panel Admin** sebelum
dipakai untuk keperluan resmi. Panel Admin dirancang agar tim pengelola bisa terus
menambah, memperbaiki, dan memperkaya data secara mandiri kapan saja.

**Tentang pembaruan dataset di deployment yang sudah berjalan:** setiap kali aplikasi
dijalankan, sistem otomatis mengecek destinasi pada `data/seed_wisata_sultra.csv` yang
belum ada di database (dicocokkan berdasarkan nama) dan menambahkannya secara otomatis
— tanpa menghapus atau menimpa data yang sudah diedit/ditambahkan lewat Panel Admin.
Jadi jika Anda mengganti file CSV dengan versi yang lebih baru/lengkap, cukup jalankan
ulang aplikasinya (`streamlit run app.py`) — tidak perlu menghapus database secara manual.

## 📷 Tentang Foto Destinasi

- **5 destinasi unggulan** (Taman Nasional Wakatobi, Benteng Keraton Buton, Air Terjun
  Moramo, Masjid Al-Alam Kendari, Pulau Labengki) menampilkan foto **asli berlisensi
  bebas** dari Wikimedia Commons (CC BY-SA / domain publik), lengkap dengan atribusi
  yang tampil otomatis di bawah kartu foto.
- Destinasi lain menampilkan **ilustrasi placeholder** bergradasi sesuai kategori
  (dibuat orisinal sebagai SVG, tanpa hak cipta pihak lain) agar tampilan tetap rapi
  sebelum foto asli tersedia.
- Admin dapat menambahkan/mengganti foto kapan saja lewat **Panel Admin → Kelola Data
  → Edit**, dengan mengisi URL foto (mis. hasil unggah sendiri ke layanan hosting
  gambar, Wikimedia Commons, atau sumber berlisensi bebas lain) dan kredit sumbernya.

## 🗺️ Tentang Peta Interaktif

Peta dibangun dari nol memakai **Leaflet.js** (bukan sekadar embed peta statis) agar
punya pengalaman senyaman Google Maps:
- 🔍 Kotak pencarian destinasi dengan saran otomatis
- 📍 Tombol "Lokasi Saya" (memakai Geolocation API browser)
- 🧭 Tombol **"Rute ke sini"** di setiap marker — menghitung **rute jalan sungguhan**
  (mengikuti jalan raya, bukan garis lurus) lengkap dengan estimasi jarak & waktu
  tempuh, memakai layanan routing terbuka OSRM. Jika layanan routing tidak tersedia
  (mis. tidak ada koneksi internet), otomatis beralih ke estimasi jarak garis lurus.
- 🛰️ Tiga mode tampilan: Jalan (OpenStreetMap), Satelit (Esri), dan Topografi
- ⛶ Mode layar penuh
- Marker berkelompok (clustering) otomatis saat banyak destinasi berdekatan

**Catatan:** peta ini memuat data dari server ubin (tile) OpenStreetMap/Esri dan
layanan routing OSRM secara langsung dari browser pengguna saat aplikasi dijalankan
— pastikan perangkat yang menjalankan aplikasi terhubung internet agar peta tampil
dengan baik.

## 🧠 Catatan Teknis

- **Pencarian** menggunakan kombinasi TF-IDF cosine similarity + fuzzy matching
  (rapidfuzz) — ringan, cepat, dan tidak memerlukan koneksi internet atau model AI
  besar saat runtime, sehingga andal untuk deployment maupun demo langsung.
- **Itinerary Planner** menggunakan algoritma rule-based (skoring preferensi +
  nearest-neighbor heuristic berbasis jarak Haversine), bukan pemanggilan API
  AI berbayar, sehingga selalu siap pakai tanpa API key.
- **Database**: SQLite lokal (`data/sultra_tourism.db`). Untuk skala produksi/multi-
  pengguna simultan, disarankan migrasi ke PostgreSQL/MySQL.

## 🌐 Deployment ke Streamlit Community Cloud

1. Unggah folder ini ke repository GitHub.
2. Buka [share.streamlit.io](https://share.streamlit.io), hubungkan repo, pilih `app.py` sebagai entry point.
3. Tambahkan `admin_username` dan `admin_password_hash` melalui menu **Secrets** di dashboard Streamlit Cloud.

## 🔒 Keamanan

- Ganti kredensial admin default sebelum deployment publik.
- Pertimbangkan menambahkan rate-limiting/login attempt lock jika aplikasi
  diakses publik secara luas.

---
🏝️ **SultraTravel** — dibangun untuk mendukung promosi dan pengelolaan data pariwisata
daerah Sulawesi Tenggara secara digital.
