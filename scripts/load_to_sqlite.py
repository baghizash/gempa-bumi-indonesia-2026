#!/usr/bin/env python3
"""Muat katalog gempa ke SQLite dengan star schema sederhana.

Tabel:
  fact_gempa  (1 baris = 1 kejadian; FK: tanggal, wilayah)
  dim_tanggal (tanggal, tahun, bulan, nama_bulan, tahun_bulan)
  dim_wilayah (nama wilayah)
Output: data/gempa_bumi.db (TIDAK ikut di-push ke GitHub).
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "gempa_katalog_2015_2026.csv")

BULAN_ID = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei",
            6: "Juni", 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober",
            11: "November", 12: "Desember"}

dim_t = (
    df[["tanggal"]].drop_duplicates().assign(
        tahun=lambda d: pd.to_datetime(d["tanggal"]).dt.year,
        bulan_nomor=lambda d: pd.to_datetime(d["tanggal"]).dt.month,
    )
)
dim_t["nama_bulan"] = dim_t["bulan_nomor"].map(BULAN_ID)
dim_t["tahun_bulan"] = dim_t["tanggal"].str.slice(0, 7)
dim_t = dim_t.sort_values("tanggal").reset_index(drop=True)

dim_w = pd.DataFrame({"wilayah": sorted(df["wilayah"].unique())})

fact = df.rename(columns={
    "waktu_wib": "waktu_wib", "flag_tsunami_usgs": "flag_tsunami",
    "dirasakan_mmi_maks": "mmi_maks",
})[["waktu_wib", "tanggal", "wilayah", "magnitudo", "tipe_magnitudo",
    "kedalaman_km", "kelas_kedalaman", "lintang", "bujur", "lokasi_usgs",
    "flag_tsunami", "mmi_maks", "id_usgs"]]

db = ROOT / "data" / "gempa_bumi.db"
if db.exists():
    db.unlink()
con = sqlite3.connect(db)
fact.to_sql("fact_gempa", con, index=False)
dim_t.to_sql("dim_tanggal", con, index=False)
dim_w.to_sql("dim_wilayah", con, index=False)
con.execute("CREATE INDEX idx_fact_tanggal ON fact_gempa(tanggal)")
con.execute("CREATE INDEX idx_fact_wilayah ON fact_gempa(wilayah)")
con.commit()
n = con.execute("SELECT COUNT(*) FROM fact_gempa").fetchone()[0]
con.close()
print(f"SQLite: {db} — fact_gempa {n} baris, dim_tanggal {len(dim_t)}, dim_wilayah {len(dim_w)}")
