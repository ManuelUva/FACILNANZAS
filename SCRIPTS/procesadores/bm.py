import re
from procesadores.factura import Factura

fecha_hora_re = re.compile(r"(\d{2}[/-]\d{2}[/-]\d{2,4})\s*[/ ]?\s*(\d{2}:\d{2}(?::\d{2})?)")

trailing_prices_re = re.compile(r'(?:[\s,"C€]+|^)(-?\d{1,3}(?:[.,]\d{3})*[.,]\d{2})[\s,"]*(?:[\s,"C€]+(-?\d{1,3}(?:[.,]\d{3})*[.,]\d{2})[\s,"]*)?$')
total_re = re.compile(r"TOTAL COMPRA.*?(-?\d{1,3}(?:[.,]\d{3})*[.,]\d{2})", re.IGNORECASE)
factura_id_re = re.compile(r"\b(\d{17})\b") # Los IDs en este ticket BM tienen 17 dígitos

def comma_to_float(s):
    if not s:
        return 0.0
 
    s = s.replace('"', '').strip()

    last_comma = s.rfind(',')
    last_dot = s.rfind('.')
    
    if last_comma > last_dot:
        s = s.replace('.', '').replace(',', '.')
    elif last_dot > last_comma:
        s = s.replace(',', '')
        
    return float(s)

def extract_date_time(text):
    m = fecha_hora_re.search(text)
    if m: 
        return m.group(1), m.group(2)[:5] 
    return None, None

def datos(text, blacklist_words):
    text = text.replace('\xa0', ' ')

    lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in text.splitlines() if l.strip() and l.strip() != '",,"']
    
    fecha, hora = extract_date_time(text)

    # Buscar ID de factura
    if m_id := factura_id_re.search(text):
        factura_id = m_id.group(1)
    else:
        factura_id = None

    start, end = None, None
    for i, l in enumerate(lines):
        upper_l = l.upper()
        if 'IMPORTE' in upper_l:
            start = i + 1
        elif 'TOTAL COMPRA' in upper_l:
            end = i
            break
            
    block = lines[start:end] if (start is not None and end is not None) else lines

    m_total = total_re.search(text.replace('\n', ' '))
    total_factura = comma_to_float(m_total.group(1)) if m_total else 0.0

    factura_obj = Factura(
        comercio="BM Supermercados", 
        factura_id=factura_id, 
        hora=hora, 
        fecha=fecha, 
        total=total_factura
    )
    
    for line in block:
        if not line:
            continue

        if not (m := trailing_prices_re.search(line)):
            continue
            
        price1, price2 = m.group(1), m.group(2) 

        line_without_prices = line[:m.start()].replace('"', '').strip()

        qty = 1
        if qmatch_start := re.match(r'^(\d+)\s+', line_without_prices):
            qty = int(qmatch_start.group(1))
            name = line_without_prices[qmatch_start.end():].strip()
        elif qmatch_end := re.search(r'\s+(\d+)$', line_without_prices):
            qty = int(qmatch_end.group(1))
            name = line_without_prices[:qmatch_end.start()].strip()
        else:
            name = line_without_prices

        is_discount_voucher = "VALES TARJETA" in line_without_prices.upper()
        if not is_discount_voucher and any(b in name.upper() for b in blacklist_words):
            continue

        try:
            f1 = comma_to_float(price1)
            f2 = comma_to_float(price2) if price2 else None
        except ValueError:
            continue

        descuento = 0.0
        precio_ud = f1
        precio_total = f2 if f2 is not None else f1

        if f1 < 0 and f2 is None:
            descuento = f1
            precio_ud = 0.0
            precio_total = f1

        factura_obj.agregar_articulo(
            str(name), 
            float(qty), 
            float(precio_ud), 
            float(precio_total), 
            float(descuento)
        )

    return factura_obj