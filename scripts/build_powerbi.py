#!/usr/bin/env python3
"""Bangun kit Power BI di powerbi/: CSV star schema + pratinjau halaman 1.

fact_gempa : 1 baris = 1 kejadian (grain tunggal, tidak ada baris agregat)
dim_tanggal: tanggal, tahun, bulan_nomor, nama_bulan, tahun_bulan
dim_wilayah: wilayah
File DAX, layout, dan panduan ditulis manual (measures_dax.md,
dashboard_layout.md, build_guide.md) dan membaca angka dari findings.json.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PB = ROOT / "powerbi"
PB.mkdir(exist_ok=True)
F = json.loads((ROOT / "findings.json").read_text())
df = pd.read_csv(ROOT / "data" / "gempa_katalog_2015_2026.csv")

BULAN_ID = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei",
            6: "Juni", 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober",
            11: "November", 12: "Desember"}

fact = df[["tanggal", "waktu_wib", "wilayah", "magnitudo", "kedalaman_km",
           "kelas_kedalaman", "lintang", "bujur", "lokasi_usgs",
           "flag_tsunami_usgs"]].rename(columns={"flag_tsunami_usgs": "flag_tsunami"})
fact.to_csv(PB / "fact_gempa.csv", index=False)

dim_t = df[["tanggal"]].drop_duplicates().copy()
dt = pd.to_datetime(dim_t["tanggal"])
dim_t["tahun"] = dt.dt.year
dim_t["bulan_nomor"] = dt.dt.month
dim_t["nama_bulan"] = dim_t["bulan_nomor"].map(BULAN_ID)
dim_t["tahun_bulan"] = dim_t["tanggal"].str.slice(0, 7)
dim_t = dim_t.sort_values("tanggal")
dim_t.to_csv(PB / "dim_tanggal.csv", index=False)

dim_w = pd.DataFrame({"wilayah": sorted(df["wilayah"].unique())})
dim_w.to_csv(PB / "dim_wilayah.csv", index=False)
print(f"fact_gempa {len(fact)} baris | dim_tanggal {len(dim_t)} | dim_wilayah {len(dim_w)}")

# ---- Pratinjau halaman 1 (mock dari data asli) ----
NAVY, TEAL, RED = "#1E3A8A", "#0E7C7B", "#C0392B"
m = F["magnitudo"]
fig = plt.figure(figsize=(12.8, 7.2))
fig.patch.set_facecolor("white")
ax_t = fig.add_axes([0.03, 0.90, 0.94, 0.08]); ax_t.axis("off")
ax_t.text(0, 0.55, "GEMPA BUMI INDONESIA 2015–2026 — Ringkasan", fontsize=17,
          fontweight="bold", color=NAVY)
kpi = fig.add_axes([0.03, 0.78, 0.94, 0.11]); kpi.axis("off")
cards = [
    (f"{F['meta']['total_kejadian']:,}".replace(",", "."), "Total gempa M≥4,5"),
    (f"{m['m5plus']:,}".replace(",", "."), "Gempa M≥5,0"),
    (f"{m['m6plus']}", "Gempa M≥6,0"),
    (f"M{m['terbesar']['magnitudo']}", "Terbesar: Ende, 15 Agu 2026"),
    (f"{F['kedalaman']['Dangkal (<70 km)']['persen']}%", "Berada di zona dangkal"),
]
for i, (v, lab) in enumerate(cards):
    x = i * 0.2
    kpi.add_patch(plt.Rectangle((x + 0.005, 0.08), 0.185, 0.84, facecolor="#EFF6FF",
                                edgecolor=NAVY, lw=0.8, transform=kpi.transAxes))
    kpi.text(x + 0.1, 0.62, v, ha="center", fontsize=15, fontweight="bold", color=NAVY)
    kpi.text(x + 0.1, 0.28, lab, ha="center", fontsize=8.5, color="#374151")
axm = fig.add_axes([0.03, 0.06, 0.60, 0.68])
cmap = {"Dangkal (<70 km)": RED, "Menengah (70-300 km)": "#D9A441", "Dalam (>300 km)": TEAL}
for kls, c in cmap.items():
    sub = df[df["kelas_kedalaman"] == kls]
    axm.scatter(sub["bujur"], sub["lintang"], s=(sub["magnitudo"] - 4.2) ** 2 * 3,
                c=c, alpha=0.45, label=kls, edgecolors="none")
axm.set_xlim(94, 142); axm.set_ylim(-12, 7); axm.grid(color="#E5E7EB", lw=0.5)
axm.set_title("Peta sebaran (ukuran = magnitudo)", fontsize=11, color=NAVY, fontweight="bold")
axm.legend(fontsize=7.5, loc="lower left")
axb = fig.add_axes([0.67, 0.06, 0.30, 0.68])
pt = pd.Series(F["per_tahun"])
axb.barh([str(y) for y in pt.index][::-1], pt.values[::-1], color=NAVY)
axb.set_title("Gempa per tahun", fontsize=11, color=NAVY, fontweight="bold")
fig.savefig(PB / "dashboard_preview_halaman1.png", dpi=130, bbox_inches="tight")
print("preview saved")
