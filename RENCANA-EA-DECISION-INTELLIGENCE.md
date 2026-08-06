# EA Decision Intelligence — Rencana Besar (Master Plan)

**Tanggal**: 2026-08-07 | **Status**: DISETUJUI user — lanjut eksekusi
**Repo**: https://github.com/dedieko-priyadi/ea-ugm-explorer

---

## 1. Visi

Mengubah 132.183 elemen + 6.151 diagram Enterprise Architecture UGM dari "data arsip" menjadi **mesin pengambilan keputusan** untuk dua audiens:

| Audiens | Lensa | Pertanyaan utama |
|---|---|---|
| **Rektorat** | Strategis | Di mana UGM boros? Unit mana tertinggal digital? Proses mana berisiko? |
| **BTD** | Operasional | Unit mana yang perlu didampingi? Proses apa yang harus diperbaiki/diotomasi? |

Prinsip: **setiap metrik punya "alasan keputusan"** — bukan sekadar angka.

## 2. Temuan Kunci (mengubah segalanya)

EA UGM bukan sekadar diagram proses — sudah ada **lapisan governance lengkap**:

| Stereotype | Jumlah | Makna keputusan |
|---|---|---|
| Activity | 47.925 | Proses inti |
| Pool/Lane | 27.296 | Struktur BPMN (siapa melakukan) |
| Gateway | 13.545 | Percabangan keputusan |
| **Risk** | 2.604 | ⭐ Manajemen risiko terpetakan |
| **KPI** | 1.643 | ⭐ Indikator kinerja per proses |
| **Regulation** | 971 | ⭐ Regulasi terhubung proses |
| **OC_Role** | 1.850 | ⭐ Peran organisasi (RACI) |
| Mitigasi | 345 | Mitigasi risiko |
| Kontrol | 255 | Kontrol internal |
| Layanan | 179 | Layanan (ITIL) |

Connector: ControlFlow 70.374, **Dependency 20.810** (proses↔aplikasi/regulasi — bahan gap analysis), Realisation 8.

**Implikasi**: data risiko/KPI/regulasi/peran SUDAH dimodelkan tim EA — tinggal membaca relasinya.

## 3. Metrik Keputusan (turunan langsung dari data)

### 3.1 KPI Coverage (Rektorat)
- Proses tanpa KPI = unit tidak terukur → prioritas perbaikan manajemen kinerja
- KPI per unit → peta budaya pengukuran

### 3.2 Risk Map (BTD + Rektorat)
- Proses paling berisiko (jumlah Risk terhubung) → prioritas kontrol
- Risk tanpa Mitigasi (345 mitigasi vs 2.604 risk) → gap manajemen risiko
- Risk vs Kontrol (255) → kesenjangan pengendalian

### 3.3 Compliance (Rektorat)
- Proses wajib Regulasi tanpa Kontrol → risiko kepatuhan
- Regulasi tanpa proses pelaksana → regulasi "menggantung"

### 3.4 Gap Digitalisasi (BTD)
- Proses ↔ Aplikasi via Dependency (20.810) → unit mana paling manual
- ApplicationService/Layanan tanpa proses → aplikasi yatim

### 3.5 Struktur & Anomali (BTD)
- Proses terputus (node tanpa exit) → SOP tidak tuntas
- Duplikasi lintas unit → tumpang tindih tupoksi
- Kompleksitas (50+ node) → kandidat restrukturisasi
- OC_Role ↔ proses → RACI matrix otomatis

### 3.6 Kematangan Digital per Unit (Rektorat)
- % proses didukung aplikasi per package/unit → heatmap digitalisasi
- Dasar alokasi anggaran IT

## 4. Arsitektur Pipeline

```
EA DB (SQL Server 10.17.104.247, eaugm_2025) + API diagram-viewer
  │
  ├── [1] Collector EA → charts.db (cron)
  │       r9_ea_diagrams (6.151)   — dari API list
  │       r9_ea_elements (132K)    — t_object + stereotype + package
  │       r9_ea_connectors (92K+)  — t_connector + type
  │       r9_ea_packages (7.100)   — t_package hierarchy
  │       r9_ea_diagram_objects    — posisi elemen dalam diagram
  │
  ├── [2] Export Diagram (jalan)
  │       markdown (6.151) → RAG korpus
  │       svg (6.151) → visual
  │
  └── [3] EA Decision Dashboard (Streamlit, 6 tab)
          Overview | KPI Coverage | Risk Map | Compliance | Gap Digitalisasi | Struktur
          → subpath /ea-decision/ funnel
```

## 5. Fase Eksekusi

| Fase | Isi | Status |
|---|---|---|
| A | Export diagram → markdown (6.151) | 🔄 jalan (MD ~1.509) |
| B | Export diagram → SVG (6.151) | 🔄 jalan (SVG ~1.479) |
| **1** | **Collector EA → charts.db** (dump t_object/t_connector/t_diagram/t_package + relasi) | ⏳ berikutnya |
| **2** | Tunggu/sinkron dengan export A-B | 🔄 paralel |
| C | EA Decision Dashboard (6 tab, dual-view) | ⏳ |
| D | Enhance skill ugm-enterprise-architecture | ✅ v2.0.0 selesai |

## 6. Risk & Catatan

- `t_image` kosong → image asli hanya via WebEA OSLC (butuh auth)
- `get_summary` MCP bug (16 diagram) — pakai `test_connection` untuk angka benar
- SSH server EA: paramiko password (bukan key)
- Full dump 132K elemen perlu streaming (jangan satu query raksasa)
- Package → unit/fakultas mapping perlu diverifikasi (hierarchy 7.100)

## 7. Deliverable Akhir

1. **EA Decision Dashboard** — https://nuc-nuc7i5bnh-1.tail758353.ts.net/ea-decision/ (6 tab)
2. **Korpus RAG** — 6.151 markdown diagram → Qdrant (collection `ea_diagrams`)
3. **Arsip SVG** — 6.151 diagram visual
4. **Skill v2.0** — terdokumentasi lengkap
5. **Laporan berkala** — cron "10 temuan EA bulan ini" untuk pimpinan
