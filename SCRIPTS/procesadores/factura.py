class Articulo:
    def __init__(self, nombre: str, cantidad: float, precio_ud: float, precio_total: float, descuento: float):
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio_ud = precio_ud
        self.precio_total = precio_total
        self.descuento_tarjeta = descuento

    def a_diccionario(self) -> dict:
            return {
                "nombre": self.nombre,
                "cantidad": self.cantidad,
                "precio_ud": self.precio_ud,
                "precio_total": self.precio_total,
                "descuento": self.descuento_tarjeta
            }

class Factura:
    def __init__(self, comercio: str, factura_id: str, hora: str, fecha: str, total: float):
        self.comercio = comercio
        self.factura_id = factura_id

        if hora.count(':') == 1:        #Rectificación horaria para que tenga formaro HH:MM:SS
            hora += ":00"
            
        self.fecha_hora = f"{str(fecha).replace('-','/')} {hora}"
        self.total_ticket = total
        self.articulos = []
        
        
    def establece_fecha_hora(self, fecha_hora):
        self.fecha_hora = fecha_hora
           
    @classmethod
    def desde_json(cls, datos_json: dict):
        # 1. Extraemos los datos de la cabecera de la factura
        # Usamos .get() con valores por defecto para evitar errores si falta una clave
        comercio = datos_json.get('comercio', 'Desconocido')
        factura_id = datos_json.get('factura_id', '0000')
        fecha_hora = datos_json.get('fecha_hora', '01-01-0001')
        total = datos_json.get('total_ticket', '0.00')

        # 2. Creamos la instancia de Factura (cls es la propia clase Factura)
        nueva_factura = cls(comercio, factura_id, "00:00", "01-01-0001", total)       
        nueva_factura.establece_fecha_hora(fecha_hora)

        # 3. Procesamos los artículos y los convertimos en objetos 'Articulo'
        lista_productos = datos_json.get('productos', [])
        for p in lista_productos:
            articulo_obj = Articulo(
                nombre=p.get('nombre', 'Producto'),
                cantidad=p.get('cantidad', '1'),
                precio_ud=p.get('precio_ud', '0'),
                precio_total=p.get('precio_total', '0'),
                descuento=p.get('descuento', '0')
            )
            nueva_factura.articulos.append(articulo_obj)

        return nueva_factura

    def a_diccionario(self) -> dict:
        return {
            "comercio": self.comercio,
            "factura_id": self.factura_id,
            "fecha_hora": self.fecha_hora,
            "total_ticket": self.total_ticket,
            "productos": [articulo.a_diccionario() for articulo in self.articulos]
        }

    def make_invoce (self):
        ancho = 100
        nombre_ancho = 47
        cantidad_ancho = ancho/12
        precio_ud_ancho = 8
        precio_total_ancho = 8
        descuento_tarjeta_ancho = ancho/12

        lineas = []
        lineas.append("=" * ancho)
        lineas.append(f"{('FACILNANZAS').center(ancho)}") 
        lineas.append("=" * ancho)
        lineas.append(f"{self.comercio.center(ancho)}") 
        lineas.append("=" * ancho)
        lineas.append(f"Factura ID: {' ' * (ancho-32)}{self.factura_id:>20}")
        lineas.append(f"Fecha: {' ' * (ancho-26)}{self.fecha_hora:>16}")
        lineas.append("-" * ancho)
        lineas.append(f"{'Nombre':<{nombre_ancho}} | {'Cant.':<{cantidad_ancho}} | {'P. Ud':<{precio_ud_ancho+3}} | {'Total':<{precio_total_ancho+3}} | {'D. Tarjeta':<{descuento_tarjeta_ancho+3}}")
        lineas.append("-" * ancho)
        for art in self.articulos:
            nombre = str(art.nombre)[:30] 
            cantidad = str(art.cantidad)
            precio_ud = str(art.precio_ud)
            precio_total = str(art.precio_total)
            descuento_tarjeta = str(art.descuento_tarjeta)
            lineas.append(f"{nombre:<{nombre_ancho}} | {cantidad:<{cantidad_ancho}} | {precio_ud:<{precio_ud_ancho}}€ | {precio_total:<{precio_total_ancho}}€ | {descuento_tarjeta:<{descuento_tarjeta_ancho}}€")
        lineas.append("-" * ancho)
        lineas.append(f"Subtotal: {' ' * (ancho-21)} {str(self.total_ticket):>6} €")
        lineas.append(f"TOTAL TICKET: {' ' * (ancho-25)} {str(self.total_ticket):>6} €")  
        lineas.append("=" * ancho)

        invoce  = "\n".join(lineas)
        return invoce

    def agregar_articulo(self, nombre, cantidad, precio_total, precio_ud, descuento):
        nuevo_articulo = Articulo(nombre, cantidad, precio_total, precio_ud, descuento)
        self.articulos.append(nuevo_articulo)
        
    def get_name(self):
     return self.comercio + "-" + self.factura_id
        