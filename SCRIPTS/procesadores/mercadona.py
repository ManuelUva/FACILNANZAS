import re
from procesadores.factura import Factura

fecha_hora_re = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})")
factura_id_re = re.compile(r"FACTURA SIMPLIFICADA:\s*([\d\-]+)", re.IGNORECASE)
total_re = re.compile(r"TOTAL\s*\(\€\)\s*([\d,.]+)", re.IGNORECASE)

item_line_re = re.compile(r"^(\d+)\s+(.*?)\s+([\d,.]+)$")

kg_line_re = re.compile(r"^([\d,.]+)\s*kg\s+([\d,.]+)\s*(?:€/kg|E/kg|/kg)\s+([\d,.]+)$", re.IGNORECASE)

def extract_date_time(text):
    m = fecha_hora_re.search(text)
    if m: 
        hora_formateada = m.group(2)
        return m.group(1), hora_formateada
    return None, None

def comma_to_float(s):
    s = str(s).strip()
    if not s:
        return 0.0
    if '.' in s and ',' in s:
        s = s.replace('.', '')
    s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return 0.0

def datos(text, comercio="MERCADONA"):
    text = text.replace('\xa0', ' ')
    lines = [l.strip() for l in text.splitlines() if l.strip() != '']

    fecha, hora = extract_date_time(text)

    m_id = factura_id_re.search(text)
    factura_id = m_id.group(1) if m_id else None

    total = None
    end = None

    for i, l in enumerate(lines):
        m_total = total_re.search(l)
        if m_total:
            total = m_total.group(1)
            end = i
            break

    factura_obj = Factura(comercio=comercio, factura_id=factura_id, hora=hora, fecha=fecha, total=float(comma_to_float(total)))

    if end is not None:
        block = lines[:end]
        
        for i, line in enumerate(block):
            m = item_line_re.match(line)
            if m:
                qty = str(m.group(1))
                nombre = m.group(2).strip()
                precio_total = m.group(3)
                
                factura_obj.agregar_articulo(
                    str(nombre), 
                    float(comma_to_float(qty)), 
                    float(comma_to_float(precio_total)), 
                    float(comma_to_float(precio_total)), 
                    0.0
                )
                continue 

            m_kg = kg_line_re.match(line)
            if m_kg and i > 0:
                qty = str(m_kg.group(1))
                precio_kg = m_kg.group(2)
                precio_total = m_kg.group(3)
  
                nombre = block[i-1].strip()

                factura_obj.agregar_articulo(
                    str(nombre), 
                    float(comma_to_float(qty)), 
                    float(comma_to_float(precio_total)),
                    float(comma_to_float(precio_total)), 
                    0.0
                )

    return factura_obj