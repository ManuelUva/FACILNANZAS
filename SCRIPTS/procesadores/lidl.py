import re
from procesadores.factura import Factura

# --- Expresiones regulares adaptadas para LIDL ---
fecha_hora_re = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}:\d{2})")
factura_id_re = re.compile(r"(\d{5,6}/\d{2})")
total_re = re.compile(r"^Total\s+([\d,]+)", re.IGNORECASE)

# 1. Artículo normal (Ej: "Barra de pan 0,47 E")
item_line_re = re.compile(r"^(.*?)\s+([\d,]+)\s+[A-Z]$")

# 2. Artículo con unidades (Ej: "-/Hamburguesa Angus 2,49x 2 4,98 B")
item_mult_same_line_re = re.compile(r"^(.*?)\s+([\d,]+)x\s+([\d,]+)\s+([\d,]+)\s+[A-Z]$", re.IGNORECASE)

# 3. Línea de descuento: Texto seguido de espacios y un importe negativo
descuento_re = re.compile(r"^(.*?)\s+-\s*([\d,]+)$")

explicacion_peso_re = re.compile(r"^([\d,]+)\s*kg\s*x\s*([\d,]+)", re.IGNORECASE)
explicacion_uds_re = re.compile(r"^(\d+)\s*x\s*([\d,]+)", re.IGNORECASE)

def extract_date_time(text):
    m = fecha_hora_re.search(text)
    return (m.group(1), m.group(2)) if m else (None, None)

def comma_to_float(s):
    s=str(s)
    if not s:
        return 0.0
    return float(s.replace('.', '').replace(',', '.'))

def datos(text, comercio="LIDL"):
    text = text.replace('\xa0', ' ')
    lines = [l.strip() for l in text.splitlines() if l.strip() != '']

    fecha, hora = extract_date_time(text)

    m_id = factura_id_re.search(text)
    factura_id = m_id.group(1).replace("/", "") if m_id else None

    total = None
    end = None
    for i, l in enumerate(lines):
        m_total = total_re.search(l)
        if m_total:
            total = m_total.group(1)
            end = i
            break

    factura_obj = Factura(comercio, factura_id, hora, fecha, comma_to_float(total))

    if end is not None:
        block = lines[:end]
        articulos_temporales = []
        
        for line in block:
            if not line:
                continue
                
            # --- COMPROBACIÓN DE DESCUENTOS ---
            m_dto = descuento_re.search(line)
            if m_dto and articulos_temporales:
                # Actualizamos SOLO el último artículo añadido ([-1])
                dto_actual = float(articulos_temporales[-1]['descuento'].replace(',', '.'))
                dto_nuevo = float(m_dto.group(2).replace(',', '.'))
                
                # Sumamos el descuento (por si hay varios en el mismo producto)
                articulos_temporales[-1]['descuento'] = f"{(dto_actual + dto_nuevo):.2f}".replace('.', ',')
                
                # print(f"-> Descuento de {m_dto.group(2)} aplicado a: {articulos_temporales[-1]['nombre']}")
                continue
                
            m_uds = explicacion_uds_re.search(line)
            if m_uds and articulos_temporales:
                articulos_temporales[-1]['qty'] = m_uds.group(1)
                articulos_temporales[-1]['precio_ud'] = m_uds.group(2)
                continue
            
            m_peso = explicacion_peso_re.search(line)
            if m_peso and articulos_temporales:
                articulos_temporales[-1]['qty'] = m_peso.group(1)
                articulos_temporales[-1]['precio_ud'] = m_peso.group(2)
                continue
            
            m_mult = item_mult_same_line_re.match(line)
            if m_mult:
                articulos_temporales.append({
                    'nombre': m_mult.group(1).strip(),
                    'precio_ud': m_mult.group(2),
                    'qty': m_mult.group(3),
                    'precio_total': m_mult.group(4),
                    'descuento': '0,00'
                })
                continue

            m_item = item_line_re.match(line)
            if m_item:
                articulos_temporales.append({
                    'nombre': m_item.group(1).strip(),
                    'qty': 1,
                    'precio_ud': m_item.group(2), 
                    'precio_total': m_item.group(2),
                    'descuento': '0,00'
                })


        # Finalmente, pasamos cada artículo individual con su propio descuento a tu clase
        for art in articulos_temporales:
            factura_obj.agregar_articulo(
                str(art['nombre']), 
                float(comma_to_float(art['qty'])), 
                float(comma_to_float(art['precio_ud'])), 
                float(comma_to_float(art['precio_total'])), 
                float(comma_to_float(art['descuento']))
            )

    return factura_obj