"""Copia del Excel SIES con el estado de extracción por fila (destino x titulación Uniovi).

Verde   = la universidad de destino tiene extracción EXITOSA/CASI COMPLETA de una titulación de la
          misma familia que la titulación Uniovi de esa fila.
Naranja = hay extracción (>0 %) pero solo de otra familia de titulación (el grado más afín) o
          parcial: queda trabajo pendiente para esa fila.
Sin color = nada extraído.
Uso: python excel_extraction_status.py   (no usa API)
"""
import json
import re
import sys
from pathlib import Path

import openpyxl
import xlrd
from openpyxl.styles import Alignment, Font, PatternFill

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_extraction as be  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "destinosErasmus_SIES_25-26_enviar_profes.xls"
OUT = ROOT / "destinosErasmus_SIES_25-26_estado_extraccion.xlsx"
GREEN = PatternFill("solid", fgColor="C6EFCE")
ORANGE = PatternFill("solid", fgColor="FFD8A8")
COL_OFERTA, COL_INST, COL_COD = 3, 8, 9  # 0-based
EXTRA = 33  # primera columna nueva (0-based)


def fam_uniovi(t: str) -> str:
    t = t.lower()
    if "telecom" in t or "teleco" in t:
        return "tele"
    if "inform" in t or "datos" in t:
        return "info"
    if "química" in t or "quimica" in t:
        return "quim"
    if any(k in t for k in ("eléctrica", "electrica", "electrónica", "electronica", "automatiz", "energ", "potencia")):
        return "elec"
    if any(k in t for k in ("mecánica", "mecanica", "industrial", "tecnologías ind", "mecatr", "materiales", "ing mec", "ing de org")):
        return "mec"
    return "otro"


def fam_extraida(g: str) -> str:
    g = g.lower()
    if re.search(r"telecom|communication|t[eé]l[eé]com", g):
        return "tele"
    if re.search(r"inform|comput|software|data", g) and not re.search(r"electr|elettr", g):
        return "info"
    if re.search(r"chem|qu[ií]m|chim", g):
        return "quim"
    if re.search(r"electr|elettr|elektro|automat|control|energ|potencia|el[eé]ctric", g):
        return "elec"
    if re.search(r"mec|maschinen|meccan|industr|manufact|production|produç|engineering$", g):
        return "mec"
    return "otro"


def norm(code: str) -> str:
    return re.sub(r"\s+", " ", str(code)).strip().upper()


def main() -> None:
    data = be.build()
    by_slug = {u["slug"]: u for u in data["unis"]}
    # código Erasmus -> slug
    code2slug = {}
    extra = {}  # código -> slugs de grados extra (convenio_extra)
    for u in be.universities():
        if u.get("erasmus_code"):
            if "convenio_extra" in u.get("grupos", []):
                extra.setdefault(norm(u["erasmus_code"]), []).append(u["slug"])
            else:
                code2slug[norm(u["erasmus_code"])] = u["slug"]
    sies = json.loads((ROOT / "ingenium_scraper" / "db" / "destinos_sies.json").read_text(encoding="utf-8"))
    for r in sies:
        if r.get("slug"):
            code2slug.setdefault(norm(r["codigo_erasmus"]), r["slug"])

    def slug_for(code: str):
        n = norm(code)
        if n in code2slug:
            return code2slug[n]
        pre, _, rest = n.partition(" ")
        cand = f"ec_{pre.lower()}_{rest.replace(' ', '').lower()}"
        return cand if cand in by_slug else None

    wb_in = xlrd.open_workbook(str(SRC))
    sh0 = wb_in.sheet_by_index(0)

    class _Sh:  # filas con longitud irregular: relleno seguro
        nrows = sh0.nrows

        @staticmethod
        def cell_value(r, c):
            row = sh0.row_values(r)
            return row[c] if c < len(row) else ""

    sh = _Sh
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Listado SIES + extracción"
    for r in range(sh.nrows):
        for c in range(33):
            v = sh.cell_value(r, c)
            if v != "":
                ws.cell(r + 1, c + 1, v)
    heads = ["Estado extracción", "Titulación extraída", "% extraído (destino)", "Slug pipeline"]
    for i, h in enumerate(heads):
        cell = ws.cell(1, EXTRA + i + 1, h)
        cell.font = Font(bold=True)
    for c in range(1, 33):
        ws.cell(1, c).font = Font(bold=True)

    stats = {"verde": 0, "naranja": 0, "sin": 0}
    seen_dest = {}
    for r in range(1, sh.nrows):
        code = sh.cell_value(r, COL_COD)
        oferta = str(sh.cell_value(r, COL_OFERTA)).strip()
        if not code and not oferta:
            continue
        slug = slug_for(code) if code else None
        cands = [by_slug[x] for x in ([slug] if slug else []) + extra.get(norm(code), []) if x in by_slug and by_slug[x]["pct"] > 0]
        status, fill = "Sin extraer", None
        grado, pct = "", ""
        if cands:
            fam_row = fam_uniovi(oferta)
            ok_same = [u for u in cands if u["dx"]["nivel"] in ("EXITOSO", "CASI COMPLETO") and fam_extraida(u["dx"].get("grado") or "") == fam_row != "otro"]
            same = [u for u in cands if fam_extraida(u["dx"].get("grado") or "") == fam_row != "otro"]
            best = (ok_same or same or cands)[0]
            grado, pct = " | ".join((u["dx"].get("grado") or "")[:80] for u in cands), best["pct"]
            if ok_same:
                status, fill = "Completa (grado afín extraído)", GREEN
            elif same:
                status, fill = "Parcial: grado afín con extracción incompleta", ORANGE
            else:
                status, fill = f"Solo extraído otro grado ({(cands[0]['dx'].get('grado') or '')[:60]}); pendiente este", ORANGE
        stats["verde" if fill is GREEN else "naranja" if fill is ORANGE else "sin"] += 1
        for c in (COL_OFERTA, COL_INST, COL_COD):
            if fill:
                ws.cell(r + 1, c + 1).fill = fill
        for i, v in enumerate([status, grado, pct, ", ".join([slug or ""] + extra.get(norm(code), []))]):
            cell = ws.cell(r + 1, EXTRA + i + 1, v)
            if fill and i == 0:
                cell.fill = fill
        seen_dest[norm(code)] = status
    for col, w in {"D": 42, "I": 40, "J": 16, "AH": 46, "AI": 50, "AJ": 12, "AK": 22}.items():
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"

    ley = wb.create_sheet("Leyenda")
    rows = [
        ("Verde", "La universidad de destino tiene extracción exitosa/casi completa de una titulación de la misma familia que la titulación Uniovi de la fila (mecánica-industrial, eléctrica-electrónica, química, informática-datos, telecomunicación)."),
        ("Naranja", "Hay extracción del destino, pero solo del grado más afín de otra familia (o incompleta): faltan grados para esta fila, candidatos a extraer."),
        ("Sin color", "Nada extraído del destino (bloqueado, sin fuente o fuera de alcance)."),
        ("Familias", "La familia de la titulación extraída se infiere por palabras clave del nombre; revisar los casos dudosos con la columna 'Titulación extraída'."),
        ("Datos", f"Generado desde ingenium_scraper (build_extraction). Filas: verde {stats['verde']}, naranja {stats['naranja']}, sin extraer {stats['sin']}."),
    ]
    for i, (a, b) in enumerate(rows, 1):
        ley.cell(i, 1, a).font = Font(bold=True)
        ley.cell(i, 2, b).alignment = Alignment(wrap_text=True, vertical="top")
    ley["A1"].fill, ley["A2"].fill = GREEN, ORANGE
    ley.column_dimensions["A"].width = 14
    ley.column_dimensions["B"].width = 120
    wb.save(OUT)
    print(OUT, stats)


if __name__ == "__main__":
    main()
