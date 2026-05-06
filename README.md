9.	Manual del usuario para desplegar Facilnanzas
El siguiente manual detalla paso a paso el funcionamiento de la aplicación web Facilnanzas, guiando al usuario desde el registro hasta el análisis de sus gastos y la gestión de su histórico.
9.1. Acceso a la plataforma (Registro e Inicio de Sesión)
Al entrar en la aplicación, la primera pantalla que visualizará el usuario es la pasarela de autenticación. Esta pantalla garantiza que los datos financieros de cada usuario estén protegidos y sean privados.
•	Inicio de sesión: Si el usuario ya dispone de una cuenta, bastará con introducir su correo electrónico y contraseña y pulsar en "Acceder a mi cuenta".
•	Registro: Si es un usuario nuevo, puede hacer clic en "Regístrate gratis" en la parte inferior. El formulario cambiará para permitir la creación de una nueva cuenta. Una vez registrado, podrá iniciar sesión de inmediato.
 
Ilustración 25: Pantalla de login/registro 
9.2. Interfaz Principal y Navegación
Una vez autenticado, el usuario accede al panel principal de la aplicación. En la parte superior, encontrará la cabecera con el logo, el botón de "Ayuda" y "Mi Perfil". Justo debajo, se encuentra el menú de navegación principal con tres pestañas clave que organizan toda la funcionalidad de Facilnanzas:
1.	Subir Tickets: El escáner inteligente para añadir nuevos gastos.
2.	Ver Finanzas: El panel de análisis y gráficos.
3.	Histórico: El registro detallado de todas las compras anteriores.
 
Ilustración 26: Vista general del panel superior con el menú de navegación
9.3. Subida y Procesamiento de Tickets (Escáner Inteligente)
La pestaña por defecto al entrar es "Subir Tickets". Aquí es donde entra en juego el motor de inteligencia artificial de Gemini.
1.	Subida de archivos: El usuario puede añadir directamente un archivo (PDF, JPG, PNG) al recuadro haciendo clic sobre él para abrir el explorador de archivos de su dispositivo.
2.	Procesamiento: Una vez subido, aparecerá un indicador de carga avisando de que "Gemini AI extrayendo datos...". En este momento, el sistema está leyendo el ticket y estructurando la información (comercio, productos, precios, cantidades).
3.	Gestión de errores: Si el ticket está duplicado, borroso o el formato no es válido, el sistema mostrará una alerta en rojo indicando el problema exacto para que el usuario pueda corregirlo.
  
Ilustración 27: Recuadro donde subir los tickets
 
Ilustración 28: Spinner de carga tras subir un ticket
9.4. Validación y Edición de Datos
Una vez que la IA termina de procesar el ticket, la vista cambia automáticamente a la fase de "Revisión de Datos". Facilnanzas no guarda nada sin el consentimiento del usuario.
•	Se muestra una tabla con las columnas: Producto, Cantidad, Precio y Supermercado.
•	Edición interactiva: Si la inteligencia artificial ha cometido algún error de lectura (por ejemplo, confundir una letra), el usuario puede hacer clic directamente sobre cualquier celda de la tabla y corregir el texto o el número como si fuera un documento de Excel.
•	Guardado: Una vez que la información es correcta, el usuario hace clic en el botón verde "Confirmar y Guardar". El sistema calculará automáticamente los totales y lo añadirá a su base de datos.
 
Ilustración 29: La tabla de validación de datos con un ejemplo de compra 
9.5. Panel de Finanzas y Gráficos
Al navegar a la pestaña "Ver Finanzas", el usuario obtiene una visión global de su salud económica basada en los tickets guardados.
•	Filtros de tiempo: En la esquina superior derecha, se puede filtrar la información por periodos: "Este Mes", "Mes Pasado", "Todo el Año" o "Histórico Total". Al pulsar "Aplicar", los datos se actualizan en tiempo real.
•	KPIs (Indicadores Clave): En la parte superior se muestran tres tarjetas con información rápida:
o	Gasto Total: La suma de todo el dinero gastado en el periodo seleccionado.
o	Súper Favorito: El supermercado donde más dinero se ha gastado.
o	Ticket más caro: El importe de la compra más elevada.
•	Distribución de Gastos: Un gráfico de anillo (donut) interactivo que muestra el porcentaje y cantidad de dinero gastado en cada supermercado (Mercadona, Carrefour, Lidl, etc.), permitiendo identificar rápidamente dónde se va la mayor parte del presupuesto.
 
Ilustración 30: Vista completa de Finanzas
9.6. Histórico y Búsqueda Inteligente
En la pestaña "Histórico", el usuario tiene acceso a cada producto individual que ha comprado desde que utiliza la aplicación.
•	Registro tabular: Una tabla ordenada muestra la fecha, el supermercado, el nombre del producto y el precio por unidad de todo el historial.
•	Buscador Inteligente: No es una simple búsqueda de texto. Utilizando la barra de búsqueda superior, el usuario puede buscar por palabras clave (ej. "Aceite", "Leche", "Mercadona"). Al pulsar "Buscar", el backend con IA filtra la base de datos y devuelve todas las coincidencias exactas y relacionadas, permitiendo al usuario comparar fácilmente a qué precio compró un artículo en el pasado y en qué establecimiento.
 
Ilustración 31: Historial de búsqueda del producto “Leche”
9.7. Gestión del Perfil y Ayuda
Por último, el usuario puede gestionar su cuenta a través de los botones situados en la esquina superior derecha:
•	Mi Perfil: Muestra el nombre y correo del usuario conectado. Desde aquí se pueden gestionar los ajustes de la cuenta (como cambiar la contraseña) y, de forma segura, Cerrar Sesión para proteger los datos en ordenadores compartidos.
•	Ayuda: Un centro de soporte rápido donde el usuario puede consultar Preguntas Frecuentes (FAQ) sobre el funcionamiento de la IA o contactar directamente con el equipo de soporte técnico mediante teléfono o enviando un ticket de asistencia.
 
Ilustración 32: Apartado del perfil del usuario
 
Ilustración 33: Apartado de Ayuda al usuario







