#!/usr/bin/env python3
"""Analisis katalog gempa + buat findings.json dan 12 chart (charts/*.png).
Semua angka dihitung dari data/gempa_katalog_2015_2026.csv (USGS, sudah
difilter Indonesia) dan snapshot BMKG — tidak ada angka hardcode.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CH = ROOT / "charts"
CH.mkdir(exist_ok=True)

PRIMARY = "#A34A38"
ACCENT = "#DE7A2D"
REDSOFT = "#C97B63"
INK = "#33231C"
GRAY = "#8A7A6C"
GROUND = "#F8F2E5"
GRID = "#D8CCB4"
plt.rcParams.update(
    {
        "font.family": "Noto Sans",
        "axes.unicode_minus": False,
        "font.size": 11,
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.8,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "figure.facecolor": GROUND,
        "axes.facecolor": GROUND,
        "savefig.facecolor": GROUND,
        "figure.dpi": 150,
    }
)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(CH / name, bbox_inches="tight")
    plt.close(fig)
    print("chart:", name)


df = pd.read_csv(ROOT / "data" / "gempa_katalog_2015_2026.csv", parse_dates=["tanggal"])
bmkg = pd.read_csv(ROOT / "data" / "bmkg_terkini.csv")
bmkg_dir = pd.read_csv(ROOT / "data" / "bmkg_dirasakan.csv")
auto = pd.read_csv(ROOT / "data" / "bmkg_autogempa.csv").iloc[0]

F = {"meta": {}, "per_tahun": {}, "magnitudo": {}, "kedalaman": {},
     "wilayah": {}, "tsunami": {}, "bmkg": {}}
_raw_n = len(json.loads((ROOT / "data" / "raw" / "usgs_katalog.geojson").read_text())["features"])
F["meta"] = {
    "total_kejadian": int(len(df)),
    "katalog_mentah_usgs": int(_raw_n),
    "dikeluarkan_label_negara_lain": int(_raw_n - len(df)),
    "berlabel_timor_leste_dipertahankan": int(df["lokasi_usgs"].str.contains("Timor Leste").sum()),
    "periode": "1 Januari 2015 – 20 Oktober 2026",
    "tahun_2026_partial": "2026 hanya sampai 20 Oktober",
    "ambang_magnitudo": 4.5,
    "sumber_katalog": "USGS FDSN Event API (kotak batas Indonesia)",
    "sumber_snapshot": "BMKG TEWS (autogempa, gempaterkini, gempadirasakan), diambil 20 Oktober 2026",
}

# ---------- per tahun & tren ----------
per_tahun = df.groupby("tahun").size()
F["per_tahun"] = {int(k): int(v) for k, v in per_tahun.items()}
F["rata_per_tahun_penuh"] = round(float(per_tahun.loc[2015:2025].mean()), 1)
bulanan = df.set_index("tanggal").resample("ME").size()

fig, ax = plt.subplots(figsize=(8.6, 3.6))
colors = [ACCENT if y == 2026 else PRIMARY for y in per_tahun.index]
ax.bar(per_tahun.index.astype(str), per_tahun.values, color=colors)
for x, v in zip(per_tahun.index.astype(str), per_tahun.values):
    ax.text(x, v + 18, f"{v:,}".replace(",", "."), ha="center", fontsize=9)
ax.set_title("Jumlah Gempa M$\geq$4,5 per Tahun (2026 = s.d. 20 Okt, warna oranye)")
ax.set_ylabel("Jumlah kejadian")
save(fig, "01_per_tahun.png")

fig, ax = plt.subplots(figsize=(8.6, 3.4))
ax.plot(bulanan.index, bulanan.values, color=ACCENT, lw=1.4)
ax.fill_between(bulanan.index, bulanan.values, color=ACCENT, alpha=0.15)
ax.set_title("Tren Bulanan Gempa M$\geq$4,5 di Indonesia, 2015-2026")
ax.set_ylabel("Kejadian per bulan")
save(fig, "02_tren_bulanan.png")

# ---------- magnitudo ----------
F["magnitudo"] = {
    "m5plus": int((df["magnitudo"] >= 5.0).sum()),
    "m6plus": int((df["magnitudo"] >= 6.0).sum()),
    "m7plus": int((df["magnitudo"] >= 7.0).sum()),
    "median": float(df["magnitudo"].median()),
}
top10 = df.nlargest(10, "magnitudo")[
    ["tanggal", "magnitudo", "kedalaman_km", "lokasi_usgs", "wilayah", "flag_tsunami_usgs"]
].copy()
top10["tanggal"] = top10["tanggal"].dt.strftime("%Y-%m-%d")
F["top10_terbesar"] = top10.to_dict("records")
F["magnitudo"]["terbesar"] = top10.iloc[0].to_dict()

fig, ax = plt.subplots(figsize=(8.6, 3.8))
ax.hist(df["magnitudo"], bins=np.arange(4.5, 8.6, 0.25), color=PRIMARY, edgecolor=GROUND, lw=0.4)
ax.axvline(5.0, color=ACCENT, ls="--", lw=1.2)
ax.axvline(6.0, color=INK, ls="--", lw=1.2)
ax.set_title("Distribusi Magnitudo (garis putus-putus: M5 dan M6)")
ax.set_xlabel("Magnitudo")
ax.set_ylabel("Jumlah kejadian")
save(fig, "03_distribusi_magnitudo.png")

bins = pd.cut(df["magnitudo"], [4.5, 5.0, 6.0, 7.0, 10],
              labels=["M4,5-4,9", "M5,0-5,9", "M6,0-6,9", "M$\geq$7,0"], include_lowest=True)
kelas_mag = bins.value_counts().sort_index()
fig, ax = plt.subplots(figsize=(8.6, 3.6))
ax.bar(kelas_mag.index.astype(str), kelas_mag.values, color=[GRAY, REDSOFT, ACCENT, PRIMARY])
for x, v in zip(kelas_mag.index.astype(str), kelas_mag.values):
    ax.text(x, v + 60, f"{v:,}".replace(",", "."), ha="center", fontsize=10)
ax.set_title("Kejadian per Kelas Magnitudo")
ax.set_ylabel("Jumlah kejadian")
save(fig, "04_kelas_magnitudo.png")

# ---------- kedalaman ----------
kd = df["kelas_kedalaman"].value_counts()
order = ["Dangkal (<70 km)", "Menengah (70-300 km)", "Dalam (>300 km)"]
kd = kd.reindex(order)
F["kedalaman"] = {
    k: {"jumlah": int(kd[k]), "persen": round(100 * kd[k] / len(df), 1)} for k in order
}
F["kedalaman"]["median_km"] = float(df["kedalaman_km"].median())
F["kedalaman"]["terdalam_km"] = float(df["kedalaman_km"].max())
dangkal = df[df["kelas_kedalaman"] == "Dangkal (<70 km)"]
F["kedalaman"]["dangkal_m6plus"] = int((dangkal["magnitudo"] >= 6.0).sum())

fig, ax = plt.subplots(figsize=(8.6, 3.6))
ax.barh(order[::-1], kd.values[::-1], color=[REDSOFT, ACCENT, PRIMARY])
for y, v in zip(order[::-1], kd.values[::-1]):
    ax.text(v + 90, y, f"{v:,}".replace(",", ".") + f" ({100*v/len(df):.1f}%)", va="center", fontsize=10)
ax.set_title("Kelas Kedalaman: Mayoritas Gempa Indonesia Itu Dangkal")
ax.set_xlabel("Jumlah kejadian")
ax.set_xlim(0, kd.max() * 1.25)
save(fig, "05_kelas_kedalaman.png")

fig, ax = plt.subplots(figsize=(8.6, 4.0))
sampel = df.sample(min(3000, len(df)), random_state=42)
sc = ax.scatter(sampel["magnitudo"], sampel["kedalaman_km"], s=8, alpha=0.45, c=ACCENT)
ax.invert_yaxis()
ax.axhspan(0, 70, color=PRIMARY, alpha=0.07)
ax.text(8.15, 30, "Zona dangkal\n(<70 km)", color=PRIMARY, fontsize=9, ha="right")
ax.set_title("Magnitudo vs Kedalaman (sampel 3.000 kejadian)")
ax.set_xlabel("Magnitudo")
ax.set_ylabel("Kedalaman (km)")
save(fig, "06_magnitudo_vs_kedalaman.png")

# ---------- wilayah ----------
wil = df.groupby("wilayah").agg(
    jumlah=("magnitudo", "size"), maks=("magnitudo", "max"),
    m6plus=("magnitudo", lambda s: int((s >= 6.0).sum())),
).sort_values("jumlah", ascending=False)
F["wilayah"] = {
    k: {"jumlah": int(r["jumlah"]), "mag_maks": float(r["maks"]), "m6plus": int(r["m6plus"])}
    for k, r in wil.iterrows()
}
F["wilayah_teraktif"] = wil.index[0]

top_wil = wil.head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(8.6, 4.4))
ax.barh(top_wil.index, top_wil["jumlah"], color=PRIMARY)
for y, v in zip(top_wil.index, top_wil["jumlah"]):
    ax.text(v + 30, y, f"{v:,}".replace(",", "."), va="center", fontsize=10)
ax.set_title("10 Wilayah Teraktif (jumlah gempa M$\geq$4,5, 2015-2026)")
ax.set_xlim(0, top_wil["jumlah"].max() * 1.18)
save(fig, "07_wilayah_teraktif.png")

# ---------- peta ----------
fig, ax = plt.subplots(figsize=(9.4, 4.6))
color_map = {"Dangkal (<70 km)": PRIMARY, "Menengah (70-300 km)": ACCENT, "Dalam (>300 km)": REDSOFT}
for kelas, c in color_map.items():
    sub = df[df["kelas_kedalaman"] == kelas]
    ax.scatter(sub["bujur"], sub["lintang"], s=(sub["magnitudo"] - 4.2) ** 2 * 3,
               c=c, alpha=0.45, label=kelas, edgecolors="none")
for nama, lo, la in [("SUMATERA", 100, 1.5), ("KALIMANTAN", 113.5, 1.2), ("JAWA", 108.5, -6.6),
                     ("SULAWESI", 121, -1.8), ("PAPUA", 136.5, -3.2), ("MALUKU", 128.3, -1.2),
                     ("NUSA TENGGARA", 118.5, -9.3)]:
    ax.text(lo, la, nama, fontsize=8, color=GRAY, ha="center", style="italic")
ax.set_xlim(94, 142)
ax.set_ylim(-12, 7)
ax.grid(color=GRID, lw=0.5)
ax.set_title(f"Peta Sebaran {len(df):,} Gempa M$\geq$4,5, 2015-2026 (ukuran = magnitudo, warna = kedalaman)".replace(",", "."))
ax.set_xlabel("Bujur")
ax.set_ylabel("Lintang")
ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
save(fig, "08_peta_sebaran.png")

# ---------- top 10 ----------
t10 = top10.iloc[::-1]
labels = [f"M{m:.1f} - {loc.split(',')[0][:38]}" for m, loc in zip(t10["magnitudo"], t10["lokasi_usgs"])]
fig, ax = plt.subplots(figsize=(8.6, 4.4))
ax.barh(labels, t10["magnitudo"], color=PRIMARY)
for y, v, d in zip(labels, t10["magnitudo"], t10["tanggal"]):
    ax.text(v + 0.06, y, f"{d}", va="center", fontsize=9)
ax.set_xlim(6.4, 8.6)
ax.set_title("10 Gempa Terbesar 2015-2026 (label kanan = tanggal)")
ax.set_xlabel("Magnitudo")
save(fig, "09_top10_terbesar.png")

# ---------- tsunami ----------
tsu = df[df["flag_tsunami_usgs"] == 1]
F["tsunami"] = {
    "total_flag_usgs": int(len(tsu)),
    "per_tahun": {int(k): int(v) for k, v in tsu.groupby("tahun").size().items()},
    "contoh_terbesar": tsu.nlargest(5, "magnitudo")[
        ["tanggal", "magnitudo", "kedalaman_km", "lokasi_usgs", "wilayah"]
    ].assign(tanggal=lambda x: x["tanggal"].dt.strftime("%Y-%m-%d")).to_dict("records"),
    "catatan": "Flag USGS menandai gempa yang berpotensi/dinilai tsunami oleh "
               "sistem peringatan; bukan berarti tsunami merusak selalu terjadi.",
}
tsu_tahun = tsu.groupby("tahun").size().reindex(range(2015, 2027), fill_value=0)
fig, ax = plt.subplots(figsize=(8.6, 3.4))
ax.bar(tsu_tahun.index.astype(str), tsu_tahun.values, color=ACCENT)
ax.set_title("Gempa Berflag Tsunami (USGS) per Tahun")
ax.set_ylabel("Jumlah kejadian")
save(fig, "10_tsunami_per_tahun.png")

# ---------- heatmap tahun x bulan ----------
pivot = df.pivot_table(index="tahun", columns=df["tanggal"].dt.month, values="magnitudo",
                       aggfunc="count").reindex(index=range(2015, 2027), columns=range(1, 13))
fig, ax = plt.subplots(figsize=(8.6, 4.2))
from matplotlib.colors import LinearSegmentedColormap
_t4map = LinearSegmentedColormap.from_list("t4heat", ["#F8F2E5", "#EFC3A0", "#DE7A2D", "#A34A38"])
im = ax.imshow(pivot.fillna(0), cmap=_t4map, aspect="auto")
ax.set_xticks(range(12), ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"])
ax.set_yticks(range(12), [str(y) for y in range(2015, 2027)])
ax.set_title("Peta Panas: Jumlah Gempa per Bulan (baris 2026 berhenti di Oktober)")
fig.colorbar(im, ax=ax, shrink=0.9, label="Kejadian")
save(fig, "11_heatmap_tahun_bulan.png")

# ---------- snapshot BMKG ----------
F["bmkg"] = {
    "terkini_m5plus": bmkg[["tanggal", "jam", "magnitudo", "kedalaman", "wilayah", "potensi"]].to_dict("records"),
    "dirasakan_terbaru": bmkg_dir[["tanggal", "magnitudo", "wilayah", "dirasakan"]].head(5).to_dict("records"),
    "gempa_terbaru_saat_ambil": {
        "tanggal": auto["Tanggal"], "jam": auto["Jam"], "magnitudo": float(auto["Magnitude"]),
        "wilayah": auto["Wilayah"], "dirasakan": auto["Dirasakan"],
    },
    "okt2026_dari_terkini": bmkg[bmkg["tanggal"].str.contains("Okt 2026")][
        ["tanggal", "magnitudo", "wilayah"]].to_dict("records"),
}
bm = bmkg.iloc[::-1]
fig, ax = plt.subplots(figsize=(8.6, 3.8))
ax.barh([f"{t} - {w.split('|')[0][:34]}" for t, w in zip(bm["tanggal"], bm["wilayah"])],
        bm["magnitudo"], color=ACCENT)
ax.set_xlim(4.6, 6.3)
ax.set_title("Snapshot BMKG: 15 Gempa M5+ Terbaru (diambil 20 Okt 2026)")
ax.set_xlabel("Magnitudo")
save(fig, "12_snapshot_bmkg.png")

(ROOT / "findings.json").write_text(json.dumps(F, indent=2, ensure_ascii=False))
print("\nfindings.json ditulis.")
print(json.dumps({k: F[k] for k in ["magnitudo", "kedalaman", "wilayah_teraktif"]}, indent=1, ensure_ascii=False)[:900])
print("tsunami total:", F["tsunami"]["total_flag_usgs"], "| M5+:", F["magnitudo"]["m5plus"],
      "| M6+:", F["magnitudo"]["m6plus"], "| M7+:", F["magnitudo"]["m7plus"])
print("terbesar:", F["magnitudo"]["terbesar"])
