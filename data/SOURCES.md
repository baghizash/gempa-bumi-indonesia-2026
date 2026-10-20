# Sumber Data — Gempa Bumi Indonesia 2015–2026

Diambil pada **20 Oktober 2026**. Dua sumber, peran berbeda, dinyatakan apa adanya.

## 1. BMKG — snapshot terkini (resmi, real-time)
Badan Meteorologi, Klimatologi, dan Geofisika (BMKG), API publik TEWS tanpa auth:
- `https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json` — gempa terbaru
  (saat pengambilan: M3,7 di laut 6 km Barat Laut Pulau Saringi, 20 Okt 2026
  18:28:11 WIB, dirasakan III di Kab. Sumbawa; file shakemap `20261020182811.mmi.jpg`)
- `https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json` — 15 gempa M5+ terbaru
- `https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.json` — 15 gempa dirasakan terbaru

File mentah tersimpan di `data/raw/bmkg_*.json`; versi tabelnya:
`data/bmkg_terkini.csv`, `data/bmkg_dirasakan.csv`, `data/bmkg_autogempa.csv`.
Endpoint ini hanya menyimpan kejadian terbaru (jendela bergeser), jadi dipakai
untuk bagian "Snapshot Oktober 2026", bukan untuk statistik historis.

## 2. USGS — katalog historis (tulang punggung analisis)
USGS FDSN Event Web Service (`earthquake.usgs.gov/fdsnws/event/1/query`,
format GeoJSON, tanpa API key), parameter:
- `starttime=2015-01-01`, `endtime=2026-10-20`
- Kotak batas Indonesia: lintang −11 s.d. 6, bujur 95 s.d. 141
- `minmagnitude=4.5`, `orderby=time`, `limit=20000`
- Hasil mentah: **10.841 kejadian** (`data/raw/usgs_katalog.geojson`)

Kolom yang dipakai: `time` (diubah ke WIB), `mag`, `magType`, `place`,
`tsunami` (flag 0/1), koordinat `[bujur, lintang, kedalaman_km]`, `id`.

## Aturan pembersihan & derivasi (scripts/assemble.py)
1. **Filter negara lain.** Kotak batas ikut menangkap pinggiran negara tetangga.
   Kejadian yang kolom `place`-nya berlabel Philippines, Malaysia,
   Papua New Guinea, atau Palau dikeluarkan: **1.246 kejadian**.
2. **Label "Timor Leste" dipertahankan (670 kejadian).** USGS melabeli gempa
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
5. Hasil akhir katalog: **9.595 kejadian** di `data/gempa_katalog_2015_2026.csv`.

## Batasan yang harus diketahui pembaca
- Katalog memakai ambang M≥4,5; gempa kecil yang hanya dicatat BMKG tidak masuk.
- Magnitudo USGS dapat berbeda tipis dari rilis BMKG untuk kejadian yang sama
  (metode & jaringan sensor berbeda). Untuk kejadian Oktober 2026, angka BMKG
  yang dikutip berasal dari snapshot BMKG sendiri.
- Flag `tsunami` USGS = gempa dinilai berpotensi tsunami oleh sistem peringatan;
  bukan bukti tsunami merusak benar-benar terjadi.
- Tahun 2026 parsial (s.d. 20 Oktober 2026).
