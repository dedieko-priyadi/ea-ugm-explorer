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
| **A** | Diagram → Markdown struktural (6.151 diagram: nodes + connectors per diagram) | ⏳ |
| **B** | Diagram → SVG/Image (render ulang dari objects+connectors; atau image via WebEA) | ⏳ |
| **D** | Enhance skill `ugm-enterprise-architecture` — dokumentasikan semua jalur + query | ⏳ |
| **C** | Dashboard EA lengkap (charts.db: proses, aplikasi, elemen per tipe, tren) | ⏳ |

## Referensi
- Skill: `sparx-ea-rag` (pola export → markdown → Qdrant), `ugm-enterprise-architecture`, `ea-qdrant-indexer`
- Server EA: `10.17.104.247` (Windows, IIS, SQL Server)
