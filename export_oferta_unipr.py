#!/usr/bin/env python3
"""Exporta todas las columnas (visibles y ocultas) del Excel UNIPR a JSON."""
import json
import re
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter

EXCEL_PATH = Path(__file__).resolve().parent / "Offerta Formativa 2025-2026 - per pubblicazione.xlsx"
JSON_PATH = Path(__file__).resolve().parent / "OfertaUNIPr.json"


def header_key(value: str, letter: str) -> str:
    if not value:
        return letter
    key = re.sub(r"\s+", " ", str(value).replace("\n", " ").strip())
    return key


def cell_value(value):
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def export_oferta() -> None:
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb["Insegnamenti e coperture"]

    columnas = []
    for col in range(1, ws.max_column + 1):
        letter = get_column_letter(col)
        nombre = ws.cell(1, col).value
        oculta = bool(ws.column_dimensions[letter].hidden) if letter in ws.column_dimensions else False
        key = header_key(nombre, letter)
        columnas.append({
            "letra": letter,
            "nombre": nombre,
            "clave": key,
            "oculta": oculta,
        })

    filas = []
    for row_idx in range(2, ws.max_row + 1):
        fila = {}
        tiene_datos = False
        for col_idx, meta in enumerate(columnas, start=1):
            value = cell_value(ws.cell(row_idx, col_idx).value)
            if value is not None and value != "":
                tiene_datos = True
            fila[meta["clave"]] = value
        if tiene_datos:
            filas.append(fila)

    payload = {
        "fuente": EXCEL_PATH.name,
        "hoja": ws.title,
        "total_columnas": len(columnas),
        "total_filas": len(filas),
        "columnas": columnas,
        "filas": filas,
    }

    with open(JSON_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    print(json.dumps({
        "salida": str(JSON_PATH),
        "columnas": len(columnas),
        "columnas_ocultas": sum(1 for c in columnas if c["oculta"]),
        "filas": len(filas),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    export_oferta()
