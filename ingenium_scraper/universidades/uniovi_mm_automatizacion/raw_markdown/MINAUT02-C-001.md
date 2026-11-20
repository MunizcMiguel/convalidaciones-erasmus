---
{
 "course_code": "MINAUT02-C-001",
 "course_name": "Sistemas Tiempo Real",
 "institution_slug": "uniovi_mm_automatizacion",
 "source_url": "https://www.uniovi.es/estudia/masteres/ingenieriayarquitectura/automatizacion/-/fof/asignatura/MINAUT02-C-001",
 "source_language": "es",
 "ects_catalog": 3.0,
 "blocks_found": {
  "contents": true,
  "learning_outcomes": true,
  "assessment": true,
  "bibliography": true,
  "prerequisites": true
 },
 "fetched_at": "2026-11-20T05:18:31",
 "content_sha256": "ba7a2183a62e15a9ce62942c527ddfe1554c78a316fd9b25534d6318650d8d6c"
}
---

# Sistemas Tiempo Real

Guía docente 2026-2027 · Universidad de Oviedo · Máster Universitario en Ingeniería de Automatización e Informática Industrial · MINAUT02-C-001

## Datos de la asignatura

- **Curso:** Primero
- **Temporalidad:** Primer Semestre
- **Carácter:** Complementos de Formación
- **Créditos:** 3
- **Pertenece al itinerario Bilingüe:** No
- **Actividades:** Prácticas de Laboratorio (7 Horas); Clases Expositivas (15.5 Horas)

## Contextualización

Se trata de una asignatura perteneciente al módulo de Complementos de Formación, cuya finalidad es igualar conocimientos entre los matriculados al Máster. Todos los estudiantes deberán cursar más adelante la asignatura de Sistemas Avanzados de Tiempo Real y Empotrados, por lo que en esta se hace una adelanto de los conocimientos que se precisarán y una labor de igualación, dado que hay estudiantes provenientes de titulaciones de grado que han cursado una asignatura de contenidos relacionados.

1. Comprender los mecanismos de desarrollo de aplicaciones en tiempo real, y las plataformas hardware disponibles.
2. Proporcionar al alumno los conocimientos básicos sobre la programación de sistemas de control multitarea en tiempo real.
3. Determinar si un sistema compuesto con múltiples tareas y requisitos temporales es planificable.

## Requisitos

Para un correcto aprovechamiento de la asignatura es recomendable que el alumno tenga:

Conocimientos medios de programación de un lenguaje C.

Conocimientos básicos de arquitectura de computadores.

Conocimientos básicos de sistemas operativos.

Manejo de computadores en el nivel de usuario.

Además deben tener las competencias usuales que les permitan la búsqueda y manejo de información por Internet y una capacidad de expresión oral y escrita media que les permita participar en debates y mostrar sus puntos de vista así como escribir información técnica.

## Competencias y resultados del aprendizaje

Se trabajarán las competencias generales/transversales indicadas en la memoria de verificación para esta asignatura.

| Competencias |  |
| --- | --- |
| Básicas y generales | **CB7**: Que los estudiantes sepan aplicar los conocimientos adquiridos y su capacidad de resolución de problemas en entornos nuevos o poco conocidos dentro de contextos más amplios (o multidisciplinares) relacionados con su área de estudio <br> **CB10:** Que los estudiantes posean las habilidades de aprendizaje que les permitan continuar estudiando de un modo que habrá de ser en gran medida autodirigido o autónomo. |
| Transversales | **CG2**: Desarrollar el potencial de las tecnologías de la información y de las comunicaciones en la producción industrial. <br> **CG8**: Conocer las materias y tecnologías que les capaciten para el aprendizaje de nuevos métodos y tecnologías, así como que les dote de versatilidad suficiente para adaptarse a nuevas situaciones. <br> **CG10**: Utilizar los conocimientos adquiridos para mantener una actitud crítica y activa en la gestión de proyectos de automatización. |
| Específicas | **CE5**: Analizar, diseñar y construir aplicaciones informáticas industriales. <br> **CE6**: Utilizar de manera eficaz una aproximación sistemática al desarrollo de la lógica de control de procesos industriales, utilizando técnicas normalizadas para el análisis, diseño, implementación y documentación de la solución adoptada. |

Resultados de aprendizaje

Centrándonos en las competencias específicas :

**CE5: Analizar, diseñar y construir aplicaciones informáticas industriales.**

Esta competencia esta ligada directamente con **RA222: Conocer los principios básicos de robustez y usabilidad del software industria**l. Para alcanzar este resultado los contenidos teóricos hacen hincapié en los elementos diferenciadores del software industrial frente al de uso general. Para alcanzar verdaderamente las competencias el alumno realizará varias prácticas de laboratorio en las que se hará énfasis en el análisis y el debate de las posibles soluciuons. La metodología de enseñanza se orientará a la resolución de problemas

**CE6: Utilizar de manera eficaz una aproximación sistemática al desarrollo de la lógica de control de procesos industriales, utilizando técnicas normalizadas para el análisis, diseño, implementación y documentación de la solución adoptada.**

Esta competencia está ligada con los resultados de aprendizaje:

**RA221: Aplicar una metodología adecuada para el análisis y diseño de sistemas de tiempo real.**

**RA223: Implementar aplicaciones software industriales de complejidad media.**

Nuevamente la clave para alcanzar estos resultados la vía escogida es el desarrollo del prototipo en prácticas. Los alumnos deberán aplicar las metodologías estudiadas en clase en un caso práctico . A la para que avanza la teoría los estudiantes deben usar lo visto en clase para ir añadiendo complejidad a su proyecto usando las herramientas metodológicas adecuadas y con la verificación de hitos que les obliguen a seguir un desarrollo ordenado satisfaciendo unos niveles de calidad preestablecidos.

## Contenidos

**1.** **Desarrollo de software para sistemas de tiempo real y empotrados.**

Introducción. Esquema host-target. Soportes de ejecución: núcleos y sistemas operativos empotrado de tiempo real (QNX, Windows CE, Linux, ...). Generación de imágenes firmware (BSPs). Herramientas de programación para sistemas empotrados: Depuradores, emuladores, ensambladores, compiladores, compiladores cruzados, … Técnicas de depuración. Soporte que ofrecen los distintos lenguajes de programación para el desarrollo de aplicaciones empotradas.

**2.** **Programación de aplicaciones concurrentes.**

Creación de aplicaciones multihilio. Sincronización mediante acceso exclusivo y acceso a memoria compartida. Sincronización por paso de mensajes.

**3.** **Programación de aplicaciones con requisitos temporales.**

Manejo del reloj del sistema. Tareas periódicas, aperiódicas y esporádicas. Programación de retardos y *time-outs.*

**4.** **Estudio de la planificabilidad**

Planificadores basados en algoritmos RMA o EDF. Análisis temporal de las tareas para determinar el cumplimiento de plazos.

## Metodología y plan de trabajo

El desarrollo de la asignatura combina clases expositivas, resolución de problemas y prácticas de laboratorio con el objetivo de que el estudiante comprenda los fundamentos de los métodos estudiados y sea capaz de aplicarlos en contextos prácticos. La metodología utilizada está inspirada en enfoques de aprendizaje basados en la indagación (*Inquiry-Based Learning*), fomentando que el alumnado reflexione sobre el comportamiento de las técnicas estudiadas y desarrolle una actitud crítica ante las distintas soluciones posibles.

**Clases expositivas.**  
En las clases teóricas se introducen los conceptos y principios fundamentales de la materia. Aunque el formato es principalmente expositivo, se fomenta la participación del alumnado mediante preguntas y discusiones orientadas a analizar el funcionamiento, las limitaciones y el ámbito de aplicación de las técnicas presentadas.

**Prácticas de laboratorio.**  
Las prácticas de laboratorio permiten aplicar los conceptos estudiados mediante su implementación y experimentación en problemas representativos de la asignatura. Tras la entrega de cada práctica, se proporciona material que permite al estudiante revisar y contrastar su solución.

**Sesiones de evaluación.**  
Las sesiones de evaluación corresponden principalmente a la realización de las pruebas teóricas de la asignatura y a la entrega de los trabajos o prácticas previstos en las convocatorias oficiales.

| MODALIDADES |  | Horas | % | Horas Totales |
| --- | --- | --- | --- | --- |
| **Presencial** | Clases Expositivas | 13.5 | 54% | 25 |
|  | Práctica de aula / Seminarios / Talleres | 2 | 8% |  |
|  | Prácticas de laboratorio / campo / aula de informática / aula de idiomas | 7 | 28% |  |
|  | Prácticas clínicas hospitalarias | 0 | 0% |  |
|  | Tutorías grupales | 0 | 0% |  |
|  | Prácticas Externas | 0 | 0% |  |
|  | Sesiones de evaluación | 2.5 | 10% |  |
| **No presencial** | Trabajo en Grupo | 0 | 0% | 50 |
|  | Trabajo Individual | 49.5 | 100% |  |
|  | **Total** | 75 |  |  |

| Metodologías docentes (indicar Sí o No) |  |  |
| --- | --- | --- |
| Método Expositivo / Lección Magistral |  | Si |
| Resolución de Ejercicios y Problemas |  | Si |
| Estudio de Casos |  | NO |
| Aprendizaje Basado en Problemas |  | NO |
| Aprendizaje Orientado a Proyectos |  | NO |
| Aprendizaje Cooperativo |  | SI |
| Contrato de Aprendizaje |  | No |
| Otras (Indicar cuales) | … | … |

## Evaluación del aprendizaje

**Evaluación en la convocatoria ordinaria**

**Elementos evaluables**

La evaluación ordinaria consta de los siguientes elementos evaluables:

**Examen teórico (E1)**: Prueba escrita consistente en un conjunto de cuestiones teórico-prácticas similares a las propuestas a los estudiantes a lo largo del curso y discutidas en las prácticas de aula. Esta prueba podrá realizarse mediante una prueba voluntaria al finalizar las clases teóricas, si las restricciones del calendario académico lo permiten, o bien en las convocatorias oficiales de examen establecidas por el centro. Para aprobar la asignatura en la convocatoria ordinaria es obligatorio obtener una calificación de al menos 5 puntos sobre 10 en esta prueba.

**Trabajo de curso (T1)**: Proyecto práctico relacionado con los contenidos de la asignatura. El estudiante podrá elegir entre varios temas propuestos por el profesorado o proponer uno propio, que deberá ser previamente aprobado. El trabajo incluirá la implementación de una solución al problema planteado y la elaboración de un informe técnico. El trabajo será evaluado atendiendo tanto al funcionamiento de la solución implementada como a la calidad del informe técnico entregado, en el que se deberá describir la solución adoptada y analizar críticamente sus resultados. El trabajo deberá entregarse en las convocatorias oficiales de la asignatura. Para aprobar la asignatura en la convocatoria ordinaria es obligatorio obtener una calificación de al menos 4 puntos sobre 10 en este trabajo.

**Calificación**

Si se han alcanzado todos los mínimos establecidos, la nota final de la convocatoria se calcula como:

Nota = 0,3 · E1 + 0,7 · T1

En caso contrario, la calificación de la convocatoria será el mínimo entre la nota obtenida con la fórmula anterior y 4,0.

**Consideraciones**

La realización de la prueba voluntaria es opcional y no sustituye al examen programado en la convocatoria oficial.

El examen teórico podrá realizarse en las distintas fechas previstas para esta prueba a lo largo del curso académico (prueba voluntaria, si procede, y convocatorias oficiales). Cuando un estudiante realice esta prueba en más de una ocasión, la calificación considerada para el cálculo de la nota final será la máxima de las obtenidas.

Los estudiantes que hayan superado el mínimo exigido en un elemento evaluable y deseen repetirlo en una convocatoria posterior deberán comunicarlo previamente al profesorado para su organización.

En caso de duda por parte del profesorado sobre la autoría de alguna prueba evaluable o el uso de medios no autorizados, se podrá solicitar al estudiante su defensa presencial.

**Evaluación en las convocatorias extraordinarias**

La evaluación en las convocatorias extraordinarias utilizará los mismos elementos evaluables y criterios de calificación descritos para la convocatoria ordinaria.

Para aprobar la asignatura en estas convocatorias será necesario obtener al menos 5 puntos sobre 10 en el examen teórico (E1) y 4 puntos sobre 10 en el trabajo de curso (T1). Si se alcanzan estos mínimos, la nota final de la convocatoria se calculará como:

Nota = 0,3 · E1 + 0,7 · T1

En caso contrario, la calificación de la convocatoria será el mínimo entre la nota obtenida con la fórmula anterior y 4,0.

**Consideraciones**

El examen teórico podrá realizarse en las distintas fechas previstas para esta prueba a lo largo del curso académico. Cuando un estudiante realice esta prueba en más de una ocasión, la calificación considerada será la máxima de las obtenidas.

En caso de duda por parte del profesorado sobre la autoría de alguna prueba evaluable o el uso de medios no autorizados, se podrá solicitar al estudiante su defensa presencial.

**Evaluación diferenciada**

El sistema de evaluación diferenciada utilizará los mismos elementos evaluables y criterios de calificación descritos anteriormente. En el caso del trabajo de curso, el contenido podrá adaptarse para facilitar su realización en función de las circunstancias que justifiquen este tipo de evaluación.

## Bibliografía

Aula de teoría con computador y proyector.

Laboratorio de prácticas con 24 computadores.

Real-Time Systems and Programming Languages (Fourth Edition) Ada 2005, Real-Time Java and C/Real-Time POSIX. Fourth Edition

Alan Burns and Andy Wellings. April 2009

Addison Wesley Longmain

Real-Time Systems Design and Analysis Third Edition

Phillip A. Laplante

A JOHN WILEY & SONS, INC., PUBLICATION

Design and Implementation of Real Time Software for Control of Mechanical –Systems

D.M Auslander, J.R. Ridgely, J.D. Ringgenberg

Doing Hard Time. Developing Real-Time Systems with UML, Objects, Frameworks, and Patterns.

Autores: Douglass, B P.

Editorial: Addison Wesley: Año:1999.
