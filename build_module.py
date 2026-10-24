#!/usr/bin/env python3
"""Build Modul-Analisis-Gempa-Bumi.pdf (A4 landscape, beginner-friendly ID).

Reads findings.json — every number comes from the BMKG/USGS data.
Design dials 6/3/3 (module): clean, generous whitespace, real charts.
"""
import json
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak,
)

HERE = Path(__file__).resolve().parent
F = json.loads((HERE / "findings.json").read_text())
OUT = str(Path.home() / "workspace" / "coursera-modules" / "Modul-Analisis-Gempa-Bumi.pdf")
CHARTS = HERE / "charts"
W, H = landscape(A4)
NAVY = HexColor("#1E3A8A")
TEAL = HexColor("#0D9488")
DARK = HexColor("#1F2937")
GRAY = HexColor("#6B7280")
LIGHT = HexColor("#EFF6FF")

styles = {
    "cover": ParagraphStyle("cover", fontName="Helvetica-Bold", fontSize=30, leading=36,
                            textColor=NAVY, alignment=TA_LEFT),
    "coversub": ParagraphStyle("coversub", fontName="Helvetica", fontSize=15, leading=21,
                               textColor=DARK, alignment=TA_LEFT),
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=27,
                         textColor=NAVY, spaceBefore=6, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=16, leading=20,
                         textColor=TEAL, spaceBefore=8, spaceAfter=6),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=12.5, leading=18,
                           textColor=DARK, spaceAfter=7),
    "bullet": ParagraphStyle("bullet", parent=ParagraphStyle("b", fontName="Helvetica",
                             fontSize=12.5, leading=18, textColor=DARK, spaceAfter=5,
                             leftIndent=16, bulletIndent=6)),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=10.5, leading=15,
                           textColor=DARK, backColor=LIGHT, spaceAfter=8,
                           leftIndent=8, borderPadding=(6, 6, 6)),
    "caption": ParagraphStyle("caption", fontName="Helvetica-Oblique", fontSize=10.5,
                              leading=14, textColor=GRAY, alignment=TA_CENTER,
                              spaceBefore=4, spaceAfter=10),
    "warn": ParagraphStyle("warn", fontName="Helvetica", fontSize=12.5, leading=18,
                           textColor=HexColor("#92400E"), backColor=HexColor("#FEF3C7"),
                           borderPadding=(8, 8, 8), spaceAfter=8),
}
story = []


def P(text, style="body"):
    story.append(Paragraph(text, styles[style]))


def B(text):
    story.append(Paragraph(text, styles["bullet"], bulletText="•"))


def CODE(text):
    story.append(Paragraph(text.replace(" ", "&nbsp;").replace("\n", "<br/>"), styles["code"]))


def CHART(fname, caption, width=20 * cm, ratio=0.45):
    story.append(Image(str(CHARTS / fname), width=width, height=width * ratio))
    P(caption, "caption")


def TABLE(data, widths=None):
    t = Table([[Paragraph(str(c), styles["body"]) for c in row] for row in data],
              colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), LIGHT]),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))


def fmt(n):
    return f"{int(n):,}".replace(",", ".")


M = F["meta"]
MG = F["magnitudo"]
KD = F["kedalaman"]
WL = F["wilayah"]
TS = F["tsunami"]
TOP = F["top10_terbesar"]
BM = F["bmkg"]

# ---------- COVER ----------
story.append(Spacer(1, 3 * cm))
P("MODUL BELAJAR", "cover")
P("Modul Analisis Gempa Bumi Indonesia 2015–2026", "cover")
P("Dari Katalog USGS dan API BMKG sampai Dashboard Power BI: Studi Kasus Nyata untuk Pemula", "coversub")
story.append(Spacer(1, 0.6 * cm))
P(f"Modul ini mengajak kamu membangun satu project analisis data nyata dari nol: "
  f"katalog {fmt(M['total_kejadian'])} gempa bumi bermagnitudo 4,5 ke atas di Indonesia "
  f"selama 2015–2026. Kamu akan belajar mengambil data dari dua API publik (USGS dan "
  f"BMKG), membersihkan label yang tidak relevan, menurunkan wilayah dan kelas "
  f"kedalaman, menjawab pertanyaan dengan SQL, memvisualisasikan dengan Python "
  f"(termasuk membuat peta sebaran), lalu menyusun dashboard Power BI. Semua angka "
  f"di modul ini dihitung dari data — tidak ada yang dikarang.", "coversub")
story.append(Spacer(1, 0.5 * cm))
P("Sumber data: USGS FDSN Event API (katalog historis) dan BMKG TEWS (snapshot real-time). "
  "Diambil 24 Oktober 2026. Tahun 2026 bersifat parsial (sampai 24 Oktober).", "warn")
story.append(PageBreak())

# ---------- BAB 1 ----------
P("Bab 1 — Kenalan dengan Project Ini", "h1")
P("Indonesia berdiri di pertemuan empat lempeng tektonik besar: Indo-Australia, "
  "Eurasia, Pasifik, dan Laut Filipina. Lempeng-lempeng itu terus bergerak beberapa "
  "sentimeter per tahun; energi yang menumpuk dilepas sebagai gempa. Karena itu "
  "gempa di Indonesia bukan peristiwa langka, melainkan latar kehidupan sehari-hari.", "body")
P("Pertanyaan yang akan dijawab", "h2")
B("Seberapa sering gempa M≥4,5 terjadi — per tahun, per bulan?")
B("Seberapa besar gempa yang realistis? Berapa kali M≥6 dan M≥7 terjadi?")
B("Seberapa dangkal sumber gempanya, dan kenapa itu penting?")
B("Wilayah mana yang paling aktif — dan mana yang nyaris bebas gempa?")
B("Berapa gempa yang berpotensi tsunami, dan apa yang terjadi bulan ini?")
P("Alur kerja project ini", "h2")
B("1. Ambil data: scripts/fetch_data.py (BMKG + USGS).")
B("2. Rapikan: scripts/assemble.py → katalog CSV bersih + aturan wilayah/kedalaman.")
B("3. Jawab pertanyaan dengan SQL (sql/queries.sql) dan hitung temuan (scripts/analyze.py → findings.json).")
B("4. Visualisasikan: 12 chart Python/matplotlib, termasuk peta sebaran.")
B("5. Susun paket dashboard Power BI (folder powerbi/).")
story.append(PageBreak())

# ---------- BAB 2 ----------
P("Bab 2 — Dua Sumber Data, Dua Peran", "h1")
P("Project ini memakai dua sumber resmi yang saling melengkapi. Memahami peran "
  "masing-masing adalah pelajaran pertama analisis data dunia nyata: tidak ada "
  "satu sumber yang sempurna untuk semua pertanyaan.", "body")
TABLE([
    ["Sumber", "Isi", "Dipakai untuk"],
    ["USGS FDSN Event API", f"Katalog gempa global; kita ambil kotak batas Indonesia, 2015–2026, M≥4,5 ({fmt(M['katalog_mentah_usgs'])} kejadian mentah)", "Statistik historis: tren, magnitudo, kedalaman, wilayah"],
    ["BMKG TEWS API", "Gempa terbaru, 15 gempa M5+ terakhir, 15 gempa dirasakan terakhir (jendela bergeser)", "Snapshot terkini: apa yang terjadi Oktober 2026"],
], widths=[4.5 * cm, 9.5 * cm, 8.2 * cm])
P("Endpoint BMKG (tanpa login, format JSON):", "h2")
CODE("https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json\n"
     "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json\n"
     "https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.json")
P("Endpoint USGS (tanpa API key, format GeoJSON):", "h2")
CODE("https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson\n"
     "&starttime=2015-01-01&endtime=2026-10-24\n"
     "&minlatitude=-11&maxlatitude=6&minlongitude=95&maxlongitude=141\n"
     "&minmagnitude=4.5&orderby=time&limit=20000")
P(f"Contoh isi snapshot BMKG saat pengambilan: gempa terbaru adalah "
  f"M{BM['gempa_terbaru_saat_ambil']['magnitudo']} di darat 6 km Barat Laut Lebong, "
  f"Bengkulu (22 Okt 2026, 17:57 WIB), dirasakan skala III di Kota Bengkulu dan "
  f"Arga Makmur serta II–III di Curup.", "body")
story.append(PageBreak())

# ---------- BAB 3 ----------
P("Bab 3 — Membersihkan dan Merakit Katalog", "h1")
P("Data mentah tidak pernah langsung bersih. Katalog USGS diambil dengan kotak "
  "batas persegi, jadi pinggiran negara tetangga ikut tertangkap. Tiga keputusan "
  "pembersihan diambil — dan semuanya didokumentasikan di data/SOURCES.md:", "body")
B(f"Kejadian berlabel negara lain pada kolom place (Philippines, Malaysia, "
  f"Papua New Guinea, Palau) dikeluarkan: {fmt(M['dikeluarkan_label_negara_lain'])} kejadian.")
B(f"Kejadian berlabel 'Timor Leste' DIPERTAHANKAN ({fmt(M['berlabel_timor_leste_dipertahankan'])} kejadian): "
  "USGS melabeli gempa dengan kota terdekat, dan episentrum kejadian ini berada di "
  "perairan Indonesia utara/timur Pulau Timor (sekitar P. Kisar, Wetar, Romang di NTT).")
B(f"Hasil akhir: katalog bersih {fmt(M['total_kejadian'])} kejadian di data/gempa_katalog_2015_2026.csv.")
P("Menurunkan dua kolom baru", "h2")
B("Wilayah: dari nama laut pada label USGS (Laut Banda, Laut Maluku, dst.), "
  "kalau tidak ada, dari kotak koordinat pulau terdekat (Sumatera, Jawa, Sulawesi, ...).")
B("Kelas kedalaman: Dangkal <70 km · Menengah 70–300 km · Dalam >300 km — "
  "konvensi umum seismologi.")
P("Pelajaran untuk pemula: keputusan pembersihan seperti ini wajar dalam analisis "
  "nyata. Yang tidak wajar adalah menyembunyikannya. Tulis selalu di SOURCES.md.", "warn")
story.append(PageBreak())

# ---------- BAB 4 ----------
P("Bab 4 — Menjawab Pertanyaan dengan SQL", "h1")
P("Katalog dimuat ke SQLite (scripts/load_to_sqlite.py) dengan tiga tabel: "
  "fact_gempa, dim_tanggal, dim_wilayah. Delapan query verifikasi ada di "
  "sql/queries.sql. Contoh pola yang paling sering dipakai:", "body")
P("Jumlah gempa per tahun", "h2")
CODE("SELECT t.tahun, COUNT(*) AS jumlah\n"
     "FROM fact_gempa f\n"
     "JOIN dim_tanggal t ON t.tanggal = f.tanggal\n"
     "GROUP BY t.tahun ORDER BY t.tahun;")
P("Kelas magnitudo dengan agregasi kondisional", "h2")
CODE("SELECT SUM(CASE WHEN magnitudo >= 5.0 THEN 1 ELSE 0 END) AS m5plus,\n"
     "       SUM(CASE WHEN magnitudo >= 6.0 THEN 1 ELSE 0 END) AS m6plus,\n"
     "       SUM(CASE WHEN magnitudo >= 7.0 THEN 1 ELSE 0 END) AS m7plus\n"
     "FROM fact_gempa;")
P(f"Hasilnya: M≥5 ada {fmt(MG['m5plus'])} kejadian, M≥6 ada {fmt(MG['m6plus'])}, "
  f"M≥7 ada {MG['m7plus']}. Semua angka headline di modul ini dicek dua kali: "
  "sekali dari pandas (analyze.py), sekali dari SQL — dan harus sama.", "body")
story.append(PageBreak())

# ---------- BAB 5 ----------
P("Bab 5 — Temuan 1: Frekuensi dan Magnitudo", "h1")
P(f"Indonesia diguncang rata-rata {fmt(int(F['rata_per_tahun_penuh']))} gempa M≥4,5 per tahun penuh. "
  f"Tahun tersibuk adalah 2019 ({fmt(F['per_tahun']['2019'])} kejadian), tersepi 2016 "
  f"({fmt(F['per_tahun']['2016'])}). Tahun 2026 baru berjalan sampai 24 Oktober, tetapi sudah "
  f"mencatat {fmt(F['per_tahun']['2026'])} kejadian.", "body")
CHART("01_per_tahun.png", "Jumlah gempa per tahun. 2026 (amber) bersifat parsial.", ratio=0.42)
P(f"Sebagian besar gempa itu kecil: median magnitudo hanya 4,7. Yang mencapai M≥6 "
  f"hanya {fmt(MG['m6plus'])} kali dalam 12 tahun, dan M≥7 hanya {MG['m7plus']} kali. Inilah pola hukum "
  "Gutenberg–Richter: naik 1 skala, frekuensi turun sekitar 10 kali lipat.", "body")
CHART("03_distribusi_magnitudo.png", "Distribusi magnitudo: menumpuk di 4,5–5,0, menipis ke kanan.", ratio=0.44)
story.append(PageBreak())

# ---------- BAB 6 ----------
P("Bab 6 — Temuan 2: Kedalaman Menentukan Bahaya", "h1")
P("Dua gempa dengan magnitudo sama bisa berdampak sangat berbeda. Bedanya sering "
  "terletak pada kedalaman: gempa dangkal melepas energi dekat permukaan dan "
  "permukiman, gempa dalam energinya menyebar jauh sebelum sampai ke atas.", "body")
TABLE([
    ["Kelas kedalaman", "Jumlah", "Persen"],
    ["Dangkal (<70 km)", fmt(KD["Dangkal (<70 km)"]["jumlah"]), f"{KD['Dangkal (<70 km)']['persen']}%"],
    ["Menengah (70–300 km)", fmt(KD["Menengah (70-300 km)"]["jumlah"]), f"{KD['Menengah (70-300 km)']['persen']}%"],
    ["Dalam (>300 km)", fmt(KD["Dalam (>300 km)"]["jumlah"]), f"{KD['Dalam (>300 km)']['persen']}%"],
], widths=[7 * cm, 5 * cm, 5 * cm])
P(f"Kombinasi paling waspada — dangkal sekaligus M≥6 — terjadi {KD['dangkal_m6plus']} kali "
  f"dalam 12 tahun. Contoh paling diingat: gempa Palu 28 Sep 2018 (M{TOP[2]['magnitudo']}, "
  f"kedalaman {TOP[2]['kedalaman_km']:.0f} km). Kedalaman median seluruh katalog hanya "
  f"{KD['median_km']} km; yang terdalam mencapai {KD['terdalam_km']} km di bawah Laut Banda.", "body")
CHART("05_kelas_kedalaman.png", "Mayoritas gempa Indonesia berada di zona dangkal.", ratio=0.42)
story.append(PageBreak())

# ---------- BAB 7 ----------
P("Bab 7 — Temuan 3: Peta Sebaran dan Wilayah Teraktif", "h1")
P("Peta adalah visual terpenting project ini. Setiap titik adalah satu gempa: "
  "posisinya dari bujur/lintang USGS, ukurannya magnitudo, warnanya kelas kedalaman. "
  "Tidak perlu peta dasar rumit — cukup scatter di atas grid koordinat.", "body")
CHART("08_peta_sebaran.png", "Gempa menumpuk mengikuti jalur subduksi: barat Sumatera, selatan Jawa, Banda, Maluku.", width=22 * cm, ratio=0.49)
top_rows = [["Wilayah", "Jumlah", "Mag. maks", "M≥6"]]
for name, v in list(WL.items())[:6]:
    top_rows.append([name, fmt(v["jumlah"]), f"M{v['mag_maks']}", fmt(v["m6plus"])])
TABLE(top_rows, widths=[7 * cm, 4 * cm, 4 * cm, 3 * cm])
P(f"Wilayah teraktif adalah {F['wilayah_teraktif']} ({fmt(WL[F['wilayah_teraktif']]['jumlah'])} kejadian) — "
  "zona Laut Maluku adalah salah satu kawasan seismik paling aktif di dunia. "
  f"Sebaliknya Kalimantan hanya mencatat {WL['Kalimantan']['jumlah']} kejadian dalam 12 tahun karena jauh "
  "dari batas lempeng.", "body")
story.append(PageBreak())

# ---------- BAB 8 ----------
P("Bab 8 — Tsunami dan Snapshot Terkini", "h1")
P(f"USGS memberi flag tsunami pada {TS['total_flag_usgs']} kejadian di katalog ini — artinya gempa "
  "tersebut dinilai berpotensi tsunami oleh sistem peringatan. Flag bukan bukti "
  "tsunami merusak benar-benar terjadi; untuk status resmi selalu ikuti BMKG.", "body")
B("Contoh terbesar: M7,3 Laut Banda (24 Jun 2019) dan M7,3 Laut Flores (14 Des 2021) — keduanya berflag.")
CHART("10_tsunami_per_tahun.png", "Gempa berflag tsunami per tahun (USGS).", ratio=0.40)
P("Snapshot Oktober 2026 (BMKG)", "h2")
P(f"Dari daftar 15 gempa M5+ terbaru BMKG, {len(BM['okt2026_dari_terkini'])} terjadi di Oktober 2026 — "
  "termasuk M6,1 Kodi, Sumba Barat Daya (4 Okt), M5,7 Sukabumi (11 Okt), M5,7 Pohuwato, "
  "Gorontalo (12 Okt), M5,4 Meulaboh, Aceh Barat (20 Okt), dan M5,2 Lebong, Bengkulu "
  "(22 Okt). Bulan yang sibuk bahkan menurut "
  "standar Indonesia.", "body")
CHART("12_snapshot_bmkg.png", "15 gempa M5+ terbaru versi BMKG, diambil 24 Oktober 2026.", ratio=0.44)
story.append(PageBreak())

# ---------- BAB 9 ----------
P("Bab 9 — Membangun Dashboard Power BI", "h1")
P("Folder powerbi/ berisi kit lengkap: 3 CSV star-schema, file DAX, spesifikasi "
  "layout 4 halaman, dan panduan rakit. Grain-nya sederhana: fact_gempa berisi "
  "1 baris = 1 kejadian, tanpa baris agregat — jadi tidak ada jebakan campuran level.", "body")
P("1. Import dan relasi", "h2")
B("Import fact_gempa.csv, dim_tanggal.csv, dim_wilayah.csv.")
B("Set Data Category lintang = Latitude, bujur = Longitude agar peta akurat.")
B("Relasi: dim_tanggal[tanggal] → fact_gempa[tanggal]; dim_wilayah[wilayah] → fact_gempa[wilayah]. Tandai dim_tanggal sebagai date table.")
P("2. Tempel DAX", "h2")
CODE("Total Gempa = COUNTROWS(fact_gempa)\n"
     "Gempa M6plus = CALCULATE([Total Gempa], fact_gempa[magnitudo] >= 6.0)\n"
     "Persen Dangkal = DIVIDE(CALCULATE([Total Gempa],\n"
     "    fact_gempa[kelas_kedalaman] = \"Dangkal (<70 km)\"), [Total Gempa])")
P("3. Bangun 4 halaman", "h2")
B("Halaman 1: Ringkasan (5 kartu KPI + peta + bar per tahun). Halaman 2: Peta & Wilayah.")
B("Halaman 3: Magnitudo & Kedalaman. Halaman 4: Tsunami & Snapshot BMKG + metodologi.")
P("4. Verifikasi", "h2")
B(f"Kartu KPI Halaman 1 harus menunjukkan: Total {fmt(M['total_kejadian'])}, "
  f"M5plus {fmt(MG['m5plus'])}, M6plus {fmt(MG['m6plus'])}, Maks M{MG['terbesar']['magnitudo']}, "
  f"Persen Dangkal {KD['Dangkal (<70 km)']['persen']}%. Kalau beda, cek slicer dan relasi.")
story.append(PageBreak())

# ---------- PENUTUP ----------
P("Penutup", "h1")
P("Tiga pesan utama project ini:", "body")
B(f"1. Gempa M≥4,5 terjadi rata-rata {fmt(int(F['rata_per_tahun_penuh']))} kali per tahun di Indonesia — dan {str(KD['Dangkal (<70 km)']['persen']).replace('.', ',')}% di antaranya dangkal.")
B("2. Risiko besar terkonsentrasi di timur: Halmahera–Maluku, Laut Banda, NTT, Sulawesi.")
B(f"3. Gempa M≥7 langka ({MG['m7plus']} kali dalam 12 tahun) tetapi pasti datang lagi — kesiapsiagaan bukan pilihan.")
P("Glosarium singkat", "h2")
B("Magnitudo: ukuran energi gempa di sumbernya (skala logaritmik).")
B("Episentrum: titik di permukaan bumi tepat di atas sumber gempa.")
B("Kedalaman (hiposentrum): jarak sumber gempa dari permukaan.")
B("Subduksi: zona satu lempeng menyelusup ke bawah lempeng lain — sumber gempa terbesar.")
B("MMI: skala intensitas guncangan yang dirasakan di permukaan (I–XII).")
P("Latihan untukmu: jalankan ulang scripts/fetch_data.py bulan depan, lalu "
  "scripts/assemble.py dan scripts/analyze.py. Bandingkan daftar 15 gempa M5+ "
  "terbaru BMKG dengan snapshot di modul ini — kamu baru saja memperbarui "
  "katalog gempa seperti analis kebencanaan sungguhan.", "body")

doc = SimpleDocTemplate(OUT, pagesize=landscape(A4),
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                        title="Modul Analisis Gempa Bumi Indonesia 2015-2026",
                        author="Baghiz Asshiddiqie Arasya")
doc.build(story)
print(f"Module saved: {OUT}")
