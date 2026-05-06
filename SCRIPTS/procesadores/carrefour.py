import re
from procesadores.factura import Factura

# Regex
fecha_hora_re = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}:\d{2})")
factura_id_re = re.compile(r"NRF:\s*([A-Z0-9]+)")
total_re = re.compile(r"TOTAL A PAGAR\s*:\s*([\d,]+)", re.IGNORECASE)

item_line_re = re.compile(r"^(.*?)\s+(\d{1,3},\d{2})$")

codigo_basura_re = re.compile(r"\s+[A-Z0-9]{3,6}$")


def extract_date_time(text):
    m = fecha_hora_re.search(text)
    if m: return m.group(1), m.group(2)
    return None, None

def datos(text):
    text = text.replace('\xa0', ' ')
    lines = [l.strip() for l in text.splitlines() if l.strip() != '']

    fecha, hora = extract_date_time(text)

    m_id = factura_id_re.search(text)
    factura_id = m_id.group(1) if m_id else None

    m_total = total_re.search(text)
    total_str = m_total.group(1) if m_total else "0,00"
    
    total_factura = float(total_str.replace(',', '.'))

    factura_obj = Factura(
        comercio="Carrefour", 
        factura_id=factura_id, 
        hora=hora, 
        fecha=fecha, 
        total=total_factura
    )

    start, end = None, None
    for i, l in enumerate(lines):
        if '*****************' in l:
            start = i + 1
        elif '=====' in l:
            if start is not None and end is None:
                end = i
                break

    if start is not None and end is not None:
        block = lines[start:end]
        
        for line in block:
            m = item_line_re.match(line)
            if m:
                raw_name = m.group(1)
                precio_str = m.group(2)
                nombre_limpio = codigo_basura_re.sub('', raw_name).strip()

                precio_float = float(precio_str.replace(',', '.'))

                factura_obj.agregar_articulo(
                    nombre_limpio, 
                    1.0, 
                    precio_float, 
                    precio_float, 
                    0.0
                )

    return factura_obj