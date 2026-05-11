
#==============================================================================================================================
#                COMANDO INICIO: python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
#==============================================================================================================================

import os
import sys
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS DE CARPETAS
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(str(BASE_DIR))

CARPETA_FACTURAS = BASE_DIR / "FACTURAS" / "procesar"
CARPETA_FACTURAS.mkdir(parents=True, exist_ok=True)

sys.path.append(str(BASE_DIR / "scripts"))
import main; # type: ignore

# ==========================================
# 2. INICIALIZAR APP Y SEGURIDAD (CORS)
# ==========================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 3. RUTAS PARA COMUNICARSE CON NODE.JS
# ==========================================

@app.post('/subir-factura')
async def recibir_y_procesar(ticket: UploadFile = File(...)):
    ruta_guardado = CARPETA_FACTURAS / ticket.filename

    try:
        with open(ruta_guardado, "wb") as buffer:
            shutil.copyfileobj(ticket.file, buffer)
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al guardar el archivo en el servidor: {e}"
        )

    try:
        resultado = main.procesa_factura(ruta_guardado)
        print(resultado)
        return {"resultado_python": resultado}
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except FileExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e) 
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error interno inesperado al procesar: {e}"
        )

@app.post('/actualizar_factura')
async def confirmar_y_guardar(request: Request):
    try:
        factura_aprobada = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El cuerpo de la petición no es un JSON válido."
        )

    try:
        print(factura_aprobada)
        main.guardar_correcto(factura_aprobada)
        return {"mensaje": "Factura guardada correctamente"}
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"Permiso denegado al guardar (¿archivo abierto en otro programa?): {e}"
        )
        
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error del sistema de archivos al guardar: {e}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error inesperado al guardar la factura: {e}")
       
@app.post('/get_grafico')
async def get_graf(request: Request):
    try:
        body = await request.json()
        periodo_seleccionado = body.get("periodo", "todo_ano")

        datos = main.datos_graf(periodo=periodo_seleccionado)
        print(datos)
        return datos
        
    except Exception as e:
        return {"error": str(e)}
    
@app.post('/buscar_articulo')
async def buscar_art(request: Request):

    try:
        body = await request.json()
        nombre_buscado = body.get("articulo", "")

        resultados = main.buscar_historial_articulo(nombre_buscado)
        print(resultados)
        return {"resultados": resultados}
        
    except Exception as e:
        return {"error": str(e)}