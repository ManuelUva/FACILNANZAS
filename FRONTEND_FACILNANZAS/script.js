document.addEventListener('DOMContentLoaded', () => {

// ==========================================
// CONFIGURACIÓN DE RED
// ==========================================
    const IP_SERVIDOR = 'localhost'; 
    const PUERTO = '3000';
    const BASE_URL = `http://${IP_SERVIDOR}:${PUERTO}`;

// ==========================================
// 1. LÓGICA DEL LOGIN
// ==========================================
    const pantallaLogin = document.getElementById('pantalla-login');
    const appPrincipal = document.getElementById('aplicacion-principal');
    const formLogin = document.getElementById('formulario-login');
    const btnEntrarTexto = document.getElementById('texto-btn-entrar');
    const spinnerLogin = document.getElementById('spinner-login');
    const linkCambio = document.getElementById('link-cambio');
    const tituloLogin = document.getElementById('login-titulo');
    const textoCambio = document.getElementById('texto-cambio');
    const btnCerrarSesion = document.getElementById('btn-cerrar-sesion');

    let esRegistro = false;

    linkCambio.addEventListener('click', (e) => {
        e.preventDefault();
        esRegistro = !esRegistro;
        tituloLogin.innerText = esRegistro ? "Crea tu cuenta" : "Iniciar Sesión";
        btnEntrarTexto.innerText = esRegistro ? "Registrarse ahora" : "Acceder a mi cuenta";
        textoCambio.innerText = esRegistro ? "¿Ya tienes cuenta?" : "¿No tienes cuenta?";
        linkCambio.innerText = esRegistro ? "Inicia sesión" : "Regístrate gratis";
    });

    formLogin.addEventListener('submit', async (e) => {
        e.preventDefault(); 
        btnEntrarTexto.classList.add('oculto');
        spinnerLogin.classList.remove('oculto');
        
        const emailInput = document.getElementById('login-email-input').value;
        const passwordInput = document.getElementById('login-pass-input').value;

        const endpoint = esRegistro ? '/registro' : '/login';
        const urlFinal = BASE_URL + endpoint;

        try {
            const respuesta = await fetch(urlFinal, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: emailInput, password: passwordInput })
            });

            const datos = await respuesta.json();

            if (respuesta.ok) {
                if (esRegistro) {
                    mostrarToast("✅ Cuenta creada. Inicia sesión.");
                    linkCambio.click();
                } else {
                    localStorage.setItem('facilnanzas_token', datos.token);
                    pantallaLogin.classList.add('oculto');
                    appPrincipal.classList.remove('oculto');
                    mostrarToast("¡Bienvenido!");
                    actualizarDatosPerfil();
                    inicializarFinanzas(); 
                }
            } else {
                alert("Error: " + datos.mensaje_error);
            }
        } catch (error) {
            alert("❌ Error de conexión con el servidor");
        } finally {
            btnEntrarTexto.classList.remove('oculto');
            spinnerLogin.classList.add('oculto');
        }
    });

    if (btnCerrarSesion) {
        btnCerrarSesion.addEventListener('click', () => {
            localStorage.removeItem('facilnanzas_token');
            appPrincipal.classList.add('oculto');
            pantallaLogin.classList.remove('oculto');
            cambiarPestaña('escaner');
        });
    }

// ==========================================
// 2. NAVEGACIÓN Y PESTAÑAS
// ==========================================
    const btnNavEscaner = document.getElementById('nav-escaner');
    const btnNavFinanzas = document.getElementById('nav-finanzas');
    const btnNavHistorico = document.getElementById('nav-historico');
    const btnHeaderPerfil = document.getElementById('btn-header-perfil');
    const btnHeaderAyuda = document.getElementById('btn-header-ayuda');

    function cambiarPestaña(pestaña) {
        [btnNavEscaner, btnNavFinanzas, btnNavHistorico, btnHeaderPerfil, btnHeaderAyuda].forEach(b => {
            if(b) b.classList.remove('activo');
        });
        ['escaner', 'finanzas', 'historico', 'perfil', 'ayuda'].forEach(v => {
            const el = document.getElementById('vista-'+v);
            if(el) el.classList.add('oculto');
        });

        if(pestaña === 'escaner') { 
            btnNavEscaner.classList.add('activo'); 
            document.getElementById('vista-escaner').classList.remove('oculto'); 
        }
        if(pestaña === 'finanzas') { 
            btnNavFinanzas.classList.add('activo'); 
            document.getElementById('vista-finanzas').classList.remove('oculto'); 
            inicializarFinanzas(); 
        }
        if(pestaña === 'historico') { 
            btnNavHistorico.classList.add('activo'); 
            document.getElementById('vista-historico').classList.remove('oculto'); 
            renderizarHistorico(baseDeDatosHistorico); 
            renderizarGraficaHistorico(baseDeDatosHistorico);
        }
        if(pestaña === 'perfil') { 
            btnHeaderPerfil.classList.add('activo'); 
            document.getElementById('vista-perfil').classList.remove('oculto'); 
            actualizarDatosPerfil(); 
        }
        if(pestaña === 'ayuda') { 
            btnHeaderAyuda.classList.add('activo'); 
            document.getElementById('vista-ayuda').classList.remove('oculto'); 
        }
    }

    btnNavEscaner.addEventListener('click', () => cambiarPestaña('escaner'));
    btnNavFinanzas.addEventListener('click', () => cambiarPestaña('finanzas'));
    btnNavHistorico.addEventListener('click', () => cambiarPestaña('historico'));
    btnHeaderPerfil.addEventListener('click', () => cambiarPestaña('perfil'));
    btnHeaderAyuda.addEventListener('click', () => cambiarPestaña('ayuda'));

// ==========================================
// 3. ESCÁNER Y EDICIÓN DE TICKETS
// ==========================================
    const dropzone = document.getElementById('zona-dropzone');
    const spinnerGemini = document.getElementById('spinner-gemini');
    const zonaValidacion = document.getElementById('zona-validacion');
    const seccionProcesamiento = document.getElementById('seccion-procesamiento');
    const cuerpoTabla = document.getElementById('cuerpo-tabla');
    const contenidoDropzone = document.getElementById('contenido-dropzone');
    
    const alertaError = document.getElementById('alerta-error');
    const textoAlertaError = document.getElementById('texto-alerta-error');
    
    let facturaMemoria = null; 

    dropzone.addEventListener('click', () => document.getElementById('input-archivo').click());

    document.getElementById('input-archivo').addEventListener('change', async (e) => {
        if (e.target.files.length > 0) {
            contenidoDropzone.classList.add('oculto');
            spinnerGemini.classList.remove('oculto');

            if (alertaError) alertaError.classList.add('oculto');
            
            const formData = new FormData();
            formData.append('ticket', e.target.files[0]);

            try {
                const res = await fetch(`${BASE_URL}/subir-factura`, {
                    method: 'POST',
                    body: formData
                });
                
                const datosReales = await res.json();
                
                if(res.ok) {
                    spinnerGemini.classList.add('oculto'); 
                    seccionProcesamiento.classList.add('oculto');
                    facturaMemoria = datosReales;
                    
                    cuerpoTabla.innerHTML = '';
                    datosReales.productos.forEach(prod => {
                        cuerpoTabla.innerHTML += `
                            <tr>
                                <td contenteditable="true">${prod.nombre}</td>
                                <td contenteditable="true">${prod.cantidad}</td>
                                <td contenteditable="true">${prod.precio_ud}</td>
                                <td contenteditable="true">${datosReales.comercio}</td>
                            </tr>`;
                    });
                    
                    zonaValidacion.classList.remove('oculto');
                } else {

                    spinnerGemini.classList.add('oculto');
                    contenidoDropzone.classList.remove('oculto');
                    
                    const detalleBackend = datosReales.detail || datosReales.mensaje_error || "";
                    let mensajeFinal = "";

                    switch (res.status) {
                        case 400: // Bad Request (ValueError / JSON inválido)
                            mensajeFinal = "Formato no válido o datos incorrectos. " + detalleBackend;
                            break;
                            
                        case 403: // Forbidden (PermissionError)
                            mensajeFinal = "🔒 Permiso denegado. Comprueba si el archivo Excel/CSV está abierto en tu ordenador y ciérralo.";
                            break;
                            
                        case 404: // Not Found (FileNotFoundError)
                            mensajeFinal = "Ruta no encontrada. " + detalleBackend;
                            break;
                            
                        case 409: // Conflict (FileExistsError - Nuestro duplicado)
                            mensajeFinal = "📑 ¡FACTURA DUPLICADA!";
                            break;
                            
                        case 500: // Internal Server Error (Exception)
                            mensajeFinal = "Error de servidor interno. " + detalleBackend;
                            break;
                            
                        default: // Cualquier otro caso
                            mensajeFinal = detalleBackend ? detalleBackend : "❌ Error desconocido al procesar el archivo.";
                            break;
                    }

                    textoAlertaError.textContent = mensajeFinal;
                    alertaError.classList.remove('oculto');

                    e.target.value = '';
                }
            } catch (err) {
                spinnerGemini.classList.add('oculto');
                contenidoDropzone.classList.remove('oculto');
                
                textoAlertaError.textContent = "❌ Error de red conectando con el servidor";
                alertaError.classList.remove('oculto');
                
                e.target.value = '';
            }
        }
    });

    document.getElementById('btn-nuevo').addEventListener('click', () => {
        facturaMemoria = null; 
        zonaValidacion.classList.add('oculto');
        seccionProcesamiento.classList.remove('oculto');
        document.getElementById('contenido-dropzone').classList.remove('oculto');
        document.getElementById('input-archivo').value = ''; 
    });

    document.getElementById('btn-guardar').addEventListener('click', async () => {
        if (!facturaMemoria) return;

        let superMercadoTicket = facturaMemoria.comercio;
        const filas = cuerpoTabla.querySelectorAll('tr');
        
        filas.forEach((fila, index) => {
            const celdas = fila.querySelectorAll('td');
            const nombreProd = celdas[0].innerText;
            const cantStr   = celdas[1].innerText.replace(',', '.');

            const subtotalStr = celdas[2].innerText.replace(',', '.'); 
            superMercadoTicket = celdas[3].innerText;
            
            const cantFloat   = parseFloat(cantStr) || 1;
            const subtotalFloat = parseFloat(subtotalStr) || 0;
            
            if (facturaMemoria.productos[index]) {
                facturaMemoria.productos[index].nombre = nombreProd;
                facturaMemoria.productos[index].cantidad = cantFloat.toString();
                facturaMemoria.productos[index].precio_total = subtotalFloat.toFixed(2);
            }
        });

        facturaMemoria.comercio = superMercadoTicket;

        const btnGuardar = document.getElementById('btn-guardar');
        btnGuardar.innerText = "Guardando...";
        btnGuardar.disabled = true;

        try {
            const res = await fetch(`${BASE_URL}/confirmar-factura`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(facturaMemoria)
            });

            if (res.ok) {
                mostrarToast(`¡Guardado! Total ticket: ${facturaMemoria.total_ticket}€`);
                document.getElementById('btn-nuevo').click();
                
                if (typeof cargarGastosTotalesCSV === "function") {
                    cargarGastosTotalesCSV(); 
                }
            }
        } catch (error) {
            console.error("Error al guardar:", error);
        } finally {
            btnGuardar.innerText = "Confirmar y Guardar";
            btnGuardar.disabled = false;
        }
    });

// ==========================================
// 4. LECTURA DE CSV Y GESTIÓN DEL HISTÓRICO
// ==========================================
    let baseDeDatosHistorico = []; 

    async function cargarGastosTotalesCSV() {
        try {
            const respuesta = await fetch('gastos_totales.csv');
            const textoCSV = await respuesta.text();
            
            const lineas = textoCSV.trim().split('\n');
            baseDeDatosHistorico = [];
            
            for (let i = 1; i < lineas.length; i++) {
                let linea = lineas[i].trim();
                if (!linea) continue;
                
                if (linea.startsWith('"') && linea.endsWith('"')) {
                    linea = linea.substring(1, linea.length - 1);
                    linea = linea.replace(/""/g, '"'); 
                }

                const columnas = linea.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);

                if (columnas.length >= 6) {
                    const superMercado = columnas[0].replace(/"/g, '').trim();
                    const fechaCompleta = columnas[2].replace(/"/g, '').trim();
                    const fechaTxt = fechaCompleta.split(' ')[0].replace(/-/g, '/');
                    const producto = columnas[3].replace(/"/g, '').trim();
                    
                    const precioUdStr = columnas[5].replace(/"/g, '').replace(',', '.'); 
                    const precioTotalStr = columnas[6].replace(/"/g, '').replace(',', '.'); 

                    const precioFloat = parseFloat(precioUdStr);
                    const totalLineaFloat = parseFloat(precioTotalStr);

                    if (!isNaN(precioFloat)) {
                        baseDeDatosHistorico.push({
                            fecha: fechaTxt,
                            super: superMercado,
                            producto: producto,
                            precioUd: precioFloat.toFixed(2), 
                            precio: isNaN(totalLineaFloat) ? precioFloat : totalLineaFloat
                        });
                    }
                }
            }

            if (!document.getElementById('vista-historico').classList.contains('oculto')) {
                renderizarHistorico(baseDeDatosHistorico);
            }

            if (!document.getElementById('vista-finanzas').classList.contains('oculto')) {
                inicializarFinanzas();
            }

        } catch (error) {
            console.error("No se pudo cargar el archivo CSV", error);
        }
    }

    function renderizarHistorico(datos) {
        const cuerpo = document.getElementById('cuerpo-historico');
        if(!cuerpo) return;
        
        if (datos.length === 0) {
            cuerpo.innerHTML = `<tr><td colspan="4" style="text-align:center;">No se han encontrado resultados</td></tr>`;
            return;
        }

        cuerpo.innerHTML = datos.map(item => `
            <tr>
                <td>${item.fecha}</td>
                <td style="color:var(--facil-green); font-weight:600">${item.super}</td>
                <td>${item.producto}</td>
                <td style="font-weight:600">${item.precioUd} €</td>
            </tr>
        `).join('');
    }

    async function ejecutarBusquedaHistorico() {
        const inputBuscador = document.getElementById('buscador-historico');
        const texto = inputBuscador.value.trim();

        if (!texto) {
            renderizarHistorico(baseDeDatosHistorico);
            return;
        }

        try {a
            const res = await fetch(`${BASE_URL}/buscar-articulo`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ articulo: texto })
            });

            const data = await res.json();
            
            if (data.resultados) {
                const datosFormateados = data.resultados.map(item => ({
                    fecha: item.fecha,
                    super: item.super,
                    producto: item.nombre,
                    precioUd: item.precio_ud.toFixed(2)
                }));

                renderizarHistorico(datosFormateados);
            } else if (data.error) {
                console.error("Error del servidor:", data.error);
                mostrarToast("Error en la búsqueda");
            }
        } catch (error) {
            console.error("Error en búsqueda remota:", error);
            mostrarToast("Servidor de IA no disponible");
        }
    }

    // --- EVENTOS DE INTERACCIÓN ---

    // Botón de buscar
    const btnBuscarHistorico = document.getElementById('btn-buscar-historico');
    if (btnBuscarHistorico) {
        btnBuscarHistorico.addEventListener('click', ejecutarBusquedaHistorico);
    }

    // Tecla Enter en el campo de búsqueda
    const inputBuscador = document.getElementById('buscador-historico');
    if (inputBuscador) {
        inputBuscador.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                ejecutarBusquedaHistorico();
            }
        });
    }
    cargarGastosTotalesCSV();

// ==========================================
// 5. FINANZAS DINÁMICAS 
// ==========================================
    let ruletaChart = null;
    async function actualizarGraficoFinanzas() {
        const filtro = document.getElementById('filtro-fechas').value;
        const ctx = document.getElementById('ruletaGastos').getContext('2d');

        try {
            const respuesta = await fetch(`${BASE_URL}/get_grafico`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ periodo: filtro })
            });

            const respuestaJson = await respuesta.json();

            if (respuesta.ok && !respuestaJson.error) {
                const datosGrafico = respuestaJson.grafico; 
                const comercios = Object.keys(datosGrafico);
                const totales = Object.values(datosGrafico);

                if (ruletaChart) ruletaChart.destroy();        

                ruletaChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: comercios,
                        datasets: [{
                            data: totales,
                            backgroundColor: ['#117b3d', '#f29c11', '#71c055', '#222222', '#3498db', '#e74c3c']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom' } }
                    }
                });

                const gastoTotal = totales.reduce((acumulador, actual) => acumulador + actual, 0);            
                
                let superFavorito = "-";
                let maxGasto = 0;
                for (const [comercio, total] of Object.entries(datosGrafico)) {
                    if (total > maxGasto) {
                        maxGasto = total;
                        superFavorito = comercio;
                    }
                }

                document.getElementById('kpi-total').innerText = gastoTotal.toFixed(2) + " €";
                document.getElementById('kpi-super').innerText = superFavorito;

                const kpiTicketCaro = document.getElementById('kpi-ticket');
                if (kpiTicketCaro && respuestaJson.ticket_mas_caro) {
                    kpiTicketCaro.innerText = respuestaJson.ticket_mas_caro.toFixed(2) + " €";
                }

            } else {
                console.error("Error devuelto por el servidor:", respuestaJson.error);
                if (typeof mostrarToast === "function") {
                    mostrarToast("Error al cargar gráfica: " + respuestaJson.error);
                }
            }
        } catch (error) {
            console.error("Fallo de red al intentar obtener gráfico:", error);
        }
    }

    const btnAplicar = document.getElementById('btn-aplicar-filtro');
    if (btnAplicar) {
        btnAplicar.addEventListener('click', actualizarGraficoFinanzas);
    }

    function inicializarFinanzas() {
        actualizarGraficoFinanzas();
    }
    // ==========================================
    // 6. PERFIL 
    // ==========================================
    function actualizarDatosPerfil() {
        const token = localStorage.getItem('facilnanzas_token');
        const elementoEmail = document.getElementById('perfil-email');
        const elementoNombre = document.getElementById('perfil-nombre');
        if (!token || !elementoEmail || !elementoNombre) return;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            elementoEmail.innerText = payload.email;
            if (payload.nombre && payload.apellidos) {
                elementoNombre.innerText = payload.nombre + " " + payload.apellidos;
            } else if (payload.nombre) {
                elementoNombre.innerText = payload.nombre;
            } else {
                const pre = payload.email.split('@')[0];
                elementoNombre.innerText = pre.charAt(0).toUpperCase() + pre.slice(1);
            }
        } catch (e) { console.error("Error cargando perfil"); }
    }

    function mostrarToast(msg) {
        const t = document.createElement('div'); t.className='toast'; t.innerHTML=`<span>✅</span> ${msg}`;
        document.getElementById('toast-container').appendChild(t);
        setTimeout(() => t.remove(), 3000);
    }
    cargarGastosTotalesCSV();
});