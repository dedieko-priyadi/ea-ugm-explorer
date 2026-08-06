#!/usr/bin/env python3
"""Fase B — Export SEMUA diagram EA UGM → SVG (render ulang dari objects+connectors).
Sumber: API diagram-viewer tim EA. Output: ~/ea-ugm-explorer/output/svg/<id>-<slug>.svg
Pola render: port dari diagram-viewer/index.php tim EA.
"""
import json, os, re, sys, time, urllib.request, html

API = "http://10.17.104.247/audit/diagram-viewer/api.php"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "svg")
LIMIT = int(os.environ.get("EA_LIMIT", "0"))

def http_get(url, retries=3):
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read())
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(2)

def slugify(name):
    s = re.sub(r"[^\w\s-]", "", name or "").strip().lower()
    return re.sub(r"[\s_]+", "-", s)[:60] or "diagram"

def shape_style(o):
    """Color per type — port dari index.php tim EA."""
    t = o.get("Object_Type", "")
    fill, stroke, rx, ry = "#E8F0FE", "#8AB4F8", 6, 6
    if t in ("Event", "StartEvent"):
        fill, stroke, rx, ry = "#E6F4EA", "#34A853", None, None  # circle
    elif t == "EndEvent":
        fill, stroke, rx, ry = "#FCE8E6", "#EA4335", None, None
    elif t in ("Decision", "Gateway"):
        fill, stroke = "#FFF3E0", "#FB8C00"
    elif t == "Activity":
        fill, stroke = "#E3F2FD", "#1E88E5"
    elif t == "Artifact":
        fill, stroke = "#F3E5F5", "#8E24AA"
    elif t == "Class":
        fill, stroke = "#FFF9C4", "#F9A825"
    elif t == "Package":
        fill, stroke = "#EFEBE9", "#6D4C41"
    elif t == "Actor":
        fill, stroke = "#E8EAF6", "#5C6BC0"
    st = o.get("Stereotype", "")
    if st == "BusinessProcess":
        fill, stroke = "#E1F5FE", "#0288D1"
    elif st == "ApplicationComponent":
        fill, stroke = "#E0F2F1", "#00897B"
    elif st == "ApplicationService":
        fill, stroke = "#FFF8E1", "#F9A825"
    return fill, stroke, rx, ry

def render_svg(diagram, objects, connectors):
    W, H = diagram.get("Width", 800), diagram.get("Height", 600)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
    parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>')

    # Connectors (di belakang)
    for c in connectors:
        sx, sy, ex, ey = c.get("StartX", 0), c.get("StartY", 0), c.get("EndX", 0), c.get("EndY", 0)
        lc = c.get("LineColor", "#000000")
        parts.append(f'<path d="M{sx},{sy} L{ex},{ey}" stroke="{lc}" stroke-width="1.5" fill="none"/>')
        # Arrow
        dx, dy = ex - sx, ey - sy
        ln = (dx*dx + dy*dy) ** 0.5 or 1
        ux, uy = dx/ln, dy/ln
        a = 8
        p1 = f"{ex},{ey}"
        p2 = f"{ex-ux*a+uy*a/2},{ey-uy*a-ux*a/2}"
        p3 = f"{ex-ux*a-uy*a/2},{ey-uy*a+ux*a/2}"
        parts.append(f'<polygon points="{p1} {p2} {p3}" fill="{lc}"/>')
        if c.get("Name"):
            parts.append(f'<text x="{(sx+ex)/2}" y="{(sy+ey)/2-6}" font-size="11" text-anchor="middle">{html.escape(c["Name"])}</text>')

    # Objects
    for o in objects:
        x, y, w, h = o.get("x", 0), o.get("y", 0), o.get("width", 100), o.get("height", 40)
        fill, stroke, rx, ry = shape_style(o)
        name = html.escape(o.get("Name") or "(unnamed)")
        st = html.escape(o.get("Stereotype") or "")
        t = html.escape(o.get("Object_Type") or "")
        cx, cy = x + w/2, y + h/2
        if rx is None:
            # circle (event)
            r = min(w, h) / 2
            parts.append(f'<circle cx="{x+w/2}" cy="{y+h/2}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        else:
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        # Text
        max_chars = max(int(w / 6.5), 4)
        disp = (o.get("Name") or "(unnamed)")
        if len(disp) > max_chars + 2:
            disp = disp[:max_chars] + "…"
        parts.append(f'<text x="{cx}" y="{cy-4}" font-size="12" text-anchor="middle" dominant-baseline="middle">{html.escape(disp)}</text>')
        if st:
            parts.append(f'<text x="{cx}" y="{cy+12}" font-size="10" text-anchor="middle" dominant-baseline="middle" fill="#555">«{st}»</text>')
        parts.append(f'<text x="{cx}" y="{y+h-4}" font-size="9" text-anchor="middle" fill="#777">{t}</text>')

    parts.append("</svg>")
    return "\n".join(parts)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Ambil daftar diagram...")
    lst = http_get(f"{API}?action=list")
    diagrams = lst.get("data", [])
    print(f"Total: {len(diagrams)}")
    if LIMIT:
        diagrams = diagrams[:LIMIT]

    ok = fail = 0
    for i, d in enumerate(diagrams):
        did = d["Diagram_ID"]
        try:
            det = http_get(f"{API}?action=diagram&id={did}")
            if not det.get("success", True):
                continue
            svg = render_svg(det.get("diagram", {}), det.get("objects", []), det.get("connectors", []))
            fname = f"{did}-{slugify(d.get('Name'))}.svg"
            with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
                f.write(svg)
            ok += 1
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/{len(diagrams)}...")
        except Exception as e:
            fail += 1
            print(f"  ✗ {did}: {e}")
        time.sleep(0.15)

    print(f"\nSELESAI: {ok} OK, {fail} gagal → {OUT_DIR}")

if __name__ == "__main__":
    main()
