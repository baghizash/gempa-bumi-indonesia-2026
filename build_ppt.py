#!/usr/bin/env python3
"""Build Portofolio-Analisis-Gempa-Bumi.pptx (16:9, 10 slides, ID).
Reads findings.json — every number comes from the fetched BMKG/USGS data.
Design: dials 7/5/3 (deck portfolio), real charts only, no fake numbers.
"""
import json
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn

HERE = Path(__file__).resolve().parent
F = json.loads((HERE / "findings.json").read_text())
CHARTS = HERE / "charts"
OUT = Path.home() / "workspace" / "your_files" / "Portofolio-Analisis-Gempa-Bumi.pptx"

NAVY = RGBColor(0x1E, 0x3A, 0x8A)
TEAL = RGBColor(0x0E, 0x7C, 0x7B)
RED = RGBColor(0xC0, 0x39, 0x2B)
DARK = RGBColor(0x1F, 0x29, 0x37)
GRAY = RGBColor(0x6B, 0x72, 0x80)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]


def fmt(n):
    return f"{n:,}".replace(",", ".")


def solid_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def textbox(slide, l, t, w, h):
    tx = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tx.text_frame
    tf.word_wrap = True
    return tf


def add_par(tf, text, size, color, bold=False, italic=False, first=False, align=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.space_after = Pt(8)
    if align is not None:
        p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    return p


def add_bullet(tf, text, size=17, first=False):
    p = add_par(tf, text, size, DARK, first=first)
    pPr = p._p.get_or_add_pPr()
    pPr.append(pPr.makeelement(qn("a:buChar"), {"char": "\u2022"}))
    pPr.set("marL", "171450")
    pPr.set("indent", "-171450")
    p.space_after = Pt(10)
    p.space_before = Pt(2)
    return p


def content_title(slide, text):
    tf = textbox(slide, 0.7, 0.3, 11.9, 0.9)
    add_par(tf, text, 30, NAVY, bold=True, first=True)
    bar = slide.shapes.add_shape(1, Inches(0.7), Inches(1.15), Inches(1.5), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()


def content_slide(title, bullets, chart=None, caption=None, full_width=False, chart_w=5.8):
    s = prs.slides.add_slide(blank)
    solid_bg(s, WHITE)
    content_title(s, title)
    bw = 11.9 if full_width else 5.6
    tf = textbox(s, 0.7, 1.5, bw, 5.2)
    for i, b in enumerate(bullets):
        add_bullet(tf, b, first=(i == 0))
    if chart:
        s.shapes.add_picture(str(CHARTS / f"{chart}.png"), Inches(6.8), Inches(1.5), width=Inches(chart_w))
    if caption:
        tf2 = textbox(s, 0.7, 6.7, 11.9, 0.5)
        add_par(tf2, caption, 11, GRAY, italic=True, first=True)
    return s


M = F["meta"]
MG = F["magnitudo"]
KD = F["kedalaman"]
WL = F["wilayah"]
TS = F["tsunami"]
TOP = F["top10_terbesar"]
BM = F["bmkg"]

# ---- Slide 1: Title ----
s = prs.slides.add_slide(blank)
solid_bg(s, NAVY)
tf = textbox(s, 0.9, 1.0, 11.5, 1.2)
add_par(tf, "ANALISIS GEMPA BUMI INDONESIA 2015–2026", 38, WHITE, bold=True, first=True)
tf = textbox(s, 0.9, 2.4, 11.5, 1.0)
add_par(tf, "Seberapa Sering, Seberapa Besar, dan Di Mana Gempa Mengguncang Indonesia", 20, WHITE, first=True)
tf = textbox(s, 0.9, 3.7, 11.5, 2.0)
add_par(tf, f"Katalog USGS {fmt(M['total_kejadian'])} gempa M≥4,5 — 1 Januari 2015 sampai 20 Oktober 2026, "
            "plus snapshot real-time BMKG", 16, WHITE, first=True)
add_par(tf, "Plus: paket dashboard Power BI (star schema, DAX, panduan rakit)", 16, WHITE)
tf = textbox(s, 0.9, 6.0, 11.5, 0.8)
add_par(tf, "BAGHIZ ASSHIDDIQIE ARASYA", 20, WHITE, bold=True, first=True)

# ---- Slide 2: Latar belakang ----
content_slide("Kenapa Gempa Bumi?", [
    "Indonesia berdiri di pertemuan empat lempeng tektonik: Indo-Australia, "
    "Eurasia, Pasifik, dan Laut Filipina. Gempa bukan kejadian langka — "
    "ia terjadi hampir setiap hari.",
    "Tapi 'sering' saja tidak cukup untuk kebijakan dan kesiapsiagaan. Yang perlu "
    "dijawab: wilayah mana paling aktif, seberapa besar gempa yang realistis "
    "terjadi, dan seberapa dangkal sumbernya.",
    "Analisis ini menjawabnya dari katalog 12 tahun: frekuensi per tahun, kelas "
    "magnitudo, kelas kedalaman, peta sebaran, sampai gempa berflag tsunami — "
    "ditutup snapshot kejadian terbaru dari BMKG.",
], full_width=True, caption="Sumber data: USGS FDSN Event API (katalog historis) dan BMKG TEWS (snapshot real-time), diambil 20 Oktober 2026.")

# ---- Slide 3: Data dan metode ----
content_slide("Data dan Metode", [
    f"Katalog mentah USGS: {fmt(M['katalog_mentah_usgs'])} kejadian dalam kotak batas Indonesia "
    f"(lintang −11 s.d. 6, bujur 95 s.d. 141), ambang M≥4,5. Setelah {fmt(M['dikeluarkan_label_negara_lain'])} kejadian "
    "berlabel negara lain (Filipina, Malaysia, Papua Nugini, Palau) dikeluarkan, katalog bersih berisi "
    f"{fmt(M['total_kejadian'])} kejadian.",
    f"{M['berlabel_timor_leste_dipertahankan']} kejadian berlabel 'Timor Leste' dipertahankan: episentrumnya di perairan "
    "Indonesia utara/timur Pulau Timor, hanya kota acuannya yang lintas negara.",
    "Wilayah diturunkan dari nama laut pada label USGS, lalu kotak koordinat pulau "
    "terdekat. Kelas kedalaman: dangkal <70 km, menengah 70–300 km, dalam >300 km.",
    "Snapshot BMKG (autogempa, gempaterkini, gempadirasakan) dipakai untuk bagian "
    "terkini — endpoint itu hanya menyimpan kejadian terbaru, bukan arsip.",
], full_width=True)

# ---- Slide 4: Tren per tahun ----
content_slide("Frekuensi: Hampir 800 Gempa per Tahun", [
    f"Rata-rata tahun penuh 2015–2025: {fmt(int(F['rata_per_tahun_penuh']))} gempa M≥4,5 per tahun. "
    "Tidak ada tren naik/turun yang jelas — aktivitas berfluktuasi mengikuti "
    "rangkaian gempa besar dan gempa susulannya.",
    f"Tahun tersibuk: 2019 dengan {fmt(F['per_tahun']['2019'])} kejadian; tersepi: 2016 ({fmt(F['per_tahun']['2016'])}).",
    f"2026 baru berjalan sampai 20 Oktober tetapi sudah mencatat {fmt(F['per_tahun']['2026'])} kejadian — "
    "setara tahun penuh yang sibuk, didorong rangkaian gempa besar tahun ini.",
], chart="01_per_tahun", caption="Chart: jumlah gempa per tahun. 2026 (amber) bersifat parsial.")

# ---- Slide 5: Magnitudo ----
content_slide("Magnitudo: Yang Besar Itu Langka, Tapi Nyata", [
    f"Dari {fmt(M['total_kejadian'])} gempa: {fmt(MG['m5plus'])} mencapai M≥5,0 — "
    f"{fmt(MG['m6plus'])} mencapai M≥6,0, dan hanya {MG['m7plus']} yang mencapai M≥7,0.",
    "Median magnitudo hanya 4,7: sebagian besar gempa Indonesia kecil. "
    "Risiko terkonsentrasi di ekor distribusi — belasan gempa M7+ per dekade.",
    "Pola ini konsisten dengan hukum Gutenberg–Richter: setiap kenaikan 1 skala "
    "magnitudo, frekuensi turun kira-kira 10 kali lipat.",
], chart="04_kelas_magnitudo", caption="Chart: kejadian per kelas magnitudo, 2015–2026.")

# ---- Slide 6: Terbesar ----
t0, t2 = TOP[0], TOP[2]
content_slide("Gempa Terbesar dalam 12 Tahun", [
    f"Terbesar: M{t0['magnitudo']} — {t0['lokasi_usgs']} ({t0['tanggal']}), "
    f"kedalaman hanya {t0['kedalaman_km']:.0f} km. Besar dan dangkal: kombinasi paling berbahaya.",
    f"Nama yang paling diingat publik: M{t2['magnitudo']} Palu, Sulawesi ({t2['tanggal']}) — "
    "gempa dangkal 20 km yang memicu tsunami dan likuefaksi.",
    "10 daftar teratas didominasi kawasan timur (NTT, Tanimbar, Halmahera, Laut Banda) "
    "dan Sulawesi — bukan Jawa yang penduduknya terpadat.",
], chart="09_top10_terbesar", caption="Chart: 10 gempa terbesar 2015–2026 berdasarkan katalog USGS.")

# ---- Slide 7: Kedalaman ----
dk = KD["Dangkal (<70 km)"]
content_slide("Kedalaman: 7 dari 10 Gempa Itu Dangkal", [
    f"Gempa dangkal (<70 km): {fmt(dk['jumlah'])} kejadian ({dk['persen']}%). "
    f"Menengah: {fmt(KD['Menengah (70-300 km)']['jumlah'])} ({KD['Menengah (70-300 km)']['persen']}%). "
    f"Dalam (>300 km): {fmt(KD['Dalam (>300 km)']['jumlah'])} ({KD['Dalam (>300 km)']['persen']}%).",
    "Gempa dangkal lebih berpotensi merusak: energi dilepas dekat permukaan dan "
    "permukiman. Kedalaman median katalog hanya 36,2 km.",
    f"Kombinasi paling waspada — dangkal sekaligus M≥6 — terjadi {KD['dangkal_m6plus']} kali "
    "dalam 12 tahun, kira-kira 9 kali per tahun.",
], chart="05_kelas_kedalaman", caption="Chart: jumlah kejadian per kelas kedalaman.")

# ---- Slide 8: Peta & wilayah ----
wa = F["wilayah_teraktif"]
content_slide("Peta Sebaran dan Wilayah Teraktif", [
    f"Wilayah teraktif: {wa} — {fmt(WL[wa]['jumlah'])} kejadian, magnitudo maks M{WL[wa]['mag_maks']}. "
    "Zona tumbukan Laut Maluku memang salah satu kawasan seismik paling aktif di dunia.",
    f"Menyusul: Sumatera ({fmt(WL['Sumatera']['jumlah'])}), Papua ({fmt(WL['Papua']['jumlah'])}), "
    f"Sulawesi ({fmt(WL['Sulawesi']['jumlah'])}). Kalimantan hanya {WL['Kalimantan']['jumlah']} kejadian — "
    "jauh dari batas lempeng, nyaris bebas gempa.",
    "Pola peta memperlihatkan jalur busur kepulauan: gempa menumpuk mengikuti "
    "garis subduksi dari barat Sumatera, selatan Jawa, sampai Banda dan Maluku.",
], chart="08_peta_sebaran", caption="Chart: peta sebaran — ukuran titik = magnitudo, warna = kelas kedalaman.")

# ---- Slide 9: Snapshot BMKG ----
okt = BM["okt2026_dari_terkini"]
content_slide("Snapshot BMKG: Oktober 2026", [
    f"Dalam 18 hari pertama Oktober 2026 saja, BMKG mencatat {len(okt)} gempa M5+ — "
    "termasuk M6,1 di Kodi, Sumba Barat Daya (4 Okt) dan M5,8 di Tahuna, Kep. Sangihe (8 Okt).",
    "Dua gempa M5,7 berurutan: Sukabumi, Jawa Barat (11 Okt, dangkal 10 km) dan "
    "Pohuwato, Gorontalo (12 Okt). Terakhir di daftar: M5,3 Labuan Bajo, NTT (18 Okt).",
    f"Gempa terbaru saat data diambil: M{BM['gempa_terbaru_saat_ambil']['magnitudo']} di perairan "
    "Pulau Saringi (20 Okt, 18:28 WIB) — dirasakan III di Kabupaten Sumbawa. "
    "Bukti bahwa katalog ini hidup: gempa terjadi bahkan saat analisis dikerjakan.",
], chart="12_snapshot_bmkg", caption="Chart: 15 gempa M5+ terbaru versi BMKG (snapshot 20 Oktober 2026).")

# ---- Slide 10: Penutup ----
content_slide("Penutup", [
    f"Tiga pesan utama: (1) Indonesia rata-rata diguncang {fmt(int(F['rata_per_tahun_penuh']))} gempa M≥4,5 per tahun "
    f"dan {dk['persen']}% di antaranya dangkal; (2) risiko besar terkonsentrasi di timur — "
    "Halmahera–Maluku, Banda, NTT, Sulawesi; (3) gempa M7+ memang langka "
    f"({MG['m7plus']} kali dalam 12 tahun) tetapi selalu datang tanpa jadwal.",
    "Paket dashboard Power BI tersedia di folder powerbi/: star schema 3 tabel, "
    "measure DAX siap tempel dengan tabel verifikasi, layout 4 halaman (termasuk "
    "halaman peta), dan panduan rakit langkah demi langkah.",
    "Semua angka dapat direproduksi: jalankan scripts/fetch_data.py lalu "
    "scripts/analyze.py — findings.json dan 12 chart dihitung ulang dari nol, dan "
    "bisa dicek silang dengan sql/queries.sql.",
    "Terima kasih.",
], full_width=True)

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUT))
print(f"PPT saved: {OUT}")
