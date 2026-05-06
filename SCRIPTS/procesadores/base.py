import procesadores.eroski
import procesadores.mercadona
import procesadores.carrefour
import procesadores.bm
import procesadores.aldi
import procesadores.lidl
import procesadores.facilnanzas

class ErrorFactura(Exception):
    """Clase base para excepciones de este módulo."""
    pass

class FacturaVaciaError(ErrorFactura):
    """Se lanza cuando el texto de la factura no contiene datos."""
    def __init__(self, mensaje="El texto de la factura está vacío"):
        self.mensaje = mensaje
        super().__init__(self.mensaje)

class ComercioNoIdentificadoError(ErrorFactura):
    """Se lanza cuando no se reconoce ninguna palabra clave del comercio."""
    def __init__(self, texto):
        self.mensaje = f"No se pudo identificar el comercio en el texto: '{texto[:30]}...'"
        super().__init__(self.mensaje)
               
blacklist_words = [
    'TOTAL', 'TARJETA', 'AHORRO', 'CUENTA', 'APP', 'TIPO', 
    'BASE', 'REQ', 'COPIA', 'FECHA', 'CENTRO', 'SEC/AUTORIZ', 
    'COMERCIO', 'TITULAR', 'ARC', 'N.SEC', 'AID', 'ET.APLICACION', 
    'M. VALIDACION', 'VENTA', 'IMPORTE', 'EUR', 'ALIMENTACIÓN',
    'BODEGA', 'UD/KG', 'CARNICERÍA', 'CHARCUTERÍA'
    'IVA', 'GUZTIZKOAK', 'SALDO', 'BEHERAPENAK', 'DESCUENTO',
    'WWW', 'TBAI', 'S.:', 'SC:', 'EGUNA', 'TIKET-ZENB', 'ESTABLECIMIENTO',
    'KUTXA-ZENB', 'NUMERO CAJERA', 'IMPORTE', 'ENT. AUT.', 'BAIMENA',
    'COPIA PARA EL CLIENTE', 'DESCUENTOS', 'ORDAINTZEKOA', 'MOVIL', 
    'EQUIPAMIENTO FAMILIAR', 'MADARIAGA', 'IFK/CIF', 'SARRERA/', 
    'ING.CLUB', 'SALDO EN TU MONEDERO', 'BEZA BARNE', 'TIKET-ZENB'
]        
    
def extrae_datos(texto):
    # 1. Validación de factura vacía
    if not texto or not texto.strip():
        raise FacturaVaciaError()
    t = texto.upper()
    
    try:
        if "FACILNANZAS" in t:
            return procesadores.facilnanzas.datos(texto)
        if "EROSKI" in t:
            return procesadores.eroski.datos(texto, blacklist_words)
        if "MERCADONA" in t:
            return procesadores.mercadona.datos(texto)
        if "CARREFOUR" in t:
            return procesadores.carrefour.datos(texto)
        if "ALDI" in t:
            return procesadores.aldi.datos(texto)
        if "LIDL" in t:
            return procesadores.lidl.datos(texto)
        if "BM" in t:
            return procesadores.bm.datos(texto, blacklist_words)
        
        # Si llega aquí, es que no reconoció el comercio
        raise ComercioNoIdentificadoError(texto)

    except ErrorFactura as e:
        print(f"Error de validación: {e}")
        return 0
    except Exception as e:
        print(f"Error inesperado de sistema: {e}")
        return 0