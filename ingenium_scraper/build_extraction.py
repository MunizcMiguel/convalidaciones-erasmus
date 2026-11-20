"""Estado de la extracción por universidad -> botón «Extraction State» del explorador.

Calcula, SIN llamar a ninguna API, para cada universidad del pipeline:
  - estado de cada asignatura del catálogo:  ok (verde) / parcial (naranja) / sin guía (rojo)
  - % de extracción de la universidad y un diagnóstico esquemático (estado, fallos, causa, mejoras)
y una métrica global.

Uso:
  python build_extraction.py            # escribe explorer/extraction.json y lo inyecta en explorer/index.html
  (build_explorer.py también lo inyecta al regenerar el explorador)

Definiciones (se muestran también en la interfaz):
  verde   = JSON estructurado (Fase 3) con temario Y resultados de aprendizaje.
  naranja = extracción parcial: JSON al que le falta temario o resultados de aprendizaje,
            o Markdown listo pero Fase 3 aún pendiente.
  rojo    = asignatura del catálogo sin guía docente descargada (sin Markdown ni JSON).
  % universidad = (verdes + 0,5·naranjas) / asignaturas del catálogo   (0 % si no hay catálogo)
  Métrica global = COBERTURA × PROFUNDIDAD
      COBERTURA   = universidades con algo extraído / universidades en el ámbito
      PROFUNDIDAD = % medio de extracción de las universidades con algo extraído
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from common.util import load_catalog, safe_name, uni_dir, universities  # noqa: E402
import build_explorer as be  # noqa: E402  (COORDS de las universidades ya ubicadas)

OUT = ROOT / "explorer"
EXCLUIDAS = {"mu_sofia"}  # N/A: universidad médica sin grado afín (ver config)

# slug -> (ciudad, lat, lon) de las universidades que aún no estaban en el explorador
EXTRA_COORDS = {
    "es_autonoma_barcelona": ("Bellaterra", 41.50, 2.10), "es_catolica_santa_teresa_jesus_": ("Ávila", 40.66, -4.70),
    "es_europea_madrid": ("Villaviciosa de Odón", 40.37, -3.90), "es_francisco_vitoria": ("Pozuelo de Alarcón", 40.44, -3.80),
    "es_pompeu_fabra": ("Barcelona", 41.39, 2.19), "es_a_coruna": ("Ferrol", 43.48, -8.23),
    "es_cantabria": ("Santander", 43.47, -3.80), "es_castilla_mancha": ("Ciudad Real", 38.99, -3.92),
    "es_cordoba": ("Córdoba", 37.91, -4.72), "es_deusto": ("Bilbao", 43.27, -2.94),
    "es_huelva": ("Huelva", 37.27, -6.93), "es_las_palmas_gran_canaria": ("Las Palmas", 28.07, -15.45),
    "es_lleida": ("Lleida", 41.62, 0.62), "es_sevilla": ("Sevilla", 37.36, -5.99),
    "ec_a_graz09": ("Graz", 47.07, 15.43), "ec_a_innsbru01": ("Innsbruck", 47.26, 11.39),
    "ec_a_wien02": ("Viena", 48.20, 16.37), "ec_bg_rousse01": ("Ruse", 43.85, 25.97),
    "ec_cz_brno01": ("Brno", 49.20, 16.60), "ec_cz_ostrava01": ("Ostrava", 49.83, 18.16),
    "ec_cz_praha10": ("Praga", 50.10, 14.39), "ec_d_berlin02": ("Berlín", 52.51, 13.33),
    "ec_d_bielefe02": ("Bielefeld", 52.02, 8.53), "ec_d_clausth01": ("Clausthal-Zellerfeld", 51.80, 10.34),
    "ec_d_gelsenk02": ("Gelsenkirchen", 51.52, 7.10), "ec_d_hamburg03": ("Hamburgo-Harburg", 53.46, 9.97),
    "ec_d_ingolst01": ("Ingolstadt", 48.77, 11.43), "ec_d_karlsru05": ("Karlsruhe (convenio)", 49.01, 8.37),
    "ec_d_munchen02": ("Múnich", 48.15, 11.57), "ec_d_osnabru02": ("Osnabrück", 52.28, 8.02),
    "ec_d_paderbo01": ("Paderborn", 51.71, 8.77), "ec_f_belfort06": ("Belfort", 47.64, 6.86),
    "ec_f_besanco01": ("Besançon", 47.24, 6.02), "ec_f_besanco06": ("Besançon (ENSMM)", 47.26, 6.04),
    "ec_f_dijon01": ("Dijon", 47.31, 5.07), "ec_f_grenobl22": ("Grenoble", 45.19, 5.72),
    "ec_f_nancy43": ("Nancy", 48.69, 6.18), "ec_f_nantes07": ("Nantes", 47.25, -1.55),
    "ec_f_tarbes03": ("Tarbes", 43.23, 0.07), "ec_hu_budapes02": ("Budapest", 47.48, 19.06),
    "ec_i_ancona01": ("Ancona", 43.59, 13.51), "ec_i_bari05": ("Bari", 41.11, 16.88),
    "ec_i_bologna01": ("Bolonia", 44.50, 11.35), "ec_i_cagliar01": ("Cagliari", 39.22, 9.11),
    "ec_i_cosenza01": ("Rende", 39.36, 16.23), "ec_i_firenze01": ("Florencia", 43.78, 11.25),
    "ec_i_l_aquil01": ("L'Aquila", 42.35, 13.40), "ec_i_milano02": ("Milán", 45.48, 9.23),
    "ec_i_parma01": ("Parma", 44.77, 10.31), "ec_i_perugia01": ("Perugia", 43.11, 12.39),
    "ec_i_salerno01": ("Fisciano", 40.77, 14.79), "ec_i_trento01": ("Trento", 46.07, 11.12),
    "ec_p_arcozel01": ("Barcelos", 41.53, -8.62), "ec_p_coimbra02": ("Coimbra", 40.21, -8.41),
    "ec_p_lisboa03": ("Lisboa (Nova)", 38.66, -9.20), "ec_p_lisboa109": ("Lisboa (IST)", 38.74, -9.14),
    "ec_p_porto02": ("Oporto", 41.18, -8.60), "ec_pl_elblag01": ("Elbląg", 54.16, 19.40),
    "ec_pl_radom01": ("Radom", 51.40, 21.15), "ec_pl_rzeszow01": ("Rzeszów", 50.02, 21.99),
    "ec_pl_sanok01": ("Sanok", 49.56, 22.21), "ec_pl_wroclaw02": ("Wrocław", 51.11, 17.06),
    "ec_ro_petrosa01": ("Petroșani", 45.41, 23.37), "ec_ro_timisoa04": ("Timișoara", 45.75, 21.23),
    "ec_s_jonkopi01": ("Jönköping", 57.78, 14.16), "ec_s_lulea01": ("Luleå", 65.62, 22.14),
    "ec_sk_zilina01": ("Žilina", 49.21, 18.76), "ec_tr_ankara02": ("Ankara", 39.94, 32.82),
    "ec_tr_bartin01": ("Bartın", 41.64, 32.34), "ec_tr_duzce01": ("Düzce", 40.84, 31.16),
    "ec_tr_konya05": ("Konya", 37.87, 32.51), "ec_tr_kutahya01": ("Kütahya", 39.42, 29.98),
    "ec_tr_sakarya01": ("Sakarya", 40.74, 30.33), "ec_tr_zonguld01": ("Zonguldak", 41.45, 31.79),
    "uniovi_giti": ("Gijón (EPI · GITI)", 43.525, -5.615), "uniovi_gieia": ("Gijón (EPI · GIEIA)", 43.515, -5.605),
    "uniovi_gie": ("Gijón (EPI · GIE)", 43.530, -5.630), "uniovi_giqi": ("Gijón (EPI · GIQI)", 43.510, -5.630),
    "uniovi_gioi": ("Gijón (EPI · GIOI)", 43.520, -5.640),
    "ec_uk_glasgow02": ("Glasgow", 55.86, -4.24), "ec_uk_liverpo02": ("Liverpool", 53.41, -2.98),
}

# (regex sobre las notas del worker) -> (causa, mejora)
CAUSAS = [
    (r"robots", "robots.txt impide el rastreo automático de la zona de guías",
     "Pedir los datos a la universidad (correo tipo «data request») o usar un export oficial; NO saltarse robots.txt."),
    (r"\b403\b|desaf[ií]o|challenge|cloudflare|captcha|anti-?bot", "Filtro anti-bot / 403 en el servidor",
     "Solicitud de datos a la universidad; reintentar en otra franja con el cliente educado (sin cambiar UA)."),
    (r"certificad|tls|ssl", "Certificado TLS inválido en el servidor de guías",
     "Avisar al servicio informático de la universidad o pedir los PDFs; no desactivar la verificación TLS."),
    (r"login|autenticaci|credencial|intranet|moses|sso", "Las guías están tras un login / sistema interno",
     "Solicitar acceso institucional (convenio) o exportación de módulos; sin sesión no es viable."),
    (r"javascript|\bjs\b|spa\b|din[aá]mic|onlineservices|se carga", "Contenido cargado por JavaScript (sin HTML estático)",
     "Buscar API/JSON público documentado o PDF del plan; si no existe, petición de datos."),
    (r"sin gu[ií]as? p[uú]blic|no hay gu[ií]as|no publica|sin_guia|sin guía", "La universidad no publica guías docentes por asignatura",
     "Pedir fichas de asignatura/Modulhandbuch en PDF a la oficina de relaciones internacionales."),
    (r"pdf", "Guías solo en PDF (extracción menos fiable)",
     "Mantener extractor de PDF por tablas/regiones y revisar muestras; valorar OCR si son escaneados."),
    (r"extinci|no se imparte|suspendid", "Titulación en extinción / no ofertada este curso",
     "Confirmar con la universidad si existe grado equivalente vigente."),
    (r"no (se )?localiz|no se encontr|no se identific|no encontr", "No se localizó el sitio/plan de la titulación",
     "Búsqueda manual guiada del plan de estudios o contacto con el coordinador Erasmus."),
    (r"inaccesible|no responde|timeout|unreachable|host", "Servidor inaccesible o sin respuesta",
     "Reintentar más tarde; si persiste, contactar con la universidad."),
]


def classify_course(slug: str, entry: dict) -> tuple[str, list[str], bool, bool]:
    """-> (estado, secciones_que_faltan, tiene_md, tiene_json)"""
    stem = safe_name(entry.get("codigo_asignatura", ""))
    md = uni_dir(slug) / "raw_markdown" / f"{stem}.md"
    js = uni_dir(slug) / "structured_data" / f"{stem}.json"
    has_md, has_js = md.exists(), js.exists()
    if has_js:
        try:
            d = json.loads(js.read_text(encoding="utf-8"))
        except ValueError:
            return "parcial", ["json_ilegible"], has_md, True
        miss = []
        if not d.get("syllabus_topics"):
            miss.append("temario")
        if not d.get("learning_outcomes"):
            miss.append("resultados de aprendizaje")
        return ("ok" if not miss else "parcial"), miss, has_md, True
    if has_md:
        return "parcial", ["Fase 3 pendiente"], True, False
    return "sin_guia", [], False, False


def diagnose(u: dict, cat: dict | None, tot: dict, courses: list[dict]) -> dict:
    meta = (cat or {}).get("meta", {})
    estado_cat = meta.get("estado") or ("sin catálogo" if not cat else "?")
    notas = (meta.get("notas") or "").strip()
    n, g, o, r = tot["n"], tot["ok"], tot["par"], tot["red"]
    pend = sum(1 for c in courses if "Fase 3 pendiente" in c["m"])
    miss = Counter(m for c in courses for m in c["m"] if m != "Fase 3 pendiente")
    fuentes = Counter((a.get("tipo_fuente") or "n/d") for a in (cat or {}).get("asignaturas", []))
    texto = (notas + " " + str(meta.get("estrategia_fuente") or "")).lower()
    causas, mejoras = [], []
    for rx, causa, mejora in CAUSAS:
        if re.search(rx, texto):
            causas.append(causa)
            mejoras.append(mejora)
    if not cat:
        causas, mejoras = ["Sin catálogo: la universidad no ha pasado por la Fase 1-2 o quedó bloqueada en el reconocimiento"], \
            ["Lanzar/relanzar el reconocimiento (BRIEF_ES.md / BRIEF_CONVENIO.md) o pedir los datos a la universidad."]
    if r and not causas:
        causas = ["Hay asignaturas en el catálogo sin guía descargada (causa no identificada en las notas)"]
        mejoras = ["Revisar `notas_descubrimiento.md` y la columna `url_guia_docente` del catálogo; reintentar sólo las filas rojas."]
    if pend:
        mejoras.insert(0, f"Ejecutar Fase 3 (`python semantic_parser.py --unis {u['slug']}`): {pend} guías con Markdown pendientes de JSON.")
    if miss:
        mejoras.append("Revisar el extractor/prompt para: " + ", ".join(f"{k} ({v})" for k, v in miss.most_common(3)) + ".")
    if n and g == n:
        nivel = "EXITOSO"
    elif g + o == 0:
        nivel = "SIN DATOS"
    elif (g + 0.5 * o) / max(n, 1) >= 0.8:
        nivel = "CASI COMPLETO"
    else:
        nivel = "PARCIAL"
    fallos = []
    if r:
        fallos.append(f"{r} asignaturas del catálogo sin guía descargada")
    if pend:
        fallos.append(f"{pend} con Markdown pero sin JSON (Fase 3 pendiente: créditos/tope de Gemini u otro error)")
    for k, v in miss.most_common():
        fallos.append(f"{v} JSON sin {k}")
    if not fallos and n:
        fallos.append("ninguno detectado")
    reco = []
    if nivel == "EXITOSO":
        reco.append("Nada que corregir; muestrear 3-5 fichas por si hay deriva de calidad.")
    if estado_cat == "parcial" and g + o:
        reco.append("Catálogo marcado `parcial`: verificar que el plan cubre los cursos 2.º-4.º antes de usarlo para convalidar.")
    if u["slug"] == "ec_d_karlsru05":
        reco.append("Posible DUPLICADO de `hka` (misma universidad, Karlsruhe UAS): fusionar o descartar una de las dos.")
    return {
        "nivel": nivel, "estado_catalogo": estado_cat,
        "cobertura": f"{n} en catálogo · {g} verdes · {o} naranjas · {r} rojas",
        "fuentes": dict(fuentes), "fallos": fallos, "causas": causas or ["—"], "mejoras": mejoras or ["—"],
        "recomendaciones": reco or ["—"], "notas": notas[:700] + ("…" if len(notas) > 700 else ""),
        "plan": meta.get("url_plan_estudios"), "grado": meta.get("nombre_grado"),
    }


# destinos añadidos en la tanda 3 y titulaciones Uniovi nuevas (coordenadas aproximadas del centro urbano)
EXTRA_COORDS.update({
    "ec_b_leuven01": ("Lovaina", 50.88, 4.70), "ec_b_louvain01": ("Louvain-la-Neuve", 50.67, 4.61),
    "ec_b_mechele14": ("Malinas", 51.03, 4.48), "ec_cz_pardub01": ("Pardubice", 50.04, 15.77),
    "ec_d_bingen01": ("Bingen", 49.97, 7.90), "ec_d_bochum01": ("Bochum", 51.45, 7.26),
    "ec_d_deggend01": ("Deggendorf", 48.84, 12.96), "ec_d_karlsru01": ("Karlsruhe (KIT)", 49.01, 8.40),
    "ec_d_marburg01": ("Marburgo", 50.81, 8.77), "ec_dk_alborg01": ("Aalborg", 57.05, 9.92),
    "ec_f_le_havr11": ("Le Havre", 49.49, 0.11), "ec_f_poitier05": ("Poitiers", 46.58, 0.34),
    "ec_f_rouen07": ("Rouen", 49.44, 1.10), "ec_g_ioannin01": ("Ioánina", 39.67, 20.85),
    "ec_i_beneven02": ("Benevento", 41.13, 14.78), "ec_i_campoba01": ("Campobasso", 41.56, 14.66),
    "ec_i_modena01": ("Módena", 44.65, 10.93), "ec_i_napoli01": ("Nápoles", 40.85, 14.26),
    "ec_i_padova01": ("Padua", 45.41, 11.88), "ec_i_pavia01": ("Pavía", 45.19, 9.16),
    "ec_i_pisa01": ("Pisa", 43.72, 10.40), "ec_i_roma01": ("Roma", 41.90, 12.51),
    "ec_p_coimbra01": ("Coímbra", 40.21, -8.43), "ec_p_lisboa07": ("Lisboa", 38.75, -9.15),
    "ec_pl_bydgosz01": ("Bydgoszcz", 53.12, 18.01), "ec_pl_gdansk02": ("Gdansk", 54.37, 18.62),
    "ec_pl_gdynia01": ("Gdynia", 54.52, 18.54), "ec_pl_krakow02": ("Cracovia", 50.06, 19.92),
    "ec_ro_clujnap01": ("Cluj-Napoca", 46.77, 23.60), "ec_ro_oradea01": ("Oradea", 47.06, 21.93),
    "ec_s_linkopi01": ("Linköping", 58.40, 15.58), "ec_sf_espoo12": ("Espoo", 60.19, 24.83),
    "ec_si_ljublja01": ("Liubliana", 46.05, 14.50), "ec_sk_bratisl02": ("Bratislava", 48.15, 17.11),
    "ec_tr_istanbu07": ("Estambul", 41.05, 29.01), "ec_tr_mersin04": ("Mersin", 36.80, 34.64),
    "ec_uk_staffor02": ("Stafford", 52.81, -2.12),
    "ec_pl_gliwice01": ("Gliwice", 50.29, 18.67), "ec_sf_vaasa01": ("Vaasa", 63.10, 21.62),
    "ec_p_porto05": ("Oporto", 41.15, -8.61), "ec_p_maia01": ("Maia", 41.23, -8.62),
    "ec_p_vila_re01": ("Vila Real", 41.30, -7.74), "ec_tr_kocaeli02": ("Kocaeli", 40.77, 29.94),
    "ec_tr_elazig01": ("Elazığ", 38.67, 39.22), "ec_tr_samsun01": ("Samsun", 41.29, 36.33),
    "ec_f_angers01": ("Angers", 47.47, -0.55), "ec_f_marseil84": ("Marsella", 43.30, 5.37),
    "ec_b_antwerp01": ("Amberes", 51.22, 4.40), "ec_nl_ensched01": ("Enschede", 52.22, 6.89),
    "ec_d_rostock01": ("Rostock", 54.09, 12.10), "ec_i_palermo01": ("Palermo", 38.12, 13.36),
    "ec_i_catania01": ("Catania", 37.50, 15.09), "ec_g_komotin01": ("Komotini", 41.12, 25.41),
    "ec_bg_sofia20": ("Sofía", 42.70, 23.32),
    # Uniovi: telecomunicación e industrial en Gijón; informática en Oviedo
    "uniovi_dg_infdatos": ("Oviedo (Informática)", 43.355, -5.853), "uniovi_giiti": ("Oviedo (Informática)", 43.357, -5.851),
    "uniovi_gcid": ("Oviedo (Informática)", 43.353, -5.855), "uniovi_mm_inf": ("Oviedo (Informática)", 43.358, -5.857),
    "uniovi_dg_telecodatos": ("Gijón (Telecomunicación)", 43.522, -5.622), "uniovi_gitst": ("Gijón (Telecomunicación)", 43.524, -5.620),
    "uniovi_mm_teleco": ("Gijón (Telecomunicación)", 43.521, -5.618), "uniovi_mii": ("Gijón (EPI · Máster)", 43.527, -5.612),
    "uniovi_mm_automatizacion": ("Gijón (EPI · Máster)", 43.512, -5.610), "uniovi_mm_energetica": ("Gijón (EPI · Máster)", 43.510, -5.616),
    "uniovi_mm_energia_elec": ("Gijón (EPI · Máster)", 43.530, -5.608), "uniovi_mm_erasmus_mecatronica": ("Gijón (EPI · Máster)", 43.513, -5.622),
    "uniovi_mm_integridad": ("Gijón (EPI · Máster)", 43.528, -5.624), "uniovi_mm_mecatronica": ("Gijón (EPI · Máster)", 43.508, -5.612),
})


def _coords_extra_degrees() -> None:
    """Grados extra (convenio_extra): mismas coordenadas que el destino padre, con un pequeño desplazamiento."""
    base = {**be.COORDS, **EXTRA_COORDS}
    for i, u in enumerate(universities()):
        par = u.get("parent")
        if par and u["slug"] not in EXTRA_COORDS and par in base:
            v = base[par]
            city, lat, lon = (v[0], v[1], v[2]) if isinstance(v[0], str) else ("", v[0], v[1])
            n = sum(1 for k in EXTRA_COORDS if k.startswith(par + "__"))
            EXTRA_COORDS[u["slug"]] = (city, lat + 0.012 * (n + 1), lon + 0.012 * (n + 1))


_coords_extra_degrees()


def build() -> dict:
    coords = {**be.COORDS, **EXTRA_COORDS}
    unis = []
    for u in universities():
        slug = u["slug"]
        if slug in EXCLUIDAS:
            continue
        cat = load_catalog(slug)
        courses = []
        for a in (cat or {}).get("asignaturas", []):
            st, m, has_md, has_js = classify_course(slug, a)
            courses.append({"c": a.get("codigo_asignatura", ""), "n": a.get("nombre_asignatura", ""),
                            "e": a.get("creditos_ects"), "y": a.get("curso"), "s": st, "m": m,
                            "md": has_md, "js": has_js, "url": a.get("url_guia_docente")})
        n = len(courses)
        ok = sum(c["s"] == "ok" for c in courses)
        par = sum(c["s"] == "parcial" for c in courses)
        red = n - ok - par
        pct = round(100 * (ok + 0.5 * par) / n) if n else 0
        tot = {"n": n, "ok": ok, "par": par, "red": red}
        city = coords.get(slug)
        unis.append({"slug": slug, "name": u["name"], "country": u["country"],
                     "city": city[0] if city else "", "lat": city[1] if city else None, "lon": city[2] if city else None,
                     "grupos": u.get("grupos", []), **tot, "pct": pct,
                     "dx": diagnose(u, cat, tot, courses), "courses": courses})
    # la métrica global mide los destinos y universidades externas; los grados propios de Uniovi (lado origen) se muestran en el mapa pero no cuentan
    ext = [x for x in unis if "uniovi_epi" not in x["grupos"] and "convenio_extra" not in x["grupos"]]
    covered = [x for x in ext if x["pct"] > 0]
    cob = 100 * len(covered) / len(ext)
    prof = sum(x["pct"] for x in covered) / len(covered) if covered else 0
    return {"generated": time.strftime("%Y-%m-%d %H:%M"), "unis": unis,
            "global": {"total": len(ext), "covered": len(covered), "coverage": round(cob, 1),
                       "depth": round(prof, 1), "score": round(cob * prof / 100)},
            "sin_coordenadas": [x["slug"] for x in unis if x["lat"] is None]}


def inject(data: dict, html: str) -> str:
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return re.sub(r"const EXTRACTION = .*?;/\*EXT\*/", lambda _m: f"const EXTRACTION = {blob};/*EXT*/", html, count=1, flags=re.S)


def main() -> None:
    data = build()
    (OUT / "extraction.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    g = data["global"]
    print(f"Universidades: {g['total']} | con datos: {g['covered']} | cobertura {g['coverage']} % | profundidad {g['depth']} % | MÉTRICA {g['score']} %")
    if data["sin_coordenadas"]:
        print("¡sin coordenadas!", data["sin_coordenadas"])
    idx = OUT / "index.html"
    if idx.exists():
        idx.write_text(inject(data, idx.read_text(encoding="utf-8")), encoding="utf-8")
        print("Inyectado en", idx)


if __name__ == "__main__":
    main()
