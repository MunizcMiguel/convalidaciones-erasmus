import re
import json
import sqlite3
from pathlib import Path
from html.parser import HTMLParser

# Paths
WORKSPACE = Path("f:/000. Antigravity/700. ERASMUS")
INPUT_JSON = WORKSPACE / "OfertaFEUP_Ingegneria_Meccanica.json"
SAMPLES_DIR = Path("C:/Users/Usuario/.gemini/antigravity/brain/84d1e12c-cfc7-4341-a8db-02b3468e4a46/scratch/porto_samples")
OUTPUT_JSON = WORKSPACE / "OfertaFEUP_Ingegneria_Meccanica_Samples_Details.json"
OUTPUT_DB = WORKSPACE / "OfertaFEUP_Ingegneria_Meccanica_Samples_Details.sqlite"

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
            # If it looks like Instance (e.g. Instance: 2025/2026)
            if "instance" in raw_h2.lower() or "ocorrência" in raw_h2.lower():
                self.instance = raw_h2

    def handle_data(self, data):
        if self.in_h2:
            self.h2_text.append(data)
        elif not self.current_header and self.tag_path and self.tag_path[-1] == "h3":
            self.current_header = data.strip()
        elif self.collecting and self.current_header:
            self.collected_text.append(data)

def parse_porto_file(file_path):
    with open(file_path, "r", encoding="latin-1") as f:
        content = f.read()
        
    parser = PortoCourseHTMLParser()
    parser.feed(content)
    
    # Save the last section
    if parser.current_header:
        parser.sections[parser.current_header] = " ".join(parser.collected_text).strip()
        
    # Clean sections
    cleaned_sections = {}
    for k, v in parser.sections.items():
        # Clean whitespaces
        v_clean = re.sub(r'\s+', ' ', v).strip()
        # Filter out Javascript/boilerplate that might have been appended at the end of the last section
        if k == "Observations" or k == "Observações":
            v_clean = re.split(r'jQuery\(document\)|document\.write', v_clean)[0].strip()
        cleaned_sections[k] = v_clean
        
    return {
        "instance": parser.instance,
        "sections": cleaned_sections
    }

def main():
    print("Cargando catálogo base de Oporto...")
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        all_courses = json.load(f)
        
    courses_map = {c["code"]: c for c in all_courses}
    
    # List available HTML files
    html_files = list(SAMPLES_DIR.glob("*_en.html"))
    print(f"Archivos descargados para analizar: {len(html_files)}")
    
    parsed_samples = []
    
    for hf in html_files:
        code = hf.name.replace("_en.html", "")
        if code not in courses_map:
            print(f"Código {code} no encontrado en el mapa base.")
            continue
            
        base_info = courses_map[code]
        print(f"Analizando: {base_info['name']} ({code})...")
        
        detail = parse_porto_file(hf)
        
        merged_course = {
            "code": code,
            "abbreviation": base_info.get("abbreviation"),
            "name": base_info.get("name"),
            "credits": base_info.get("credits"),
            "link": base_info.get("link"),
            "instance": detail["instance"],
            "sections": detail["sections"]
        }
        parsed_samples.append(merged_course)
        
    # Save to JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(parsed_samples, f, ensure_ascii=False, indent=2)
    print(f"Muestras guardadas en JSON: {OUTPUT_JSON.name}")
    
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
    
    for c in parsed_samples:
        sec = c["sections"]
        
        # Get standard sections or alternative Portuguese names
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
    print(f"Muestras guardadas en SQLite: {OUTPUT_DB.name}")

if __name__ == "__main__":
    main()
