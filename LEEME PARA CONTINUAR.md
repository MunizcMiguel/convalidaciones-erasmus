# 📚 LEEME PARA CONTINUAR — Proyecto ERASMUS Convalidaciones
> Última actualización: Octubre de 2026  
> Contexto IA: Conversación `84d1e12c-cfc7-4341-a8db-02b3468e4a46`

---

## 🗂️ Estado Actual del Proyecto

El proyecto dispone de un **sistema integral de convalidaciones y orientación para la movilidad internacional** de los estudiantes de la Escuela Politécnica de Ingeniería de Gijón (UNIOVI), con soporte multi-titulación:

### 1. Grado en Ingeniería Mecánica (GIMECA - UNIOVI)
| Universidad | País | Oferta Docente | Catálogo Extraído | Tasa de Convalidación |
|---|---|---|---|---|
| **Technische Hochschule Ingolstadt (THI)** | 🇩🇪 Alemania | B.Eng. Maschinenbau + FWPM Electives | 71 módulos oficiales (Modulhandbuch) | **40 / 44 (90.9%)** |
| **Università di Parma (UNIPr)** | 🇮🇹 Italia | Laurea / Magistrale in Ingegneria Meccanica | 96 asignaturas (detalles y temarios) | **38 / 44 (86.4%)** |
| **Universitatea Politehnica Timișoara (UPT)** | 🇷🇴 Rumanía | Inginerie Mecanică (Catálogo Erasmus) | 70 asignaturas (detalles y temarios) | **32 / 44 (72.7%)** |
| **Universidade do Porto (FEUP)** | 🇵🇹 Portugal | Licenciatura em Engenharia Mecânica | 47 asignaturas (detalles y temarios) | **25 / 44 (56.8%)** |

### 2. Grado en Ingeniería en Organización Industrial (GIOI - UNIOVI)
| Universidad | País | Oferta Docente | Catálogo Extraído | Tasa de Convalidación |
|---|---|---|---|---|
| **Universidade do Porto (FEUP)** | 🇵🇹 Portugal | Licenciatura (L.EGI) + Mestrado (M.EGI) em Engenharia e Gestão Industrial | 35 asignaturas (L.EGI / M.EGI) | **33 / 35 (94.3%)** |

---

## 🌐 Entregable Principal: Aplicación Web Interactiva Multi-Titulación

El núcleo del proyecto es la aplicación web desarrollada para estudiantes y coordinadores:
👉 **[`convalidaciones_web.html`](file:///f:/000.%20Antigravity/700.%20ERASMUS/convalidaciones_web.html)**

### Funcionalidades implementadas:
1. **Selector de Titulación Dinámico (Degree Switcher):**
   - Conmutador en cabecera: `⚙️ Mecánica (GIMECA)` vs `🏢 Organización Industrial (GIOI)`.
   - Adapta en tiempo real la matriz de convalidaciones, el resumen de KPIs, el buscador, la vista en tarjetas, el modal de temarios comparados y el simulador de acuerdo lectivo.
2. **Matriz de Convalidaciones Global:**
   - **Para GIMECA:** 44 asignaturas de 2º, 3º y 4º curso frente a Parma, Porto, Timișoara y TH Ingolstadt (25 columnas).
   - **Para GIOI:** 35 asignaturas de 2º, 3º y 4º curso frente a Porto (FEUP - L.EGI y M.EGI) (10 columnas: asignaturas, ciclos, cursos, semestres, créditos y códigos oficiales).
   - Distintivo visual inmediato: ⭐ **Validada previamente en convenios**, 🔬 **Nueva propuesta técnica (>75% temario)**, ❌ **Sin convalidación directa**.
3. **Comparador Interactivo de Temarios Lado a Lado (Syllabus Matcher):**
   - Al pulsar en cualquier asignatura se despliega un panel comparativo a doble columna.
   - Izquierda: Guía docente UNIOVI oficial (competencias, contenidos capítulo por capítulo, criterios de evaluación).
   - Derecha: Asignatura de destino seleccionada (objetivos formativos, programa lectivo oficial, métodos de examen).
   - **Dictamen técnico del coordinador**: Justificación técnica detallada de por qué se valida y qué particularidades tiene.
4. **Simulador de Acuerdo de Aprendizaje (Learning Agreement Builder):**
   - Permite al estudiante seleccionar titulación, destino y curso/semestre, marcar las asignaturas deseadas y calcular en tiempo real el balance de créditos (controlando el objetivo de 30 ECTS/semestre o 60 ECTS/año) con alertas de sobrecarga o déficit de créditos.
5. **Acceso Verificado a Fuentes Oficiales:**
   - Enlace directo a la guía docente en la web de UNIOVI.
   - Enlace directo a la ficha de Unidade Curricular en SIGARRA de FEUP (L.EGI / M.EGI / Mecánica).
   - Enlaces a Parma, UPT y THI.

---

## 📁 Archivos Disponibles en la Carpeta del Proyecto

### 📊 Datos y Aplicación (`f:/000. Antigravity/700. ERASMUS/`)
* **`convalidaciones_web.html`** — Portal web interactivo completo con conmutador GIMECA / GIOI.
* **`convalidaciones_data.js`** — Base de datos consolidada en JS (`window.CONVALIDACIONES_DATA_GIMECA` y `window.CONVALIDACIONES_DATA_GIOI`) para ejecución local inmediata sin CORS ni servidor web.
* **`gioi_porto_convalidaciones.json`** — Base de datos unificada con las 35 asignaturas de GIOI y sus correspondencias con FEUP EGI.
* **`gioi_plan_estudios.json`** y **`gioi_guias_docentes.json`** — Guías docentes oficiales extraídas de UNIOVI para GIOI.
* **`Tabla_Convalidaciones_GIOI_Oporto.xlsx`** — Hoja Excel maestra de convalidaciones GIOI ↔ Porto (FEUP).
* **`Tabla_Convalidaciones_ERASMUS.xlsx`** — Hoja Excel maestra de convalidaciones GIMECA (5 universidades).
* `uniovi_guias.sqlite` — Base de datos SQLite unificada con las 53 guías de GIMECA y 35 guías de GIOI.

### 🐍 Scripts en Scratch (`.../scratch/`)
* **`extraer_gioi_plan.py`** — Extractor del plan de estudios de GIOI desde UNIOVI.
* **`extract_all_gioi_official.py`** — Extractor oficial de guías docentes completas (portlet SIES) de GIOI.
* **`build_gioi_porto_dataset.py`** — Mapeador experto de convalidaciones GIOI ↔ Porto, generador de JSON y Excel.
* **`update_web_with_gioi.py`** — Actualizador del frontend web interactivo con soporte multi-titulación.

---

## 📋 Resumen Estadístico de Convalidaciones Auditadas

### GIOI (Grado en Organización Industrial) ↔ Porto (FEUP):
* Total asignaturas analizadas: **35 asignaturas** (2º, 3º y 4º curso).
* Convalidables: **33 / 35 (94.3%)**.
* No convalidables: **2 asignaturas** (Cooperación Tecnológica y Técnicas de Expresión en Inglés).
* Convalidaciones probadas previamente: **12 asignaturas** con notas medias registradas (media 8.6/10).
* Ciclos de destino en FEUP: **L.EGI** (Licenciatura, 1º ciclo) para 2º y 3º año; **M.EGI** (Mestrado, 2º ciclo) para materias avanzadas de 4º año (Supply Chain, Calidad, Gestión de Procesos, Minería de Datos, Dirección de Proyectos).

---

## 🚀 Próximas Fases Recomendadas

1. **Ampliación de GIOI a los demás destinos:**
   - Cruzar el catálogo de GIOI con THI (Wirtschaftsingenieurwesen), Parma (Ingegneria Gestionale) y UPT (Inginerie Economică).
2. **Actualización Anual Automática:**
   - Ejecutar el pipeline al inicio de cada curso académico (septiembre/octubre) para alertar de posibles modificaciones en los planes de estudio socios.
