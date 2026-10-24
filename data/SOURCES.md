# Sumber Data — Gempa Bumi Indonesia 2015–2026

Diambil pada **24 Oktober 2026** (pembaruan dari pengambilan pertama
20 Oktober 2026). Dua sumber, peran berbeda, dinyatakan apa adanya.

## 1. BMKG — snapshot terkini (resmi, real-time)
Badan Meteorologi, Klimatologi, dan Geofisika (BMKG), API publik TEWS tanpa auth:
- `https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json` — gempa terbaru
  (saat pengambilan: M5,2 di darat 6 km Barat Laut Lebong, Bengkulu, 22 Okt 2026
  17:57:49 WIB, dirasakan III di Kota Bengkulu dan Arga Makmur serta II–III di
  Curup; file shakemap `20261022175749.mmi.jpg`)
- `https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json` — 15 gempa M5+ terbaru
- `https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.json` — 15 gempa dirasakan terbaru

File mentah tersimpan di `data/raw/bmkg_*.json`; versi tabelnya:
`data/bmkg_terkini.csv`, `data/bmkg_dirasakan.csv`, `data/bmkg_autogempa.csv`.
Endpoint ini hanya menyimpan kejadian terbaru (jendela bergeser), jadi dipakai
untuk bagian "Snapshot Oktober 2026", bukan untuk statistik historis.

## 2. USGS — katalog historis (tulang punggung analisis)
USGS FDSN Event Web Service (`earthquake.usgs.gov/fdsnws/event/1/query`,
format GeoJSON, tanpa API key), parameter:
- `starttime=2015-01-01`, `endtime=2026-10-24`
- Kotak batas Indonesia: lintang −11 s.d. 6, bujur 95 s.d. 141
- `minmagnitude=4.5`, `orderby=time`, `limit=20000`
- Hasil mentah: **10.847 kejadian** (`data/raw/usgs_katalog.geojson`).
  Kejadian terakhir di katalog: 23 Oktober 2026 pukul 19:24 WIB
  (M4,5 di timur laut Lospalos, Timor Leste) — tidak ada kejadian M≥4,5
  baru pada 24 Oktober sampai saat pengambilan.

Kolom yang dipakai: `time` (diubah ke WIB), `mag`, `magType`, `place`,
`tsunami` (flag 0/1), koordinat `[bujur, lintang, kedalaman_km]`, `id`.

## Aturan pembersihan & derivasi (scripts/assemble.py)
1. **Filter negara lain.** Kotak batas ikut menangkap pinggiran negara tetangga.
   Kejadian yang kolom `place`-nya berlabel Philippines, Malaysia,
   Papua New Guinea, atau Palau dikeluarkan: **1.247 kejadian**.
2. **Label "Timor Leste" dipertahankan (672 kejadian).** USGS melabeli gempa
   dengan kota terdekat; episentrum kejadian ini berada di perairan Indonesia
   di utara/timur Pulau Timor (Selat Wetar, Laut Banda, sekitar P. Kisar,
   Wetar, Romang — wilayah NTT), hanya kota acuannya yang berada di Timor Leste.
   Contoh: gempa M7,3 tanggal 30 Des 2021 "125 km NNE of Lospalos".
3. **Wilayah** diturunkan berurutan: (a) nama laut/selat pada `place`
   (Laut Banda, Laut Maluku, Laut Seram, Laut Arafura, Laut Timor, Selat Sunda,
   Laut Jawa, Laut Flores, Laut Sawu, Laut Sulawesi, Samudra Hindia);
   (b) kotak koordinat pulau terdekat (Halmahera & Maluku Utara, Maluku
   (Seram & Buru), Sulawesi, Bali & Nusa Tenggara, Nusa Tenggara Timur, Jawa,
   Sumatera, Kalimantan, Papua); (c) sisanya "Lainnya/Lepas Pantai".
   Ini pendekatan (approximation) — batas kotak tidak mengikuti garis pantai.
4. **Kelas kedalaman**: Dangkal < 70 km · Menengah 70–300 km · Dalam > 300 km
   (konvensi umum seismologi).
5. Hasil akhir katalog: **9.600 kejadian** di `data/gempa_katalog_2015_2026.csv`.

## Catatan pembaruan 24 Oktober 2026
- Katalog bersih bertambah netto **5 kejadian** (9.595 → 9.600). Rinciannya:
  7 kejadian bersih baru masuk — 5 kejadian bertanggal 20–23 Oktober 2026
  (Abepura M4,5; Meulaboh M5,0; dua kejadian episentrum perairan utara/timur
  Timor M5,1 dan M4,5; Curup/Lebong M4,9) plus 2 sisipan telat yang baru
  diterbitkan USGS untuk 17 Agustus 2026 (Sungai Penuh M4,6) dan
  24 September 2026 (Tobelo M4,5) — dan 2 kejadian lama ditarik USGS dari
  katalog (Nabire 12 Okt 2026 M4,5 dan Tobelo 10 Sep 2026 M4,5).
- USGS juga merevisi magnitudo 3 kejadian lama: Kupang 30 Sep 2026
  M5,0 → M4,9; Ende 21 Agu 2026 M5,6 → M5,2; Maumere 26 Sep 2026
  M4,6 → M4,5. Karena revisi Kupang, jumlah M≥5 hanya bertambah 1
  (2.233 → 2.234) meski ada 2 kejadian M≥5 baru.
- Magnitudo USGS dan BMKG untuk kejadian yang sama bisa berbeda: gempa
  Lebong 22 Okt 2026 tercatat M4,9 oleh USGS dan M5,2 oleh BMKG;
  gempa Meulaboh 20 Okt 2026 tercatat M5,0 oleh USGS dan M5,4 oleh BMKG.

## Batasan yang harus diketahui pembaca
- Katalog memakai ambang M≥4,5; gempa kecil yang hanya dicatat BMKG tidak masuk.
- Magnitudo USGS dapat berbeda tipis dari rilis BMKG untuk kejadian yang sama
  (metode & jaringan sensor berbeda). Untuk kejadian Oktober 2026, angka BMKG
  yang dikutip berasal dari snapshot BMKG sendiri.
- Flag `tsunami` USGS = gempa dinilai berpotensi tsunami oleh sistem peringatan;
  bukan bukti tsunami merusak benar-benar terjadi.
- Tahun 2026 parsial (s.d. 24 Oktober 2026).
