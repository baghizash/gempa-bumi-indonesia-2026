# Layout Dashboard Power BI — Gempa Bumi Indonesia 2015–2026

Empat halaman, 16:9. Pratinjau Halaman 1: `dashboard_preview_halaman1.png`.
Warna: navy `#1E3A8A` (utama), teal `#0E7C7B` (aksen), merah `#C0392B`
(bahaya/dangkal), amber `#D9A441` (waspada/menengah).

## Halaman 1 — Ringkasan Nasional
- Judul: "Gempa Bumi Indonesia 2015–2026 — Ringkasan"
- 5 kartu KPI: Total Gempa (9.595) · Gempa M5plus (2.233) · Gempa M6plus (155)
  · Magnitudo Maksimum (7,8) · Persen Dangkal (71,3%)
- Visual utama: Peta sebaran (built-in Map / Azure Maps) dari `fact_gempa`:
  Location = lintang+bujur (atau kategori Lokasi), Size = magnitudo,
  Legend/warna = kelas_kedalaman
- Kanan: Bar chart gempa per tahun (dim_tanggal[tahun] × Total Gempa)
- Catatan kaki: "2026 = data s.d. 20 Okt 2026. Sumber: USGS + BMKG (20 Okt 2026)."
- Slicer: tahun, kelas kedalaman

## Halaman 2 — Peta & Wilayah
- Peta penuh satu halaman (sama seperti Halaman 1, ukuran besar)
- Bar horizontal: 10 wilayah teraktif (dim_wilayah[wilayah] × Total Gempa)
- Tabel wilayah: jumlah, magnitudo maks, jumlah M6plus per wilayah
- Slicer: wilayah, rentang magnitudo

## Halaman 3 — Magnitudo & Kedalaman
- Histogram magnitudo (bin 0,25) atau bar per kelas magnitudo
- Bar kelas kedalaman + Persen Dangkal
- Scatter: magnitudo (X) vs kedalaman_km (Y, sumbu dibalik), warna kelas
- Kartu: Kedalaman Median (36,2 km) · Gempa Dangkal Besar (106)
- Teks insight: "Gempa dangkal + besar adalah kombinasi paling berpotensi
  merusak — 106 kali terjadi dalam 12 tahun."

## Halaman 4 — Tsunami & Snapshot Terkini
- Bar: Gempa Berflag Tsunami per tahun
- Tabel: 10 gempa terbesar 2015–2026 (tanggal, magnitudo, kedalaman,
  lokasi_usgs, wilayah)
- Panel snapshot BMKG (teks/manual, perbarui dari data/bmkg_terkini.csv):
  15 gempa M5+ terbaru — contoh saat pengambilan: M6,1 Kodi, Sumba Barat Daya
  (4 Okt 2026) dan M5,7 Pohuwato, Gorontalo (12 Okt 2026)
- Kotak metodologi: sumber data, aturan wilayah, kelas kedalaman, batasan
  (katalog USGS memakai kotak batas; label negara lain dikeluarkan)
