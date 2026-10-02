# Dashboard Produksi dan Ekspor Perikanan Tangkap Indonesia

UAS Visualisasi Data dan Informasi — Politeknik Statistika STIS.
Topik: **Data Berdimensi Tinggi (Multivariat)** + **Data Geospasial** + **Data Aliran (Ekspor)**.
Tema: Daya saing dan sebaran produksi perikanan tangkap Indonesia (BPS).

> Tema ini dipilih khusus karena **belum dipakai kelompok lain di kelas**
> (dicek terhadap daftar topik yang sudah diambil teman sekelas per 2 Okt
> 2026). Jangan ganti ke tema kemiskinan/IPM/ketenagakerjaan/migrasi/
> kesehatan/pendidikan/pertanian umum/gender/lingkungan — semua sudah
> diambil kelompok lain dengan variabel yang mirip.

## Cara menjalankan lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Struktur proyek
```
app.py                                    # aplikasi utama (3 tab)
geo_helpers.py                            # kerangka choropleth kab/kota (GeoJSON)
data/multivariat_provinsi.csv             # 34 provinsi, 8 variabel, semua TODO kecuali 1 sel
data/geospasial_kabkota_SAMPLE.csv        # data ASLI BPS tapi baru 19 dari ~500 kab/kota
data/aliran_ekspor_perikanan_SAMPLE.csv   # CONTOH struktur, ganti data ekspor BPS asli
requirements.txt
```

## ⚠️ Yang WAJIB kamu lengkapi sebelum submit

### 1. Multivariat (`data/multivariat_provinsi.csv`)
Semua kolom masih `TODO` kecuali `produksi_laut_ton` NTT (139.067 ton, 2022 —
sudah dikonfirmasi dari BPS Provinsi NTT). Isi 34 baris x 8 kolom dari tabel
BPS berikut (masing-masing provinsi punya tabel sendiri di situs BPS
provinsi, polanya: `<provinsi>.bps.go.id` > Tabel Statistik > Pertanian,
Kehutanan, Perikanan):
- Produksi Perikanan Tangkap Laut & Perairan Umum Menurut Provinsi
- Nilai Produksi Perikanan Tangkap Menurut Provinsi
- Produksi Perikanan Budidaya Menurut Provinsi
- Jumlah Rumah Tangga Usaha Perikanan (Sensus Pertanian/Susenas)
- PDRB Lapangan Usaha Perikanan Menurut Provinsi (ADHK/ADHB)
- Ekspor Perikanan per Provinsi Asal (jika tersedia) atau proxy dari BPS Statistik Ekspor Impor
- Jumlah Kapal Perikanan (Statistik Kelautan dan Perikanan BPS/KKP)

Tabel nasional ringkas juga tersedia di:
https://www.bps.go.id/id/statistics-table/2/MTA1NCMy/produksi-perikanan-tangkap-menurut-provinsi-subsektor-perikanan-laut.html

Cantumkan di setiap visualisasi: judul tabel, tahun data, URL, tanggal
akses, dan tulisan "Sumber: BPS" (wajib sesuai soal nomor 2b).

### 2. Geospasial (`data/geospasial_kabkota_SAMPLE.csv`)
19 baris pertama SUDAH data BPS asli (Sulawesi Selatan, 2021, sumber di
komentar file CSV). Ketentuan minimal soal: ±500 unit kab/kota se-Indonesia.
Langkah:
1. Untuk tiap provinsi, buka `<provinsi>.bps.go.id` > Tabel Statistik >
   Pertanian, Kehutanan, Perikanan > "Produksi Perikanan Tangkap Menurut
   Kabupaten/Kota". Pola URL/tabel konsisten antarprovinsi (33 provinsi lagi).
2. Gabungkan jadi satu CSV dengan kolom `kode_wilayah` (4 digit BPS) agar
   bisa di-join ke GeoJSON batas wilayah kab/kota.
3. Unduh GeoJSON kab/kota dari Portal Satu Data Indonesia /
   tanahair.indonesia.go.id, lalu pakai `geo_helpers.build_choropleth()`.
4. Tambahkan 1 jenis peta lain (proportional symbol sudah ada contohnya di
   versi sebelumnya — tinggal aktifkan lagi dengan kolom lat/lon kab/kota).

### 3. Aliran (`data/aliran_ekspor_perikanan_SAMPLE.csv`)
Ganti dengan data ekspor BPS Statistik Ekspor Impor, kode HS 03 (ikan dan
produk perikanan) menurut negara tujuan. Cari "Ekspor Menurut Kode HS dan
Negara Tujuan" di bps.go.id atau lewat WebAPI BPS. Minimal 15 negara (soal
sudah berisi 18 baris contoh sebagai acuan format).

## Deployment (Streamlit Community Cloud)
1. Push folder ini ke repo GitHub publik (lihat langkah git di bawah).
2. Buka https://share.streamlit.io → "New app" → pilih repo & branch →
   file utama `app.py` → Deploy.
3. Salin URL yang diberikan (format `https://<nama>.streamlit.app`) — ini
   alamat proyek yang dicantumkan di akhir makalah IEEE.
4. Pastikan tautan tetap aktif sampai nilai akhir diumumkan.

## Push ke GitHub
```bash
git init
git add .
git commit -m "UAS Visdat: dashboard perikanan tangkap Indonesia"
git branch -M main
git remote add origin https://github.com/<username>/<nama-repo>.git
git push -u origin main
```

## Deklarasi penggunaan AI
Sesuai poin 7 soal (integritas akademik): proyek ini dibantu alat AI
(Claude) untuk kerangka kode aplikasi, template makalah, dan penyusunan
struktur data. Data BPS, verifikasi angka, analisis akhir, dan keputusan
desain visualisasi tetap menjadi tanggung jawab mahasiswa. Cantumkan
kalimat deklarasi serupa di bagian Metodologi makalah.
