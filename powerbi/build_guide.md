# Panduan Rakit Dashboard Power BI — Langkah demi Langkah

Untuk Power BI Desktop (Windows). Estimasi waktu: 30–45 menit.

## 1. Import data
1. Buka Power BI Desktop → **Get Data → Text/CSV**, import tiga file di folder ini:
   `fact_gempa.csv`, `dim_tanggal.csv`, `dim_wilayah.csv`.
2. Cek tipe data: `tanggal` = Date; `magnitudo`, `kedalaman_km`, `lintang`,
   `bujur` = Decimal Number; `flag_tsunami` = Whole Number.
3. Untuk kolom `lintang`/`bujur`: set **Data Category** = Latitude / Longitude
   (tab Column tools) supaya visual peta akurat.

## 2. Buat relasi (Model view)
- `dim_tanggal[tanggal]` → `fact_gempa[tanggal]` (many-to-one, single direction)
- `dim_wilayah[wilayah]` → `fact_gempa[wilayah]` (many-to-one, single direction)
- Tandai `dim_tanggal` sebagai **date table** (klik kanan tabel → Mark as date table).

## 3. Tempel measure DAX
Buat tabel measure baru (Modeling → New measure), salin satu per satu dari
`measures_dax.md`. Format `Persen Dangkal` sebagai Percentage, `Magnitudo
Maksimum` dengan 1 desimal.

## 4. Bangun halaman mengikuti `dashboard_layout.md`
- Halaman 1: 5 kartu KPI + peta + bar per tahun + catatan kaki 2026 parsial.
- Untuk peta: pakai visual **Map** atau **Azure Maps**; tarik `lintang` ke
  Latitude, `bujur` ke Longitude, `magnitudo` ke Bubble size, `kelas_kedalaman`
  ke Legend.
- Samakan warna: dangkal = merah `#C0392B`, menengah = amber `#D9A441`,
  dalam = teal `#0E7C7B`.

## 5. Verifikasi sebelum publish
Bandingkan kartu KPI Halaman 1 dengan tabel verifikasi di `measures_dax.md`:
Total 9.595 · M5plus 2.233 · M6plus 155 · M7plus 16 · Maks 7,8 ·
Persen Dangkal 71,3%. Kalau beda, periksa: (a) slicer/filter yang tertinggal,
(b) relasi yang belum aktif, (c) tipe data magnitudo terbaca sebagai teks.

## 6. Memperbarui snapshot BMKG
Halaman 4 berisi snapshot manual. Untuk memperbarui: jalankan
`scripts/fetch_data.py` lalu `scripts/assemble.py` di repo, buka
`data/bmkg_terkini.csv` terbaru, dan sesuaikan teks/tabel snapshot.
Katalog historis diperbarui dengan menjalankan ulang seluruh pipeline
(fetch → assemble → analyze → build_powerbi) lalu refresh data di Power BI.
