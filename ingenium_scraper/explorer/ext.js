
// ---------- Extraction State ----------
const EXTRACTION = null;/*EXT*/
(function(){
  const btn = $("#btnExt");
  if (!EXTRACTION) { btn.style.display = "none"; return; }
  const G = EXTRACTION.global, U = EXTRACTION.unis;
  btn.textContent = `Extraction State [${Math.round(G.coverage)}% (${Math.round(G.depth)}%)]`;
  const col = p => `hsl(${Math.round(p * 1.2)},75%,42%)`;
  const LV = {"EXITOSO":"#1a9b50","CASI COMPLETO":"#6aa31a","PARCIAL":"#e8890c","SIN DATOS":"#d33"};
  $("#extFormula").innerHTML = `<b>[${Math.round(G.coverage)} % (${Math.round(G.depth)} %)]</b> = [cobertura (profundidad)]. Cobertura: ${G.covered} de ${G.total} universidades con datos. Profundidad: extracción media de esas universidades. `
    + `Por universidad: (verdes + ½·naranjas) / asignaturas del catálogo. Datos del ${esc(EXTRACTION.generated)}.`;
  let emap = null, elayer = null, cur = null, filt = "all";
  function open() {
    $("#ext").hidden = false;
    if (!emap) {
      emap = L.map("extMap", { worldCopyJump: true }).setView([46, 10], 4);
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 12, attribution: "© OpenStreetMap" }).addTo(emap);
      elayer = L.layerGroup().addTo(emap);
      draw();
    }
    setTimeout(() => emap.invalidateSize(), 50);
  }
  function draw() {
    elayer.clearLayers();
    U.filter(u => u.lat != null).forEach(u => {
      const sz = 34, sel = cur && cur.slug === u.slug;
      const ic = L.divIcon({ className: "", iconSize: [sz, sz], iconAnchor: [sz / 2, sz / 2],
        html: `<div class="mk${sel ? " sel" : ""}" style="width:${sz}px;height:${sz}px;background:${col(u.pct)}">${u.pct}%</div>` });
      L.marker([u.lat, u.lon], { icon: ic, zIndexOffset: sel ? 1000 : 0 })
        .bindTooltip(`${esc(u.name)} · ${esc(u.city)}<br>${u.ok} verdes · ${u.par} naranjas · ${u.red} rojas de ${u.n}`)
        .on("click", () => pick(u)).addTo(elayer);
    });
  }
  function pick(u) { cur = u; filt = "all"; draw(); detail(); }
  const SL = {ok: "Guía extraída", parcial: "Parcial", sin_guia: "Sin guía"};
  function plain(u) {
    const d = u.dx, L2 = a => a.map(x => "  - " + x).join("\n");
    return `[${u.slug}] ${u.name} (${u.city}, ${u.country}) — ${u.pct} % extraído\nESTADO: ${d.nivel} (catálogo: ${d.estado_catalogo})\nCOBERTURA: ${d.cobertura}\nFALLOS:\n${L2(d.fallos)}\nCAUSA PROBABLE:\n${L2(d.causas)}\nCÓMO MEJORAR:\n${L2(d.mejoras)}\nRECOMENDACIONES:\n${L2(d.recomendaciones)}\nNOTAS: ${d.notas || "—"}\nPLAN: ${d.plan || "—"}`;
  }
  function detail() {
    const u = cur, d = u.dx, box = $("#extDetail");
    box.hidden = false;
    const li = a => `<ul>${a.map(x => `<li>${esc(x)}</li>`).join("")}</ul>`;
    const fu = Object.entries(d.fuentes).map(([k, v]) => `${k}: ${v}`).join(", ") || "—";
    const rows = u.courses.filter(c => filt === "all" || c.s === filt);
    const fb = (f, t) => `<button data-f="${f}" class="${filt === f ? "on" : ""}">${t}</button>`;
    box.innerHTML = `<div class="extH"><h3>${esc(u.name)}</h3><span class="sub">${esc(u.city)} · ${esc(u.country)} · ${esc(u.slug)}</span>
      <span class="simbadge" style="background:${col(u.pct)}">${u.pct} %</span></div>
      <div class="extBox"><button class="cp" id="extCopy">Copiar resumen</button>
        <span class="lvl" style="background:${LV[d.nivel] || "#667085"}">${esc(d.nivel)}</span> <b>Resumen del estado de extracción</b>
        <dl><dt>Estado</dt><dd>${esc(d.nivel)} · catálogo «${esc(d.estado_catalogo)}»</dd>
        <dt>Cobertura</dt><dd>${esc(d.cobertura)}</dd>
        <dt>Titulación</dt><dd>${esc(d.grado || "—")}${d.plan ? ` · <a href="${esc(d.plan)}" target="_blank" rel="noopener">plan</a>` : ""}</dd>
        <dt>Tipo de fuente</dt><dd>${esc(fu)}</dd>
        <dt>Fallos</dt><dd>${li(d.fallos)}</dd>
        <dt>Causa probable</dt><dd>${li(d.causas)}</dd>
        <dt>Cómo mejorarlo</dt><dd>${li(d.mejoras)}</dd>
        <dt>Recomendaciones</dt><dd>${li(d.recomendaciones)}</dd>
        <dt>Notas del extractor</dt><dd>${esc(d.notas || "—")}</dd></dl></div>
      <div class="cf">${fb("all", `Todas (${u.n})`)}${fb("ok", `Verdes (${u.ok})`)}${fb("parcial", `Naranjas (${u.par})`)}${fb("sin_guia", `Rojas (${u.red})`)}</div>
      <div>${rows.map(c => `<div class="cr ${c.s}"><div class="t"><b>${esc(c.n)}</b> <small>${esc(c.c)}${c.e ? " · " + c.e + " ECTS" : ""}${c.y ? " · curso " + c.y : ""}</small></div>
        <span class="s">${SL[c.s]}${c.m.length ? " — falta: " + esc(c.m.join(", ")) : ""}</span>${c.url ? `<a href="${esc(c.url)}" target="_blank" rel="noopener">guía</a>` : ""}</div>`).join("") || `<div class="empty">${u.n ? "Ninguna en este filtro." : "Esta universidad no tiene catálogo de asignaturas todavía."}</div>`}</div>`;
    box.querySelectorAll(".cf button").forEach(b => b.onclick = () => { filt = b.dataset.f; detail(); });
    $("#extCopy").onclick = e => { const t = plain(u); try { navigator.clipboard.writeText(t).then(() => e.target.textContent = "¡Copiado!", () => e.target.textContent = "No se pudo copiar"); } catch (_) { e.target.textContent = "No se pudo copiar"; } };
    setTimeout(() => emap.invalidateSize(), 50);
  }
  btn.onclick = open;
  $("#extClose").onclick = () => { $("#ext").hidden = true; };
  document.addEventListener("keydown", e => { if (e.key === "Escape") $("#ext").hidden = true; });
})();
