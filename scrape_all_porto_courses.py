import re
import json
import sqlite3
import urllib.request
import urllib.error
import time
from pathlib import Path
from html.parser import HTMLParser

# Paths
WORKSPACE = Path("f:/000. Antigravity/700. ERASMUS")
INPUT_JSON = WORKSPACE / "OfertaFEUP_Ingegneria_Meccanica.json"
OUTPUT_JSON = WORKSPACE / "OfertaFEUP_Ingegneria_Meccanica_Details.json"
OUTPUT_DB = WORKSPACE / "OfertaFEUP_Ingegneria_Meccanica_Details.sqlite"

class PortoCourseHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections = {}
        self.current_header = None
        self.collecting = False
        self.collected_text = []
        self.tag_path = []
        
        # Meta info
        self.instance = ""
        self.in_h2 = False
        self.h2_text = []

    def handle_starttag(self, tag, attrs):
        self.tag_path.append(tag)
        attrs_dict = dict(attrs)
        
        if tag == "h3":
            # Save previous section
            if self.current_header:
                self.sections[self.current_header] = " ".join(self.collected_text).strip()
            self.current_header = None
            self.collecting = False
            self.collected_text = []
        elif tag == "h2":
            self.in_h2 = True
            self.h2_text = []

    def handle_endtag(self, tag):
        if self.tag_path:
            self.tag_path.pop()
        
        if tag == "h3":
            self.collecting = True
        elif tag == "h2":
            self.in_h2 = False
            raw_h2 = " ".join(self.h2_text).strip()
            if "instance" in raw_h2.lower() or "ocorrência" in raw_h2.lower():
                self.instance = raw_h2

    def handle_data(self, data):
        if self.in_h2:
            self.h2_text.append(data)
        elif not self.current_header and self.tag_path and self.tag_path[-1] == "h3":
            self.current_header = data.strip()
        elif self.collecting and self.current_header:
            self.collected_text.append(data)

def parse_porto_content(html_content):
    parser = PortoCourseHTMLParser()
    parser.feed(html_content)
    
    # Save the last section
    if parser.current_header:
        parser.sections[parser.current_header] = " ".join(parser.collected_text).strip()
        
    cleaned_sections = {}
    for k, v in parser.sections.items():
        v_clean = re.sub(r'\s+', ' ', v).strip()
        if k == "Observations" or k == "Observações":
            v_clean = re.split(r'jQuery\(document\)|document\.write', v_clean)[0].strip()
        cleaned_sections[k] = v_clean
        
    return {
        "instance": parser.instance,
        "sections": cleaned_sections
    }

def main():
    if not INPUT_JSON.exists():
        print(f"Error: {INPUT_JSON} no existe.")
        return
        
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        all_courses = json.load(f)
        
    # Filter only those that have a valid link
    valid_courses = [c for c in all_courses if c.get("link") and c.get("link").startswith("http")]
    total_courses = len(valid_courses)
    print(f"Iniciando descarga y parseo de {total_courses} cursos de Oporto...")
    
    parsed_results = []
    
    for idx, c in enumerate(valid_courses, 1):
        url = c['link']
        code = c['code']
        en_url = url.replace("/pt/", "/en/")
        print(f"[{idx}/{total_courses}] Descargando: {c['name']} (Código: {code})...")
        
        try:
            req = urllib.request.Request(
                en_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                html_bytes = response.read()
                
            html_content = html_bytes.decode('utf-8', errors='ignore')
            detail = parse_porto_content(html_content)
            
            merged_course = {
                "code": code,
                "abbreviation": c.get("abbreviation"),
                "name": c.get("name"),
                "credits": c.get("credits"),
                "link": c.get("link"),
                "instance": detail["instance"],
                "sections": detail["sections"]
            }
            parsed_results.append(merged_course)
            print(f"   -> OK (Secciones extraídas: {len(detail['sections'])})")
            
        except Exception as e:
            print(f"   -> ERROR al descargar/parsear {code}: {e}")
            
        time.sleep(0.5) # Politeness delay
        
    # Save to JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(parsed_results, f, ensure_ascii=False, indent=2)
    print(f"\nDatos totales guardados en JSON: {OUTPUT_JSON.name}")
    
    # Save to SQLite
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        code TEXT PRIMARY KEY,
        abbreviation TEXT,
        name TEXT,
        credits TEXT,
        link TEXT,
        instance TEXT,
        objectives TEXT,
        learning_outcomes TEXT,
        working_method TEXT,
        pre_requirements TEXT,
        program TEXT,
        mandatory_literature TEXT,
        complementary_bibliography TEXT,
        teaching_methods TEXT,
        evaluation_type TEXT,
        assessment_components TEXT,
        time_allocation TEXT,
        eligibility_for_exams TEXT,
        calculation_formula TEXT,
        observations TEXT
    )
    """)
    
    for c in parsed_results:
        sec = c["sections"]
        
        objectives = sec.get("Objectives") or sec.get("Objetivos", "")
        learning_outcomes = sec.get("Learning outcomes and competences") or sec.get("Resultados de aprendizagem e competências", "")
        working_method = sec.get("Working method") or sec.get("Método de trabalho", "")
        pre_requirements = sec.get("Pre-requirements (prior knowledge) and co-requirements (common knowledge)") or sec.get("Requisitos prévios (conhecimentos prévios) e co-requisitos (conhecimentos simultâneos)", "")
        program = sec.get("Program") or sec.get("Programa", "")
        mandatory_literature = sec.get("Mandatory literature") or sec.get("Bibliografia Obrigatória", "")
        complementary_bibliography = sec.get("Complementary Bibliography") or sec.get("Bibliografia Complementar", "")
        teaching_methods = sec.get("Teaching methods and learning activities") or sec.get("Métodos de ensino e atividades de aprendizagem", "")
        evaluation_type = sec.get("Evaluation Type") or sec.get("Tipo de avaliação", "")
        assessment_components = sec.get("Assessment Components") or sec.get("Componentes de Avaliação", "")
        time_allocation = sec.get("Amount of time allocated to each course unit") or sec.get("Tempo de trabalho estimado para a unidade curricular", "")
        eligibility_for_exams = sec.get("Eligibility for exams") or sec.get("Obtenção de frequência", "")
        calculation_formula = sec.get("Calculation formula of final grade") or sec.get("Fórmula de cálculo da classificação final", "")
        observations = sec.get("Observations") or sec.get("Observações", "")
        
        cursor.execute("""
        INSERT OR REPLACE INTO courses (
            code, abbreviation, name, credits, link, instance,
            objectives, learning_outcomes, working_method, pre_requirements,
            program, mandatory_literature, complementary_bibliography, teaching_methods,
            evaluation_type, assessment_components, time_allocation, eligibility_for_exams,
            calculation_formula, observations
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c["code"],
            c["abbreviation"],
            c["name"],
            c["credits"],
            c["link"],
            c["instance"],
            objectives,
            learning_outcomes,
            working_method,
            pre_requirements,
            program,
            mandatory_literature,
            complementary_bibliography,
            teaching_methods,
            evaluation_type,
            assessment_components,
            time_allocation,
            eligibility_for_exams,
            calculation_formula,
            observations
        ))
        
    conn.commit()
    conn.close()
    print(f"Datos totales guardados en SQLite: {OUTPUT_DB.name}")
    print("¡Proceso finalizado!")

if __name__ == "__main__":
    main()
