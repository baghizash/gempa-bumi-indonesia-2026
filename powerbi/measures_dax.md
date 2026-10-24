# Measure DAX — Dashboard Gempa Bumi Indonesia

Tempel measure ini di Power BI Desktop setelah relasi model dibuat
(lihat `build_guide.md`). Semua measure membaca **satu grain saja**:
`fact_gempa` berisi 1 baris = 1 kejadian, tanpa baris agregat/rangkuman —
jadi tidak ada jebakan campuran level seperti pada tabel yang menggabung
baris nasional + provinsi.

```dax
Total Gempa =
COUNTROWS ( fact_gempa )

Gempa M5plus =
CALCULATE ( [Total Gempa], fact_gempa[magnitudo] >= 5.0 )

Gempa M6plus =
CALCULATE ( [Total Gempa], fact_gempa[magnitudo] >= 6.0 )

Gempa M7plus =
CALCULATE ( [Total Gempa], fact_gempa[magnitudo] >= 7.0 )

Magnitudo Maksimum =
MAX ( fact_gempa[magnitudo] )

Kedalaman Median =
MEDIAN ( fact_gempa[kedalaman_km] )

Persen Dangkal =
DIVIDE (
    CALCULATE ( [Total Gempa], fact_gempa[kelas_kedalaman] = "Dangkal (<70 km)" ),
    [Total Gempa]
)

Gempa Dangkal Besar =
CALCULATE (
    [Total Gempa],
    fact_gempa[kelas_kedalaman] = "Dangkal (<70 km)",
    fact_gempa[magnitudo] >= 6.0
)

Gempa Berflag Tsunami =
CALCULATE ( [Total Gempa], fact_gempa[flag_tsunami] = 1 )
```

## Nilai verifikasi (harus sama dengan hasil dashboard)

| Measure | Nilai benar |
|---|---|
| Total Gempa | 9.600 |
| Gempa M5plus | 2.234 |
| Gempa M6plus | 155 |
| Gempa M7plus | 16 |
| Magnitudo Maksimum | 7,8 (Ende, NTT — 15 Agu 2026) |
| Kedalaman Median | 36,2 km |
| Persen Dangkal | 71,3% |
| Gempa Dangkal Besar | 106 |
| Gempa Berflag Tsunami | 17 |

Catatan filter: tahun 2026 hanya berisi data sampai 24 Oktober 2026.
Saat membandingkan antar tahun, beri catatan itu di visual (sudah ada di
layout Halaman 1) agar pembaca tidak salah menyimpulkan 2026 "lebih sepi"
atau "lebih ramai" dari tahun penuh.
