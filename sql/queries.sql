-- ============================================================
-- Gempa Bumi Indonesia 2015-2026 — Query Verifikasi (SQLite)
-- Database: data/gempa_bumi.db (buat dengan scripts/load_to_sqlite.py)
-- Semua angka headline di README/PPT/modul bisa dicek di sini.
-- ============================================================

-- Q1. Total kejadian dan rentang magnitudo
SELECT COUNT(*) AS total_kejadian, MIN(magnitudo) AS mag_min,
       MAX(magnitudo) AS mag_maks, MAX(kedalaman_km) AS terdalam_km
FROM fact_gempa;

-- Q2. Jumlah gempa per tahun (2026 parsial, s.d. 24 Okt)
SELECT t.tahun, COUNT(*) AS jumlah
FROM fact_gempa f JOIN dim_tanggal t ON t.tanggal = f.tanggal
GROUP BY t.tahun ORDER BY t.tahun;

-- Q3. Hitungan kelas magnitudo: M5+, M6+, M7+
SELECT
  SUM(CASE WHEN magnitudo >= 5.0 THEN 1 ELSE 0 END) AS m5plus,
  SUM(CASE WHEN magnitudo >= 6.0 THEN 1 ELSE 0 END) AS m6plus,
  SUM(CASE WHEN magnitudo >= 7.0 THEN 1 ELSE 0 END) AS m7plus
FROM fact_gempa;

-- Q4. 10 gempa terbesar
SELECT tanggal, magnitudo, kedalaman_km, lokasi_usgs, wilayah, flag_tsunami
FROM fact_gempa ORDER BY magnitudo DESC LIMIT 10;

-- Q5. Kelas kedalaman: jumlah dan persentase
SELECT kelas_kedalaman, COUNT(*) AS jumlah,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM fact_gempa), 1) AS persen
FROM fact_gempa GROUP BY kelas_kedalaman;

-- Q6. Gempa dangkal yang besar (paling berpotensi merusak): dangkal + M6+
SELECT COUNT(*) AS dangkal_m6plus FROM fact_gempa
WHERE kelas_kedalaman = 'Dangkal (<70 km)' AND magnitudo >= 6.0;

-- Q7. Wilayah teraktif + magnitudo maksimum per wilayah
SELECT wilayah, COUNT(*) AS jumlah, MAX(magnitudo) AS mag_maks,
       SUM(CASE WHEN magnitudo >= 6.0 THEN 1 ELSE 0 END) AS m6plus
FROM fact_gempa GROUP BY wilayah ORDER BY jumlah DESC;

-- Q8. Gempa berflag tsunami (USGS) terbesar
SELECT tanggal, magnitudo, kedalaman_km, lokasi_usgs, wilayah
FROM fact_gempa WHERE flag_tsunami = 1 ORDER BY magnitudo DESC LIMIT 10;
