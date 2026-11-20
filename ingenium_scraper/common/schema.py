"""Esquemas de datos del proyecto (pydantic v2). Fuente única de verdad para
el catálogo (Fase 1) y para el JSON estructurado de cada asignatura (Fase 3)."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

# ----------------------------------------------------------------------------
# Fase 1 · catalogo_urls.json  ->  {"meta": CatalogMeta, "asignaturas": [CatalogEntry]}
# ----------------------------------------------------------------------------
SourceType = Literal["html", "pdf", "pdf_compartido", "api", "sin_guia"]


class CatalogEntry(BaseModel):
    universidad: str
    nombre_grado: str
    codigo_asignatura: str
    nombre_asignatura: str
    curso_semestre: str = Field(description="Texto libre original, p. ej. 'Curso 2 / Semestre 1'")
    curso: Optional[int] = Field(None, ge=1, le=6)
    semestre: Optional[int] = Field(None, ge=1, le=12, description="Semestre absoluto del plan (1..8)")
    creditos_ects: Optional[float] = Field(None, ge=0, le=60)
    caracter: Optional[str] = Field(None, description="obligatoria | optativa | tfg | practicas ...")
    idioma_pagina: str = Field(description="ISO 639-1 de la guía: es, en, de, sv...")
    url_guia_docente: Optional[str] = None
    tipo_fuente: SourceType = "html"
    paginas_pdf: Optional[str] = Field(None, description="Rango 'ini-fin' si la guía vive dentro de un PDF compartido")

    @field_validator("codigo_asignatura", "nombre_asignatura")
    @classmethod
    def _no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("vacío")
        return v.strip()


class CatalogMeta(BaseModel):
    universidad: str
    slug: str
    nombre_grado: str
    nivel: str = "bachelor"
    curso_academico: str
    url_plan_estudios: str
    ects_totales_plan: Optional[float] = None
    estrategia_fuente: str = Field(description="Cómo se obtiene el catálogo: API, HTML estático, PDF, SPA...")
    generado_por: str = Field(description="Nombre del script determinista que lo genera")
    generado_en: str
    estado: Literal["ok", "parcial", "n/a"] = "ok"
    notas: str = ""


class Catalog(BaseModel):
    meta: CatalogMeta
    asignaturas: list[CatalogEntry]


# ----------------------------------------------------------------------------
# Fase 3 · structured_data/{codigo}.json
# Lo que rellena el LLM (SyllabusExtraction) + lo que añade el código (SyllabusRecord)
# ----------------------------------------------------------------------------
class Assessment(BaseModel):
    method: str
    weight_percentage: Optional[float] = Field(None, description="null si la guía no da el peso")


class LearningOutcome(BaseModel):
    text: str
    type: Literal["knowledge", "skill", "competence", "unspecified"] = "unspecified"
    code: Optional[str] = Field(None, description="Código original de la competencia si existe (p. ej. CE12)")


class SyllabusExtraction(BaseModel):
    """Campos extraídos semánticamente. Todo en inglés salvo course_name_original."""
    course_name_original: str
    course_name_en: str
    ects: Optional[float]
    semester: Optional[str]
    year_of_study: Optional[int]
    course_type: Literal["compulsory", "elective", "thesis", "internship", "other", "unknown"]
    language_of_instruction: list[str] = Field(description="ISO 639-1")
    prerequisites: list[str]
    learning_outcomes: list[LearningOutcome]
    syllabus_topics: list[str]
    teaching_methods: list[str]
    workload_hours_total: Optional[float]
    workload_hours_contact: Optional[float]
    assessment_methods: list[Assessment]
    assessment_rules: Optional[str] = Field(None, description="Grading formula, minimum marks and resit rules as stated, in English")
    bibliography: list[str]
    isced_f_code: Optional[str] = Field(None, description="Código ISCED-F 2013 de 4 dígitos, p. ej. 0715")
    missing_sections: list[Literal["learning_outcomes", "syllabus_topics", "assessment_methods", "bibliography", "prerequisites"]] = Field(description="Bloques que la guía NO contiene (no inventar)")


class SyllabusRecord(SyllabusExtraction):
    """Registro final = extracción + trazabilidad añadida de forma determinista."""
    institution: str
    institution_slug: str
    degree: str
    course_code: str
    academic_year: str
    source_url: Optional[str]
    source_language: str
    source_sha256: str
    extracted_at: str
    extractor_model: str
    schema_version: str = "1.1"
