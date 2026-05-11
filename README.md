
                            *Puesta en funcionamiento del sistema*

===============================================================================================
                      _Requisitos Previos: Instalación de Python y Librerías_
===============================================================================================
Para que el backend funcione correctamente, asegúrate de tener Python instalado en tu sistema 
(puedes descargarlo desde python.org). También necesitarás Node.js para ejecutar el archivo 
server.js. 
Una vez tengas Python instalado, debes instalar las librerías necesarias. Abre una terminal y 
ejecuta el siguiente comando: 
pip install fastapi uvicorn PyPDF2 fpdf google-genai google pandas

===============================================================================================
                       _Configuración de la API Key de Google Gemini_
===============================================================================================
Para que el sistema pueda leer la clave API de Gemini es necesario obtenerla y guardarla como 
una variable de entorno en tu sistema. 
Paso A: Encontrar/Crear la API Key 
1. Ve a Google AI Studio. 
2. Inicia sesión con tu cuenta de Google. 
3. Haz clic en el botón "Create API key" y copia la clave generada.

Paso B: Guardarla en el sistema Abre una terminal y configura la variable de entorno 
dependiendo de tu sistema operativo: 

• En Windows (Símbolo del sistema / CMD): 
set GEMINI_API_KEY=”tu_api_key_aqui” 
• En Windows (PowerShell): 
env:GEMINI_API_KEY="tu_api_key_aqui” 
• En macOS o Linux: 
export GEMINI_API_KEY="tu_api_key_aqui" 

===============================================================================================
                                _Ejecutar los Servidores_
===============================================================================================
Para ejecutar tanto el servidor Node como la API en Python simultáneamente, se necesita abrir 
dos ventanas de terminal distintas. Ambas terminales, deben situarse en la siguiente carpeta del 
proyecto:
cd ruta/hacia/tu/carpeta/BACKEND_CONTRASEÑAS

Terminal 1 (Para ejecutar el servidor Node): Asegúrate de que estás en la carpeta correcta 
y ejecuta:

node server.js

Terminal 2 (Para ejecutar la API de Python): En la segunda ventana, dentro de la misma 
carpeta, ejecuta: 

python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload 
