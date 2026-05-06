from google import genai
from google.genai import types
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def obtener_texto_de_imagen(path_imagen, modelo= "gemini-3.1-flash-lite-preview"):
    client = genai.Client(api_key=API_KEY)

    instruccion = (
        "Extrae todo el texto de esta imagen. Devuelve única y exclusivamente el texto tal cual está escrito, respetando los saltos de línea. No agregues ningún comentario extra."
    )
    try:
        with open(path_imagen, "rb") as f:
            imagen_bytes = f.read()
            
        mime_type = "image/png" if str(path_imagen).lower().endswith(".png") else "image/jpeg"
        imagen_part = types.Part.from_bytes(data=imagen_bytes, mime_type=mime_type)
        print(f"Cargada imagen: {path_imagen}")
        
    except FileNotFoundError:
        # Error si el archivo no existe
        raise ValueError(f"No se encontró el archivo en la ruta: {path_imagen}")
    except Exception as e:
        # Cualquier otro error de lectura
        raise ValueError(f"Error al leer la imagen local: {e}")

    respuesta = client.models.generate_content(
        model=modelo,
        contents=[instruccion, imagen_part]
    )
    
    if not respuesta.text:
        raise ValueError("La respuesta de la IA está vacía (posible bloqueo por seguridad).")
    
    return respuesta.text

    # Método de comprobación de modelos de Gemini disponibles. Primero imprime todos y luego solo os que contengan flash
def modelos_disponibles():
    client = genai.Client(api_key=API_KEY)

    print("Tus modelos disponibles son:")
    for modelo in client.models.list():
        print(f" -> {modelo.name}")

    print("\n")
    print("Tus modelos disponibles con 'flash' en el nombre son:")
    for modelo in client.models.list():
        if "flash" in modelo.name.lower():
            print(f" -> {modelo.name}")

    return

if __name__=="__main__":
    modelos_disponibles()