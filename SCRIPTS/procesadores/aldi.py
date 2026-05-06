import re
from procesadores.factura import Factura

fecha_hora_re = re.compile(r"Fecha:\s*(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}:\d{2})", re.IGNORECASE)
factura_id_re = re.compile(r"Número:\s*([A-Z0-9]+)", re.IGNORECASE)
total_re = re.compile(r"A PAGAR\s+([\d,]+)\s*€", re.IGNORECASE)
item_line_re = re.compile(r"^(.*?)\s+([\d,]+)\s*€\s*\d$")

explicacion_peso_re = re.compile(r"^([\d,]+)\s*kg\s*x\s*([\d,]+)\s*€", re.IGNORECASE)
explicacion_uds_re = re.compile(r"^(\d+)\s*x\s*([\d,]+)\s*€", re.IGNORECASE)

def extract_date_time(text):
    m = fecha_hora_re.search(text)
    if m: 
        return m.group(1), m.group(2)
    return None, None

def comma_to_float(s):
    s=str(s)
    if not s:
        return 0.0
    return float(s.replace('.', '').replace(',', '.'))

def datos(text):
    text = text.replace('\xa0', ' ')
    lines = [l.strip() for l in text.splitlines() if l.strip() != '']

    fecha, hora = extract_date_time(text)

    m_id = factura_id_re.search(text)
    factura_id = m_id.group(1) if m_id else None

    total = None
    for l in lines:
        m_total = total_re.search(l)
        if m_total:
            total = m_total.group(1)
            break

    end = None
    for i, l in enumerate(lines):
        if total_re.search(l):
            end = i
            break
    comercio = "Aldi"

    factura_obj = Factura(comercio = comercio, factura_id=factura_id, hora=hora, fecha=fecha, total=comma_to_float(total))

    if end is not None:
        block = lines[:end]

        articulos_temporales = []
        
        for line in block:

            m_uds = explicacion_uds_re.search(line)
            if m_uds and articulos_temporales:
                articulos_temporales[-1]['qty'] = int(m_uds.group(1))
                articulos_temporales[-1]['precio_ud'] = m_uds.group(2)
                continue

            m_peso = explicacion_peso_re.search(line)
            if m_peso and articulos_temporales:
                articulos_temporales[-1]['qty'] = m_peso.group(1)
                articulos_temporales[-1]['precio_ud'] = m_peso.group(2)

            m = item_line_re.match(line)
            if m:
                nombre = m.group(1).strip()
                precio_total = m.group(2)

                articulos_temporales.append({
                    'nombre': nombre,
                    'qty': 1,
                    'precio_ud': precio_total, 
                    'precio_total': precio_total,
                    'descuento': '0,00'
                })

        for art in articulos_temporales:
            factura_obj.agregar_articulo(
                str(art['nombre']), 
                float(comma_to_float(art['qty'])), 
                float(comma_to_float(art['precio_ud'])), 
                float(comma_to_float(art['precio_total'])), 
                float(comma_to_float(art['descuento']))
            )
                        
    return factura_obj

    
