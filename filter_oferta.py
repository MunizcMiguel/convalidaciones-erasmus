import json
from pathlib import Path

# Paths
JSON_PATH = Path("f:/000. Antigravity/700. ERASMUS/OfertaUNIPr.json")
OUTPUT_PATH = Path("f:/000. Antigravity/700. ERASMUS/OfertaUNIPr_Ingegneria_Meccanica.json")

def filter_data():
    print("Cargando JSON original...")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("Filtrando filas por INGEGNERIA MECCANICA...")
    filas = data.get("filas", [])
    
    filtered_filas = [
        fila for fila in filas 
        if fila.get("Corso di Studio Degree course name") == "INGEGNERIA MECCANICA"
    ]
    
    print(f"Filas encontradas: {len(filtered_filas)} de {len(filas)}")
    
    new_data = {
        "fuente": data.get("fuente"),
        "hoja": data.get("hoja"),
        "total_columnas": data.get("total_columnas"),
        "total_filas": len(filtered_filas),
        "columnas": data.get("columnas"),
        "filas": filtered_filas
    }
    
    print("Guardando nuevo JSON filtrado...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    
    print("¡Hecho!")

if __name__ == "__main__":
    filter_data()
