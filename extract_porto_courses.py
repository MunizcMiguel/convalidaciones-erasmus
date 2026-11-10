import re
import json
from pathlib import Path
from html.parser import HTMLParser

# Paths
WORKSPACE = Path("f:/000. Antigravity/700. ERASMUS")
HTML_FILE = Path("C:/Users/Usuario/.gemini/antigravity/brain/84d1e12c-cfc7-4341-a8db-02b3468e4a46/scratch/porto_courses_page.html")
OUTPUT_JSON = WORKSPACE / "OfertaFEUP_Ingegneria_Meccanica.json"

class SigarraDetailParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.courses = []
        self.current_course = None
        self.in_td = False
        self.td_count = 0
        self.current_href = None
        self.temp_text = []
        self.in_table = False
        self.in_tr = False
        self.is_header = False
        self.tag_path = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.tag_path.append((tag, attrs_dict))
        
        if tag == "table":
            if "dados" in attrs_dict.get("class", "") or "dadossz" in attrs_dict.get("class", ""):
                self.in_table = True
        elif tag == "tr" and self.in_table:
            self.in_tr = True
            self.td_count = 0
            self.current_course = {"code": "", "abbreviation": "", "name": "", "credits": "", "link": ""}
            self.is_header = False
        elif tag in ["td", "th"] and self.in_tr:
            self.in_td = True
            self.temp_text = []
            if tag == "th":
                self.is_header = True
        elif tag == "a" and self.in_td:
            href = attrs_dict.get("href", "")
            if "ficha_uc_view" in href or "ucurr_geral" in href:
                # Build absolute URL
                if href.startswith("/"):
                    self.current_href = "https://sigarra.up.pt" + href
                elif href.startswith("http"):
                    self.current_href = href
                else:
                    self.current_href = "https://sigarra.up.pt/feup/pt/" + href

    def handle_endtag(self, tag):
        if not self.tag_path:
            return
        opened_tag, attrs_dict = self.tag_path.pop()
        
        if tag == "table":
            self.in_table = False
        elif tag == "tr":
            self.in_tr = False
            # Check if this looks like a course row
            if self.current_course and self.current_course["code"] and self.current_course["name"] and not self.is_header:
                # Avoid duplicates
                if self.current_course["code"] not in [c["code"] for c in self.courses]:
                    self.courses.append(self.current_course)
            self.current_course = None
        elif tag in ["td", "th"] and self.in_tr:
            self.in_td = False
            text = " ".join(self.temp_text).strip()
            text = re.sub(r'\s+', ' ', text)
            
            if not self.is_header and self.current_course:
                if self.td_count == 0:
                    self.current_course["code"] = text
                elif self.td_count == 1:
                    self.current_course["abbreviation"] = text
                elif self.td_count == 2:
                    self.current_course["name"] = text
                    if self.current_href:
                        self.current_course["link"] = self.current_href
                        self.current_href = None
                elif self.td_count == 4 or (self.td_count == 3 and text.replace(',', '').replace('.', '').isdigit()):
                    if text:
                        self.current_course["credits"] = text
                        
            self.td_count += 1

    def handle_data(self, data):
        if self.in_td:
            self.temp_text.append(data)

def main():
    if not HTML_FILE.exists():
        print(f"Error: {HTML_FILE} no existe.")
        return
        
    with open(HTML_FILE, "r", encoding="latin-1") as f:
        content = f.read()
        
    parser = SigarraDetailParser()
    parser.feed(content)
    
    print(f"Se han extraído {len(parser.courses)} asignaturas únicas.")
    
    # Save to JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(parser.courses, f, ensure_ascii=False, indent=2)
        
    print(f"Archivo guardado correctamente en: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
