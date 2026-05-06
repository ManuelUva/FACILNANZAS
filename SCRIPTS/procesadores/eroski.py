import re
from procesadores.factura import Factura

# Extracción de fecha
fecha_hora_re = re.compile(r"C:\s*\d+\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}:\d{2})")
fecha_hora_alt_re = re.compile(r"EGUNA/FECHA:\s*(\d{2}-\d{2}-\d{4})\s*(\d{2}:\d{2})")
fecha_hora_fallback_re = re.compile(r"(\d{2}-\d{2}-\d{4})\s+(\d{2}:\d{2})")

# Demás datos
trailing_prices_re = re.compile(r'(-?\d{1,3},\d{2})(?:\s+(-?\d{1,3},\d{2}))?\s*$')
total_re = re.compile(r"TOTAL A PAGAR\s+(-?\d{1,3},\d{2})")
factura_id_re = re.compile(r"\b(\d{18})\b")

def comma_to_float(s):
    if not s:
        return 0.0
    return float(s.replace('.', '').replace(',', '.'))

def extract_date_time(text):
    for regex in (fecha_hora_re, fecha_hora_alt_re, fecha_hora_fallback_re):
        m = regex.search(text)
        if m: 
            return m.group(1), m.group(2)
    return None, None

def datos(text, blacklist_words):
    text = text.replace('\xa0', ' ')
    lines = [re.sub(r'[ \t]+', ' ', l).rstrip() for l in text.splitlines() if l.strip() != '']

    fecha, hora = extract_date_time(text)

    m_id = factura_id_re.search(text)
    factura_id = m_id.group(1) if m_id else None

    start, end = None, None
    socio_idx = None
    for i, l in enumerate(lines):
        if 'SOCIO' in l.upper():
            socio_idx = i
            break
            
    if socio_idx is not None:
        for i in range(socio_idx + 1, len(lines)):
            if re.fullmatch(r'-{4,}', lines[i]):
                start = i + 1
                break
        if start is not None:
            for j in range(start, len(lines)):
                if re.fullmatch(r'-{4,}', lines[j]):
                    end = j
                    break
                    
    block = lines[start:end] if (start and end) else lines

    m = total_re.search(text)
    total_factura = comma_to_float(m.group(1)) if m else None

    factura_obj = Factura(comercio="Eroski", factura_id=factura_id, hora=hora, fecha=fecha, total=total_factura)
    
    for line in block:
        m = trailing_prices_re.search(line)
        if not m:
            continue
            
        price1 = m.group(1)  # precio unitario (o total si viene solo)
        price2 = m.group(2)  # precio total o descuento (si existe)
        
        line_without_prices = line[:m.start()]

        qmatch = re.match(r'^\s*(\d+)\s+', line_without_prices)
        qty = int(qmatch.group(1)) if qmatch else 1

        name = re.sub(r'^\s*\d+\s+', '', line_without_prices).strip()
        
        if any(b in name.upper() for b in blacklist_words):
            continue

        try:
            f1 = comma_to_float(price1)
            f2 = comma_to_float(price2) if price2 else None
        except ValueError:
            continue

        descuento = 0.0
        precio_ud = f1
        precio_total = f1

        if f2 is not None:
            if f2 < f1:
                descuento = f2
            else:
                precio_total = f2

        factura_obj.agregar_articulo(
            name, 
            float(qty), 
            float(precio_ud), 
            float(precio_total), 
            float(descuento)
        )

    return factura_obj