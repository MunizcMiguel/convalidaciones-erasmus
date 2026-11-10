import re
import json
import sqlite3
import random
import sys
import os
import win32com.client
from pathlib import Path
import openpyxl

# Reconfigure stdout to use UTF-8
sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path("f:/000. Antigravity/700. ERASMUS")
EXCEL_PATH = WORKSPACE / "Course_catalogue_Faculty of Mechanical Engineering_2025-2026.xlsx"
WORD_DIR = WORKSPACE / "INGINERIE MECANICĂ - INGINERIE MECANICĂ"
OUTPUT_JSON = WORKSPACE / "OfertaUPT_Ingegneria_Meccanica_Samples.json"
OUTPUT_DB = WORKSPACE / "OfertaUPT_Ingegneria_Meccanica_Samples.sqlite"

def get_excel_courses():
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb['Bachelor 2025-2026 ']
    
    courses = []
    # Columns: 
    # Row 1 is header (1-indexed: E=5 is Course unit, F=6 is Code, G=7 is Year, H=8 is Semester, I=9 is ECTS, J=10 is Course hrs, K=11 is Sem, L=12 is Lab, M=13 is Proj, N=14 is Lang)
    for r in range(3, ws.max_row + 1):
        code = ws.cell(r, 6).value
        name_en = ws.cell(r, 5).value
        if code and str(code).startswith("L431"):
            # Clean name_en: often contains "(Analiza..." or similar. Let's extract English and Romanian parts if possible.
            # Usually "English Name (Romanian Name)"
            name_str = str(name_en)
            name_en_clean = name_str
            name_ro_clean = ""
            match = re.search(r'([^(]+)\s*\(([^)]+)\)', name_str)
            if match:
                name_en_clean = match.group(1).strip()
                name_ro_clean = match.group(2).strip()
                
            courses.append({
                "code": str(code).strip(),
                "name_en": name_en_clean,
                "name_ro": name_ro_clean,
                "credits": ws.cell(r, 9).value,
                "course_hours": ws.cell(r, 10).value,
                "seminar_hours": ws.cell(r, 11).value,
                "lab_hours": ws.cell(r, 12).value,
                "project_hours": ws.cell(r, 13).value,
                "language": ws.cell(r, 14).value
            })
    return courses

def find_word_file(course_code):
    # Suffix pattern: e.g. L431.25.01.F1 -> we want to match "01.F1" or "01.C7"
    # Suffix is the last two parts of the code
    parts = course_code.split('.')
    if len(parts) >= 2:
        suffix = f"{parts[-2]}.{parts[-1]}"
    else:
        suffix = course_code
        
    # Search recursively in WORD_DIR
    for path in WORD_DIR.rglob("*"):
        if path.is_file() and (path.suffix == ".doc" or path.suffix == ".docx"):
            # Check if suffix is in filename
            # Replace dots with optional characters or just search
            if suffix.lower() in path.name.lower() or suffix.replace('.', '').lower() in path.name.lower():
                return path
    return None

def extract_sections_from_text(text):
    sections = {
        "professor": "",
        "objectives": "",
        "program_lecture": "",
        "program_applications": "",
        "bibliography": "",
        "evaluation": ""
    }
    
    # 1. Extract Professor
    prof_match = re.search(r'2\.2\s+Titularul activităţilor de curs\s*\n*(.*?)(?=\n*\s*(?:2\.3|3\.))', text, re.DOTALL | re.IGNORECASE)
    if prof_match:
        sections["professor"] = re.sub(r'\s+', ' ', prof_match.group(1)).strip()
        
    # 2. Extract Objectives
    obj_match = re.search(r'7\.\s+Obiectivele disciplinei.*?\n(.*?)8\.\s+Conţinuturi', text, re.DOTALL | re.IGNORECASE)
    if obj_match:
        sections["objectives"] = obj_match.group(1).strip()
        
    # 3. Extract Lecture Program (8.1)
    lecture_match = re.search(r'8\.1\s+Curs.*?\n(.*?)8\.2\s+Activităţi aplicative', text, re.DOTALL | re.IGNORECASE)
    if lecture_match:
        sections["program_lecture"] = lecture_match.group(1).strip()
        
    # 4. Extract Applications Program (8.2)
    app_match = re.search(r'8\.2\s+Activităţi aplicative.*?\n(.*?)9\.\s+Evaluare', text, re.DOTALL | re.IGNORECASE)
    if app_match:
        sections["program_applications"] = app_match.group(1).strip()
        
    # 5. Extract Evaluation (9)
    eval_match = re.search(r'9\.\s+Evaluare\s*\n(.*)$', text, re.DOTALL | re.IGNORECASE)
    if eval_match:
        # Stop at signatures or end of document
        eval_text = eval_match.group(1).strip()
        signature_index = eval_text.find("Data completării")
        if signature_index != -1:
            eval_text = eval_text[:signature_index].strip()
        sections["evaluation"] = eval_text
        
    return sections

def main():
    print("Obteniendo asignaturas desde Excel...")
    excel_courses = get_excel_courses()
    print(f"Total asignaturas L431 en Excel: {len(excel_courses)}")
    
    # Select 10 random courses
    random.seed(98765)
    selected_courses = random.sample(excel_courses, min(10, len(excel_courses)))
    
    print("\n--- MUESTRA SELECCIONADA PARA PROCESAR ---")
    for idx, c in enumerate(selected_courses, 1):
        print(f"{idx}. {c['code']} - {c['name_en']}")
        
    # Initialize Word COM application
    print("\nInicializando Microsoft Word COM...")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    
    parsed_courses = []
    
    for idx, c in enumerate(selected_courses, 1):
        print(f"\n[{idx}/10] Buscando archivo de Word para {c['code']}...")
        file_path = find_word_file(c["code"])
        
        if not file_path:
            print(f"   -> ADVERTENCIA: No se encontró archivo de Word para el código {c['code']}. Intentando por nombre...")
            # Fallback by name: let's search if any file contains the Romanian name or part of it
            for path in WORD_DIR.rglob("*"):
                if path.is_file() and (path.suffix == ".doc" or path.suffix == ".docx"):
                    if c["name_ro"] and c["name_ro"].lower() in path.name.lower():
                        file_path = path
                        break
            
        if file_path:
            print(f"   -> Encontrado: {file_path.relative_to(WORKSPACE)}")
            try:
                doc = word.Documents.Open(str(file_path.resolve()))
                text = doc.Content.Text
                doc.Close()
                
                # Extract sections from text
                sections = extract_sections_from_text(text)
                
                c_details = {
                    "code": c["code"],
                    "name_en": c["name_en"],
                    "name_ro": c["name_ro"],
                    "credits": c["credits"],
                    "course_hours": c["course_hours"],
                    "seminar_hours": c["seminar_hours"],
                    "lab_hours": c["lab_hours"],
                    "project_hours": c["project_hours"],
                    "language": c["language"],
                    "professor": sections["professor"],
                    "sections": {
                        "Objectives": sections["objectives"],
                        "Lecture Program": sections["program_lecture"],
                        "Practical Program": sections["program_applications"],
                        "Evaluation": sections["evaluation"]
                    }
                }
                parsed_courses.append(c_details)
                print(f"   -> OK: Información extraída correctamente.")
            except Exception as e:
                print(f"   -> ERROR al procesar el archivo Word: {e}")
        else:
            print(f"   -> ERROR: No se pudo encontrar ningún archivo de Word para esta asignatura.")
            
    word.Quit()
    
    # Save to JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(parsed_courses, f, ensure_ascii=False, indent=2)
    print(f"\nDatos guardados en JSON: {OUTPUT_JSON.name}")
    
    # Save to SQLite
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        code TEXT PRIMARY KEY,
        name_en TEXT,
        name_ro TEXT,
        credits INTEGER,
        course_hours INTEGER,
        seminar_hours INTEGER,
        lab_hours INTEGER,
        project_hours INTEGER,
        language TEXT,
        professor TEXT,
        objectives TEXT,
        program_lecture TEXT,
        program_applications TEXT,
        evaluation TEXT
    )
    """)
    
    for c in parsed_courses:
        sec = c["sections"]
        cursor.execute("""
        INSERT OR REPLACE INTO courses (
            code, name_en, name_ro, credits, course_hours, seminar_hours, lab_hours, project_hours,
            language, professor, objectives, program_lecture, program_applications, evaluation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c["code"],
            c["name_en"],
            c["name_ro"],
            c["credits"],
            c["course_hours"],
            c["seminar_hours"],
            c["lab_hours"],
            c["project_hours"],
            c["language"],
            c["professor"],
            sec["Objectives"],
            sec["Lecture Program"],
            sec["Practical Program"],
            sec["Evaluation"]
        ))
        
    conn.commit()
    conn.close()
    print(f"Datos guardados en SQLite: {OUTPUT_DB.name}")
    print("Proceso de prueba finalizado.")

if __name__ == "__main__":
    main()
