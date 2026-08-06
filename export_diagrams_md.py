#!/usr/bin/env python3
"""Fase A — Export SEMUA diagram EA UGM → markdown struktural.
Sumber: API diagram-viewer tim EA (http://10.17.104.247/audit/diagram-viewer/api.php).
Output: ~/ea-ugm-explorer/output/markdown/<Diagram_ID>-<slug>.md
"""
import json, os, re, sys, time, urllib.request

API = "http://10.17.104.247/audit/diagram-viewer/api.php"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "markdown")
LIMIT = int(os.environ.get("EA_LIMIT", "0"))  # 0 = semua

def http_get(url, retries=3):
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read())
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(2)

def slugify(name):
    s = re.sub(r"[^\w\s-]", "", name or "").strip().lower()
    return re.sub(r"[\s_]+", "-", s)[:60] or "diagram"

def obj_label(o):
    return o.get("Name") or f"[{o.get('Object_Type','')}]"

def to_md(diagram, objects, connectors):
    name = diagram.get("Name", "Untitled")
    md = [f"# {name}", ""]
    md.append(f"- **Package:** {diagram.get('PackageName','')}")
    md.append(f"- **Type:** {diagram.get('Diagram_Type','')}")
    md.append(f"- **ID:** {diagram.get('Diagram_ID')}")
    md.append(f"- **GUID:** {diagram.get('ea_guid','')}")
    md.append(f"- **Size:** {diagram.get('Width')}x{diagram.get('Height')}")
    md.append("")

    # Node mapping
    obj_map = {o["Object_ID"]: o for o in objects}
    md.append("## Nodes")
    md.append("| ID | Name | Type | Stereotype | Author | Status |")
    md.append("|---|---|---|---|---|---|")
    for o in sorted(objects, key=lambda x: x.get("Object_ID", 0)):
        md.append(f"| {o.get('Object_ID')} | {obj_label(o).replace('|','/')} | {o.get('Object_Type','')} | "
                  f"{o.get('Stereotype','') or ''} | {o.get('Author','') or ''} | {o.get('Status','') or ''} |")
    md.append("")

    md.append("## Connectors")
    md.append("| From | To | Type | Stereotype |")
    md.append("|---|---|---|---|")
    for c in connectors:
        src = obj_map.get(c.get("Start_Object_ID"), {})
        dst = obj_map.get(c.get("End_Object_ID"), {})
        md.append(f"| {obj_label(src)} | {obj_label(dst)} | {c.get('Connector_Type','')} | {c.get('Stereotype','') or ''} |")
    md.append("")
    return "\n".join(md)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Ambil daftar diagram...")
    lst = http_get(f"{API}?action=list")
    diagrams = lst.get("data", [])
    print(f"Total diagram: {len(diagrams)}")
    if LIMIT:
        diagrams = diagrams[:LIMIT]
        print(f"Batas: {LIMIT}")

    ok = fail = 0
    for i, d in enumerate(diagrams):
        did = d["Diagram_ID"]
        try:
            det = http_get(f"{API}?action=diagram&id={did}")
            if not det.get("success", True):
                continue
            md = to_md(det.get("diagram", {}), det.get("objects", []), det.get("connectors", []))
            fname = f"{did}-{slugify(d.get('Name'))}.md"
            with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
                f.write(md)
            ok += 1
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/{len(diagrams)}...")
        except Exception as e:
            fail += 1
            print(f"  ✗ {did}: {e}")
        time.sleep(0.15)  # jangan banjiri server

    print(f"\nSELESAI: {ok} OK, {fail} gagal → {OUT_DIR}")

if __name__ == "__main__":
    main()
