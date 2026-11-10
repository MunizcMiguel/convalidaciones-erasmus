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
INPUT_JSON = WORKSPACE / "OfertaUNIPr_Ingegneria_Meccanica.json"
OUTPUT_JSON = WORKSPACE / "OfertaUNIPr_Ingegneria_Meccanica_Details.json"
OUTPUT_DB = WORKSPACE / "OfertaUNIPr_Ingegneria_Meccanica_Details.sqlite"

class CourseHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = {
            "title": "",
            "code": "",
            "academic_year": "",
            "semester_info": "",
            "professor": "",
            "professor_link": "",
            "discipline": "",
            "field": "",
            "activity_type": "",
            "hours": "",
            "credits": "",
            "hub": "",
            "language": "",
            "sections": {}
        }
        
        self.state_stack = []
        self.temp_text = []
        self.in_dl = False
        self.current_dt = None
        self.in_section = False
        self.current_section_title = None
        self.tag_path = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.tag_path.append((tag, attrs_dict))
        
        # Title and Code
        if tag == "h1" and "page-header-title" in attrs_dict.get("class", ""):
            self.state_stack.append("title")
            self.temp_text = []
        elif tag == "span" and "title" in self.state_stack and "font-weight-semibold" in attrs_dict.get("class", ""):
            self.data["title"] = " ".join(self.temp_text).strip()
            self.state_stack.append("code")
            self.temp_text = []
            
        # Academic year and semester details
        elif tag == "div" and "page-header-subtitle" in attrs_dict.get("class", ""):
            self.state_stack.append("subtitle")
            self.temp_text = []
            
        # Professor, discipline info in DL list
        elif tag == "dl" and "dl--insegnamento" in attrs_dict.get("class", ""):
            self.in_dl = True
        elif self.in_dl and tag == "dt":
            self.state_stack.append("dt")
            self.temp_text = []
        elif self.in_dl and tag == "dd":
            self.state_stack.append("dd")
            self.temp_text = []
        elif self.in_dl and tag == "a" and "dd" in self.state_stack:
            if "href" in attrs_dict:
                self.data["professor_link"] = attrs_dict["href"]
                
        # Attributes like Hours, Credits, Sede/Hub, Language
        elif tag == "div" and "xx-small" in attrs_dict.get("class", ""):
            self.state_stack.append("icon_text")
            self.temp_text = []
            
        # Course detail sections
        elif tag == "article" and "it-page-section" in attrs_dict.get("class", ""):
            self.in_section = True
        elif self.in_section and tag == "h2" and "page-section-title" in attrs_dict.get("class", ""):
            self.state_stack.append("section_title")
            self.temp_text = []
        elif self.in_section and tag == "p":
            self.state_stack.append("section_p")
            self.temp_text = []

    def handle_endtag(self, tag):
        if not self.tag_path:
            return
        
        opened_tag, attrs_dict = self.tag_path.pop()
        text_content = " ".join(self.temp_text).strip()
        text_content = re.sub(r'\s+', ' ', text_content)
        
        if self.state_stack:
            current_state = self.state_stack[-1]
            
            if current_state == "title" and tag == "h1":
                if not self.data["title"]:
                    self.data["title"] = text_content
                self.state_stack.pop()
            elif current_state == "code" and tag == "span":
                match = re.search(r'cod\.\s*(\w+)', text_content, re.IGNORECASE)
                self.data["code"] = match.group(1) if match else text_content
                self.state_stack.pop()
                if self.state_stack and self.state_stack[-1] == "title":
                    self.state_stack.pop()
            elif current_state == "subtitle" and tag == "div":
                parts = [p.strip() for p in text_content.split(" - ") if p.strip()]
                self.data["academic_year"] = parts[0] if len(parts) > 0 else text_content
                self.data["semester_info"] = parts[1] if len(parts) > 1 else ""
                self.state_stack.pop()
            elif current_state == "dt" and tag == "dt":
                self.current_dt = text_content.lower()
                self.state_stack.pop()
            elif current_state == "dd" and tag == "dd":
                if self.current_dt:
                    if "professor" in self.current_dt:
                        self.data["professor"] = text_content
                    elif "discipline" in self.current_dt:
                        self.data["discipline"] = text_content
                    elif "field" in self.current_dt:
                        self.data["field"] = text_content
                    elif "type of" in self.current_dt:
                        self.data["activity_type"] = text_content
                self.state_stack.pop()
            elif current_state == "icon_text" and tag == "div":
                if "hours" in text_content.lower():
                    self.data["hours"] = text_content
                elif "credits" in text_content.lower():
                    self.data["credits"] = text_content
                elif "hub" in text_content.lower():
                    self.data["hub"] = text_content
                elif "course unit in" in text_content.lower():
                    self.data["language"] = text_content
                self.state_stack.pop()
            elif current_state == "section_title" and tag == "h2":
                self.current_section_title = text_content
                self.state_stack.pop()
            elif current_state == "section_p" and tag == "p":
                if self.current_section_title:
                    self.data["sections"][self.current_section_title] = text_content
                self.state_stack.pop()
                
        if tag == "dl":
            self.in_dl = False
        elif tag == "article":
            self.in_section = False
            self.current_section_title = None

    def handle_data(self, data):
        if self.state_stack:
            self.temp_text.append(data)

def parse_html_string(html_content):
    parser = CourseHTMLParser()
    parser.feed(html_content)
    
    title = parser.data["title"]
    title = re.sub(r'\s+', ' ', title)
    title = title.replace("<br />", "").replace("<br>", "").strip()
    parser.data["title"] = title
    
    return parser.data

def run_mass_scraper():
    if not INPUT_JSON.exists():
        print(f"Error: {INPUT_JSON} no existe.")
        return
        
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    filas = data.get("filas", [])
    valid_courses = []
    for fila in filas:
        cid = fila.get("Id. Insegnamento")
        cname = fila.get("Nome Insegnamento Component title (original)")
        if cid:
            valid_courses.append((cid, cname))
            
    # Keep order but unique IDs
    unique_list = []
    seen = set()
    for cid, cname in valid_courses:
        if cid not in seen:
            seen.add(cid)
            unique_list.append((cid, cname))
            
    total_courses = len(unique_list)
    print(f"Comenzando raspado masivo de {total_courses} cursos de ingeniería mecánica...")
    
    parsed_results = []
    
    for idx, (cid, cname) in enumerate(unique_list, start=1):
        url = f"https://corsi.unipr.it/en/ugov/degreecourse/{cid}"
        print(f"[{idx}/{total_courses}] Descargando: {cname} (ID: {cid})...")
        
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                html_bytes = response.read()
                
            html_content = html_bytes.decode('utf-8', errors='ignore')
            parsed = parse_html_string(html_content)
            parsed["id"] = cid
            # Keep original spreadsheet names for cross-referencing
            parsed["original_name"] = cname
            parsed_results.append(parsed)
            print(f"   -> OK: {parsed['title']} ({parsed['code']})")
        except Exception as e:
            print(f"   -> ERROR al descargar/parsear {cid}: {e}")
            
        time.sleep(0.5) # Safe politeness delay to avoid rate limiting
        
    # Save to JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(parsed_results, f, ensure_ascii=False, indent=2)
    print(f"\nDatos totales guardados en JSON: {OUTPUT_JSON.name}")
    
    # Save to SQLite
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        code TEXT,
        title TEXT,
        original_name TEXT,
        academic_year TEXT,
        semester_info TEXT,
        professor TEXT,
        professor_link TEXT,
        discipline TEXT,
        field TEXT,
        activity_type TEXT,
        hours TEXT,
        credits TEXT,
        hub TEXT,
        language TEXT,
        learning_objectives TEXT,
        prerequisites TEXT,
        course_content TEXT,
        full_programme TEXT,
        bibliography TEXT,
        teaching_methods TEXT,
        assessment_methods TEXT,
        other_information TEXT,
        agenda_2030_goals TEXT
    )
    """)
    
    for course in parsed_results:
        sections = course.get("sections", {})
        cursor.execute("""
        INSERT OR REPLACE INTO courses (
            id, code, title, original_name, academic_year, semester_info, professor, professor_link,
            discipline, field, activity_type, hours, credits, hub, language,
            learning_objectives, prerequisites, course_content, full_programme,
            bibliography, teaching_methods, assessment_methods, other_information,
            agenda_2030_goals
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course.get("id"),
            course.get("code"),
            course.get("title"),
            course.get("original_name"),
            course.get("academic_year"),
            course.get("semester_info"),
            course.get("professor"),
            course.get("professor_link"),
            course.get("discipline"),
            course.get("field"),
            course.get("activity_type"),
            course.get("hours"),
            course.get("credits"),
            course.get("hub"),
            course.get("language"),
            sections.get("Learning objectives"),
            sections.get("Prerequisites"),
            sections.get("Course unit content"),
            sections.get("Full programme"),
            sections.get("Bibliography"),
            sections.get("Teaching methods"),
            sections.get("Assessment methods and criteria"),
            sections.get("Other information"),
            sections.get("2030 agenda goals for sustainable development")
        ))
        
    conn.commit()
    conn.close()
    print(f"Datos totales guardados en SQLite: {OUTPUT_DB.name}")
    print("¡Proceso finalizado!")

if __name__ == "__main__":
    run_mass_scraper()
