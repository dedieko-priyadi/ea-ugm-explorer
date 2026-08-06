# EA UGM Explorer — Diagram & Data Extraction

Mengekstrak data Enterprise Architecture UGM dari Sparx EA (SQL Server `eaugm_2025`) — diagram, elemen, relasi — untuk analisis & RAG.

## Temuan Eksplorasi (2026-08-07)

### Sumber data (3 jalur, semua terverifikasi)

| Jalur | Detail | Status |
|---|---|---|
| **DB Direct** | SQL Server `10.17.104.247`, DB `eaugm_2025`, user `sa` (kredensial via MCP ugmcore / config) | ✅ 107 tabel Sparx EA |
| **API Tim EA** | `http://10.17.104.247/audit/diagram-viewer/api.php` — `action=list` (6.151 diagram), `action=diagram&id=X` (objects+connectors JSON) | ✅ 200 |
| **WebEA (Sparx PCS)** | OSLC `completeresource/{GUID}` → diagram image base64 + imagemap | ✅ di server |

### Skala data
- **132.183 elemen** (`t_object`): Activity 48K, ActivityPartition 27K, Class 15K, Decision 13K, Device 7.7K, Package 7.1K, Event 7K, Risk 2.8K, UseCase 488...
- **6.151 diagram** (`t_diagram`): Analysis 5.408, Logical 411, Custom 158, Use Case 125, Deployment 7, Sequence 1
- **7.100 package** (`t_package`)
- `t_image` kosong → diagram digenerate dari struktur (objects + connectors)

### API diagram-viewer (tim EA — sangat berguna)
```
GET http://10.17.104.247/audit/diagram-viewer/api.php?action=list
  → {"count": 6151, "data": [{Diagram_ID, ea_guid, Name, Diagram_Type, PackageName}]}

GET http://10.17.104.247/audit/diagram-viewer/api.php?action=diagram&id=6138
  → {"diagram": {...}, "objects": [{Name, Object_Type, x, y, width, height, bgColor, Tags}],
     "connectors": [{Connector_Type, Start_Object_ID, End_Object_ID, Name, StartX/Y, EndX/Y}]}
```
- `index.php` = UI render → **SVG** (client-side, dari JSON)
- `query-diagram.ps1` = backend PowerShell (Get-DiagramList, Get-Diagram)
- `api.php` CORS `*` — bisa dipanggil dari NUC langsung

### MCP ugmcore (8+3 tools, via SSH→PowerShell→SQL)
- `test_connection`, `get_summary`, `search_elements`, `get_element_detail`, `list_business_processes`, `search_business_processes`, `list_applications`, `run_custom_query` + `search_qdrant` (17K vectors), `search_regulations`, `search_dsh`
- Backend: `C:\inetpub\wwwroot\ugmcore\ugmcore_ai\query-ai.ps1` (actions: test, summary, search, detail, proses-bisnis, search-proses, aplikasi)

### Qdrant semantic (sudah ada)
- Collection `ea_elements` (17K vectors) via `ea-qdrant-indexer`
- Search natural language via MCP `search_qdrant`

## Rencana (disetujui user 2026-08-07)

| Fase | Isi | Status |
|---|---|---|
| **A** | Diagram → Markdown struktural (6.151 diagram: nodes + connectors per diagram) | 🔄 jalan |
| **B** | Diagram → SVG/Image (render ulang dari objects+connectors; atau image via WebEA) | 🔄 jalan |
| **D** | Enhance skill `ugm-enterprise-architecture` — dokumentasikan semua jalur + query | ✅ v2.0.0 selesai |
| **C** | Dashboard EA lengkap (charts.db: proses, aplikasi, elemen per tipe, tren) | ⏳ |

## Progress & Iterasi (logbook)

### 2026-08-07 — Fase A & B SELESAI ✅
- **Fase A**: 6.151/6.151 markdown (28,5 MB, 0 gagal, 100% punya connectors) → `output/markdown/`
- **Fase B**: 6.151/6.151 SVG (78,7 MB, 100% valid closed tag) → `output/svg/`
- Total ~40 menit utk 2×6.151 API calls (sleep 0.15s/diagram)
- Korpus siap utk RAG (MD) + arsip visual (SVG)

### 2026-08-07 — Collector EA → charts.db SELESAI ✅
- `collection-engine/collect_ea_ugm.py` → 5 tabel di charts.db:
  - `r9_ea_packages` 7.100 | `r9_ea_elements` 132.183 | `r9_ea_connectors` 94.375 | `r9_ea_diagrams` 6.151 | `r9_ea_diagram_objects` 149.954
- Iterasi (pitfall → fix):
  1. executemany dict → tuple
  2. Query multi-line gagal via SSH → single-line
  3. ConvertTo-Json 132K rows hang (7+ menit) → **batch 25K per Object_ID**
  4. JSON terpotong di ~6.8MB (batas console SSH) → **tulis file JSON di server → baca via SFTP chunk 1MB**
  5. `t_diagram` pakai `cx`/`cy` (bukan Width/Height)
  6. `t_diagramobjects` pakai `RectLeft/Top/Right/Bottom` (bukan `rect`)
- Cron: `collect-ea-ugm` tiap hari 04:00 (job `9ee05160435f`, script `~/.hermes/scripts/collect_ea_ugm.py`)

### 2026-08-07 — Master plan EA Decision Intelligence
- `RENCANA-EA-DECISION-INTELLIGENCE.md` — dual-view (Rektorat/BTD), 6 metrik keputusan dari Risk 2.604/KPI 1.643/Regulasi 971/OC_Role 1.850

### 2026-08-07 — Skill v2.0
- `ugm-enterprise-architecture` → 3 jalur data + API diagram + pitfalls

## Referensi
- Skill: `sparx-ea-rag` (pola export → markdown → Qdrant), `ugm-enterprise-architecture`, `ea-qdrant-indexer`
- Server EA: `10.17.104.247` (Windows, IIS, SQL Server)
