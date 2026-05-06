import re
from procesadores.factura import Factura

def datos(texto_raw: str):

    texto_limpio = re.sub(r"\\", "", texto_raw)
    texto_limpio = texto_limpio.replace('"', '').replace('|', '')

    match_comercio = re.search(r"(Aldi|Eroski)", texto_limpio, re.IGNORECASE)
    comercio = match_comercio.group(1).capitalize() if match_comercio else "Desconocido"

    match_id = re.search(r"(FS\d{18}|\d{18})", texto_limpio)
    factura_id = match_id.group(1) if match_id else "Desconocido"

    match_fecha = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})\s+(\d{2}:\d{2}(?::\d{2})?)", texto_limpio)
    if match_fecha:
        fecha = match_fecha.group(1).replace('/', '-') 
        hora = match_fecha.group(2)
    else:
        fecha, hora = "Desconocido", "Desconocido"

    match_total = re.search(r"TOTAL TICKET:\W*([\d,]+)\W*EUR", texto_limpio)
    total = match_total.group(1) if match_total else "0,00"

    factura = Factura(comercio=comercio, factura_id=factura_id, hora=hora, fecha=fecha, total=total)

    patron_articulo = re.compile(
        r"(?P<nombre>[A-ZÑ#][A-ZÑ0-9\s#\.]+[A-ZÑ0-9])\s+"  # Nombre
        r"(?P<cant>\d+(?:,\d+)?)\s+"                       # Cantidad 
        r"(?P<p_ud>[\d,]+)\s*EUR\s+"                       # Precio Ud
        r"(?P<p_total>[\d,]+)\s*EUR\s+"                    # Precio Total
        r"(?P<desc>[\d.,]+)(?:\s*EUR)?",                   # Descuento
        re.MULTILINE
    )

    for match in patron_articulo.finditer(texto_limpio):
        nombre = re.sub(r"\s+", " ", match.group("nombre")).strip()
        if any(palabra in nombre for palabra in ["TOTAL", "SUBTOTAL", "FACILNANZAS", "NOMBRE"]):
            continue

        factura.agregar_articulo(
            nombre=nombre,
            cantidad=match.group("cant"),
            precio_ud=match.group("p_ud"),
            precio_total=match.group("p_total"),
            descuento=match.group("desc")
        )

    return factura