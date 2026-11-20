# es_miguel_hernandez_elche — notas de descubrimiento
- Título: Grado en Ingeniería Mecánica (UMH, Escuela Politécnica Superior de Elche; RUCT 2501621, RD 1393/2007). Curso 2026-27 (fichas validadas en 2026).
- Fuente: portal umh.es (plantillas JS que pintan una ficha desde un JSON). Endpoint descubierto con la red del navegador: `https://www.umh.es/get_dataJson.py?item={item}&frm=DEFAULT&lang=ES`, con `item=:tit_g_143_S1` (título) o `:asi_g_{codigo}_S1` (asignatura). La respuesta es `jsonArray["..."]={...}`: se parsea con `json.JSONDecoder().raw_decode` tras `={`. Los HTML `/contenido/Estudios/:asi_.../datos_es.html` están vacíos sin JS.
- robots.txt de www.umh.es: solo veta bots concretos (GPTBot, anthropic-ai...) y `*` no veta `/get_dataJson.py`; PoliteClient lo acepta.
- Catálogo: `_x_inv_asignatura_pertenece_a_estudio` del título (44 asignaturas con curso, semestre, tipo, ECTS). Básica 60 + obligatorias 150 + TFG 12 = RUCT; se ofertan 36 ECTS optativos (RUCT 18). Código = número de la asignatura (asi_g_NNNN).
- Ficha: campos `_x_*`: descripción, interés profesional, competencias generales/específicas, objetivos (= resultados de aprendizaje), unidades didácticas (solo títulos, sin detalle), metodología, evaluación (+ características de prueba y criterios de corrección), bibliografía básica/complementaria (HTML con enlaces), software. Los valores llevan prefijos `~$`, `~f`, `~>`.
- Se descartan todos los campos de profesorado (`*profesor*`, `*responsable*`, `*colaborador*`) y el cronograma.
- Trampas: no hay campo de requisitos previos en casi ninguna ficha (`prerequisites=false`); los contenidos son solo títulos de unidades; el nombre llega en MAYÚSCULAS (se pasa a «Capitalizado»).

## Fase 2
`scraper_es_miguel_hernandez_elche.py`: 44/44 Markdown. Comprobadas 6 muestras contra el JSON. Ausente casi siempre: prerrequisitos.
