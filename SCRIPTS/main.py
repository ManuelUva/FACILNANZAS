#Librerías nativas python
import os
import csv
from pathlib import Path 
import json
import io
from datetime import datetime
import unicodedata

#Librerías facilnanzas
import imgText
import procesadores.base
from procesadores.factura import Factura

#Librerías ajenas
import PyPDF2
from fpdf import FPDF
from google.genai import errors
import pandas as pd


RUTA_BASE = Path(r'FACTURAS/procesar')
RUTA_TRAMITADAS = Path(r'FACTURAS/tramitadas')
RUTA_FALLO = Path(r'FACTURAS/fallo')
ARCHIVO_CSV = "gastos_totales.csv"

def save_to_pdf(factura_obj, subcarpeta = RUTA_TRAMITADAS):
    
    texto  = factura_obj.make_invoce()
    nombre_archivo = factura_obj.get_name()
    
    if not nombre_archivo.endswith('.pdf'):
        nombre_archivo += '.pdf'

    altura = (texto.count('\n') + 1) * 6 + 6
    ancho  = len(texto.splitlines()[0])*1.95
    texto = texto.replace("€", "EUR")
    texto = unicodedata.normalize('NFKC', texto)

    ruta_completa = os.path.join(subcarpeta, nombre_archivo)
    ruta_fallo =  os.path.join(RUTA_FALLO, nombre_archivo)

    pdf = FPDF(format=(ancho, altura))
    pdf.add_page()

    pdf.set_font("Courier", size=8)

    pdf.multi_cell(0, 4, text=texto, align='L')

    try:
        directorio = os.path.dirname(ruta_completa)
        if directorio:
            os.makedirs(directorio, exist_ok=True)
                
        pdf.output(ruta_completa)
        print(f"Ticket guardado exitosamente en: {ruta_completa}")
        return 1

    except Exception as e:
        print(f'Error inesperado con {nombre_archivo}: {str(e)}')
        return 0

def save_to_json(texto, nombre_archivo, subcarpeta = RUTA_BASE):
    if not os.path.exists(subcarpeta):
        os.makedirs(subcarpeta)
    
    if not nombre_archivo.endswith('.json'):
        nombre_archivo += '.json'

    ruta_completa = os.path.join(subcarpeta, nombre_archivo)
    
    datos = {
        "texto_original": texto
    }

    with open(ruta_completa, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Guardado en: {ruta_completa}")

def pdf_to_text(pdf):
    # Extraer infomración del PDF   
    with open(pdf, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ' '

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    return text

def save_to_csv(factura_obj, filename=ARCHIVO_CSV):
    file_exists = os.path.isfile(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter = ';')
        # Solo escribe encabezados si el archivo no existía
        if not file_exists:
            writer.writerow([
            "comercio", "factura_id", "fecha", "nombre",
            "cantidad", "precio_ud", "precio_total",
            "descuento_tarjeta", "total_ticket"
            ])

        for art in factura_obj.articulos:
            writer.writerow([
                factura_obj.comercio,
                factura_obj.factura_id,
                factura_obj.fecha_hora,
                art.nombre,
                art.cantidad,
                art.precio_ud,
                art.precio_total,
                art.descuento_tarjeta,
                factura_obj.total_ticket
            ])
    historial(factura_obj.get_name())   # Actualiza un archivo donde guarda todos los nombres de facturas procesadas para futuras implementaciones
    print(f"✅ Datos de la factura {factura_obj.factura_id} ({factura_obj.comercio}) añadidos a: {filename}")

def mover_archivo(archivo, factura_obj, destino): 
    factura_name = factura_obj.get_name()
    extension = os.path.splitext(archivo)[1]
    destino = os.path.join(destino, f"{factura_name}{extension}")
    os.makedirs(os.path.dirname(destino), exist_ok=True)

    try:
        os.replace(archivo, destino)

    except FileNotFoundError:
        historial(f'fallo con factura {factura_name}: el archivo origen no existe')
        return 0
    except Exception as e:
        historial(f'error inesperado con factura {factura_name}: {str(e)}')
        return 0

def historial(operacion):
    filename =("historial.txt")
    with open(filename, mode="a", encoding="utf-8") as log:
        log.write(operacion + '\n')
    print(f"historial actualizado: {operacion}")

def procesar_pdf(ruta_archivo):
    return pdf_to_text(ruta_archivo)

def procesar_ia(ruta_archivo):
    # Orden de prioridad de los modelos
    modelos = [
        "gemini-3.1-flash-lite-preview",    # 1. Principal
        "gemini-3-flash-preview",           # 2. Primer respaldo
        "gemini-2.5-flash",                 # 3. Segundo respaldo
        "gemini-2.5-flash-lite"             # 4. Tercer respaldo
    ]
    
    resultado = None 
    
    for modelo in modelos:
        try:
            resultado = imgText.obtener_texto_de_imagen(ruta_archivo, modelo)
            print(f"✅ Éxito usando el modelo: {modelo}")
            return resultado  
        # Si tiene éxito, retorna el resultado y sale de la función
            
        except errors.APIError as e:
            # Se comprueban los errores de disponibilidad (503) o de cuota (429)
            if e.code in [503, 429]:
                motivo = "no disponible" if e.code == 503 else "cuota agotada"
                print(f"⚠️ Error {e.code}: {modelo} {motivo}. Cambiando al siguiente modelo...")
                continue  # Pasa al siguiente modelo en la lista
            else:
                # Si es otro error de API detenemos la ejecución
                print(f"🔥 Error de API inesperado (Código {e.code}) con {modelo}: {e}")
                break
                
        except ValueError as e:
            # Los errores de contenido aplican a todos los modelos
            print(f"🚫 Contenido bloqueado o sin texto: {e}")
            break
            
        except Exception as e:
            print(f"🔥 Error genérico inesperado con {modelo}: {str(e)}")
            break
            
    # Si el bucle termina y resultado sigue siendo None, significa que todos los modelos fallaron
    if resultado is None:
        raise Exception("Fallo crítico: Todos los modelos IA disponibles fallaron o devolvieron error.")
        
    return resultado

def busca_factura(factura_obj):
    factura_name = factura_obj.get_name()      
    destino = os.path.join(RUTA_TRAMITADAS, f"{factura_name}.pdf")

    # Si existe, se eleva la excepción FileExistsError
    if os.path.exists(destino):
        raise FileExistsError(f"FACTURA DUPLICADA: {factura_name}")

PROCESADORES_POR_EXTENSION = {
    '.pdf': procesar_pdf,
    '.png': procesar_ia,
    '.jpeg': procesar_ia, 
    '.jpg': procesar_ia,
}

def main():     # Esta función se usa para crear la base de datos completa, procesa todas las facturas de la carpeta FACTURAS/procesar
    try:
        archivos = RUTA_BASE.iterdir()
    except (FileNotFoundError, PermissionError) as e:
        print(f"❌ Error al acceder al directorio base: {e}")
        return

    for archivo in archivos: 
        # 1. Validación de archivo
        if archivo.is_file():
            # 2. Elección de la forma de procesamiento del archivo(Gemini o PyPDF2)
            extension = archivo.suffix.lower()
            funcion_procesadora = PROCESADORES_POR_EXTENSION.get(extension)

            if funcion_procesadora:
                try:
                    # 3. Extracción de texto
                    texto = funcion_procesadora(archivo)  
                    # 4. Se limpia el texto
                    texto = unicodedata.normalize('NFKC', texto) 
                    # 5. Se crea el objeto factura (se procesa el texto)
                    factura_obj = procesadores.base.extrae_datos(texto)  
                
                except UnicodeDecodeError as e:
                    print(f"⏭️ Saltando {archivo} - Error de codificación: {e}")
                    continue
                except TypeError as e:
                    print(f"⏭️ Saltando {archivo} - Error de tipos (¿texto vacío?): {e}")
                    continue
                except ValueError as e:
                    print(f"⏭️ Saltando {archivo} - Error al extraer datos de la factura: {e}")
                    continue
                except Exception as e:
                    print(f"⏭️ Saltando {archivo} - Error inesperado al procesar: {e}")
                    continue
                
                if factura_obj != 0:            
                    try:
                        # 6. Comprovación de la existencia de la factura
                        busca_factura(factura_obj)
                        # 7. Guarda un archivo .pdf con el formato unificado de FACILNANZAS
                        save_to_pdf(factura_obj)
                        # 8. Guarda la información en la base de datos
                        save_to_csv(factura_obj, ARCHIVO_CSV)
                        # 9. FIN borra el archivo procesado
                        os.remove(archivo)
                        
                    except FileExistsError as e:
                        print(f"⚠️ {e}")
                        resultado_mover = mover_archivo(archivo, factura_obj, RUTA_FALLO)
                        if str(resultado_mover) == "1":
                            continue
                            
                    except PermissionError as e:
                        print(f"⚠️ Error de permisos al guardar/borrar en {archivo}: {e}")
                        continue
                        
                    except OSError as e:
                        print(f"⚠️ Error del sistema de archivos con {archivo}: {e}")
                        continue
                        
                    except Exception as e:
                        print(f"⚠️ Error inesperado al guardar datos de {archivo}: {e}")
                        continue
                    
                print('-------------------------------------------')

            else:
                print(str(archivo) + " IGNORADO: Extensión no soportada.")
      
# ==========================================
#              FUNCIONES SERVIDOR
# ==========================================
  
def procesa_factura(archivo):
    # 1. Validación de entrada
    if archivo is None:
        raise ValueError("❌ Error: Se ha pasado 'None' en lugar de un archivo válido.")
        
    if not archivo.is_file():
        raise FileNotFoundError(f"❌ Error: El archivo no existe o la ruta no es válida -> {archivo}")
    
    # 2. Elección de la forma de procesamiento del archivo(Gemini o PyPDF2)
    extension = archivo.suffix.lower()
    funcion_procesadora = PROCESADORES_POR_EXTENSION.get(extension)

    if not funcion_procesadora:
        raise ValueError(f"❌ Extensión no soportada: {extension} en el archivo {archivo}")
    
    # 3. Extracción de texto
    texto_1 = funcion_procesadora(archivo)
    
    if not texto_1:
        raise ValueError(f"❌ Error: El archivo {archivo} está vacío o no se pudo extraer texto.")

    # 4. Se limpia el texto
    texto = unicodedata.normalize('NFKC', texto_1)
    # 5. Se crea el objeto factura (se procesa el texto)
    factura_obj = procesadores.base.extrae_datos(texto)
    
    if factura_obj == 0 or factura_obj is None:
        raise ValueError(f"❌ Error: No se pudo generar la factura a partir del texto en {archivo}.")

    # 6. Comprovación de la existencia de la factura
    busca_factura(factura_obj)
    # 7. Borrado el archivo procesado
    os.remove(archivo)

    return factura_obj.a_diccionario()
          
def guardar_correcto(datos_json_corregidos: dict) -> dict:
    factura_obj = Factura.desde_json(datos_json_corregidos)
    try: 
        # 7. Guarda un archivo .pdf con el formato unificado de FACILNANZAS
        save_to_pdf(factura_obj)
        # 9. FIN guarda la información en la base de datos
        save_to_csv(factura_obj)
    except Exception:
        print("Error al guardar factura")
        
def datos_graf(archivo_csv="gastos_totales.csv", periodo="todo_el_ano"):
    df = pd.read_csv(archivo_csv, sep=';')

    """if 'precio_total' in df.columns and df['precio_total'].dtype == object:
        df['precio_total'] = df['precio_total'].astype(str).str.replace(',', '.').astype(float)

    if 'total_ticket' in df.columns and df['total_ticket'].dtype == object:
        df['total_ticket'] = df['total_ticket'].astype(str).str.replace(',', '.').astype(float)"""

    df['fecha'] = pd.to_datetime(df['fecha'], format='mixed', dayfirst=True, errors='coerce')
    
    # Filtros de fecha
    hoy = datetime.now()
    
    if periodo == "este_mes":
        df_filtrado = df[(df['fecha'].dt.year == hoy.year) & (df['fecha'].dt.month == hoy.month)]
        
    elif periodo == "mes_pasado":
        mes_pasado = hoy.month - 1 if hoy.month > 1 else 12
        ano_pasado = hoy.year if hoy.month > 1 else hoy.year - 1
        df_filtrado = df[(df['fecha'].dt.year == ano_pasado) & (df['fecha'].dt.month == mes_pasado)]
        
    elif periodo == "todo_ano":
        # Desde el 1 de enero del año en curso
        df_filtrado = df[df['fecha'].dt.year == hoy.year]
        
    elif periodo == "ultimo_ano":
        # Desde hoy hasta hace exactamente 365 días
        hace_un_ano = hoy - pd.DateOffset(years=1)
        df_filtrado = df[(df['fecha'] >= hace_un_ano) & (df['fecha'] <= hoy)]
        
    else:
        df_filtrado = df 
        
    # Se grupa por comercio y sumar
    gastos_agrupados = df_filtrado.groupby('comercio')['precio_total'].sum().reset_index()
    
    # Ordenar de mayor a menor
    gastos_agrupados = gastos_agrupados.sort_values(by='precio_total', ascending=False)
    
    # Cálculo del ticket más caro de ese periodo
    if 'total_ticket' in df_filtrado.columns and not df_filtrado.empty:
        max_ticket = df_filtrado['total_ticket'].max()
        if pd.isna(max_ticket):
            max_ticket = 0.0
    else:
        max_ticket = 0.0

    return {
        "grafico": dict(zip(gastos_agrupados['comercio'], gastos_agrupados['precio_total'])),
        "ticket_mas_caro": float(max_ticket)
    }
    
def buscar_historial_articulo(nombre_articulo, ruta_csv="gastos_totales.csv"):
    try:
        df = pd.read_csv(ruta_csv, sep=";") 
        

        filtro = df['nombre'].str.contains(nombre_articulo, case=False, na=False)
        df_filtrado = df[filtro].copy()  # Se usa .copy() para evitar warnings al modificarlo

        df_filtrado['fecha_orden'] = pd.to_datetime(
            df_filtrado['fecha'], 
            format="%d/%m/%Y %H:%M:%S", 
            errors='coerce'
        )
        # Se Ordena por la fecha (ascending=False pone el más reciente primero)
        df_filtrado = df_filtrado.sort_values(by='fecha_orden', ascending=False)

        # Se Construir la lista de resultados
        resultados = []
        for index, fila in df_filtrado.iterrows():
            resultados.append({
                "fecha": str(fila.get("fecha", "")),
                "nombre": str(fila.get("nombre", "")),
                "super": str(fila.get("comercio", "")),
                "precio_ud": float(fila.get("precio_ud", 0.0))
            })
            
        return resultados

    except Exception as e:
        print(f"❌ Error al buscar el artículo '{nombre_articulo}': {e}")
        return []
        
if __name__ == "__main__":
    main()
    print(buscar_historial_articulo("lech"))