// ==============================================================================================================================
                                                        //  COMANDO INICIO: node server.js
// ==============================================================================================================================
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const cors = require('cors');

const sqlite3 = require('sqlite3');
const { open } = require('sqlite');
const multer = require('multer');
const axios = require('axios');
const upload = multer({ storage: multer.memoryStorage() });
const app = express();

const IP_SERVIDOR = '192.168.1.36';

app.use(express.json()); 
app.use(cors());         

const SECRETO_JWT = "MiSuperSecretoFaciLnanzas2026";
let db; 
// ==========================================
// 1. ARRANCAR LA BASE DE DATOS SQLITE
// ==========================================
async function iniciarBaseDeDatos() {
    db = await open({
        filename: './database.db',
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    `);
    console.log("✅ Base de datos SQLite lista y conectada.");
}
iniciarBaseDeDatos();

// ==========================================
// 2. RUTA PARA REGISTRARSE
// ==========================================
app.post('/registro', async (req, res) => {
    try {
        const { email, password } = req.body;
        
        const passwordHasheada = await bcrypt.hash(password, 10);

        try {
            await db.run(
                'INSERT INTO usuarios (email, password) VALUES (?, ?)', 
                [email, passwordHasheada]
            );
            res.status(201).json({ mensaje: "Usuario registrado con éxito." });
        } catch (dbError) {
            if (dbError.code === 'SQLITE_CONSTRAINT') {
                return res.status(400).json({ mensaje_error: "Este correo ya está registrado." });
            }
            throw dbError; 
        }
    } catch (error) {
        res.status(500).json({ mensaje_error: "Error del servidor." });
    }
});

// ==========================================
// 3. RUTA PARA INICIAR SESIÓN (MODO DETECTIVE)
// ==========================================
app.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        console.log(`\n🕵️ INFORMACIÓN: Alguien intenta entrar con el email: "${email}"`);

        const usuario = await db.get('SELECT * FROM usuarios WHERE email = ?', [email]);
        
        if (!usuario) {
            console.log("❌ ERROR: No he encontrado ese email en la base de datos.");
            return res.status(400).json({ mensaje_error: "Correo o contraseña incorrectos." });
        }
        console.log("✅ ÉXITO: Usuario encontrado en la base de datos. Su ID es:", usuario.id);

        const contraseñaCorrecta = await bcrypt.compare(password, usuario.password);
        if (!contraseñaCorrecta) {
            console.log("❌ ERROR: La contraseña escrita NO coincide con el hash guardado.");
            return res.status(400).json({ mensaje_error: "Correo o contraseña incorrectos." });
        }
        console.log("✅ ÉXITO: La contraseña es correcta.");

        const token = jwt.sign(
            { idUsuario: usuario.id, email: usuario.email },
            SECRETO_JWT,
            { expiresIn: '2h' }
        );

        res.status(200).json({ mensaje: "Login correcto", token: token });

    } catch (error) {
    if (error.response) {
        // Python recibió la llamada pero respondió con un error (ej. 404 o 500)
        console.error("❌ Python respondió con error:", error.response.status, error.response.data);
        res.status(error.response.status).json({ error: "El motor de IA devolvió un error" });
    } else if (error.request) {
        // La llamada se hizo pero no hubo respuesta (Python está apagado o puerto bloqueado)
        console.error("❌ No se pudo contactar con Python. ¿Está encendido el servidor en el puerto 8000?");
        res.status(503).json({ error: "El motor de IA no responde" });
    } else {
        // Error al configurar la petición
        console.error("❌ Error de configuración:", error.message);
        res.status(500).json({ error: "Fallo interno en el servidor" });
    }
}
});

// ==========================================
// RUTA PARA SUBIR FACTURA                                                       
// ==========================================
app.post('/subir-factura', upload.single('ticket'), async (req, res) => {
    try {
        if (!req.file) return res.status(400).json({ error: "No hay imagen" });

        const URL_PYTHON = "http://127.0.0.1:8000/subir-factura";
        const formData = new FormData();
        const blob = new Blob([req.file.buffer], { type: req.file.mimetype });
        formData.append('ticket', blob, req.file.originalname);

        const respuesta = await axios.post(URL_PYTHON, formData);

        console.log("🤖 Respuesta de Python:", respuesta.data);

        if (respuesta.data.error) {
            return res.status(400).json({ detail: respuesta.data.error });
        }

        res.json(respuesta.data.resultado_python); 

    } catch (error) {
        if (error.response) {
            console.error(`❌ Python devolvió estado ${error.response.status}:`, error.response.data);
            return res.status(error.response.status).json(error.response.data);
            
        } else {
            console.error("❌ Fallo crítico de red en Node:", error.message);
            return res.status(500).json({ detail: "Fallo al conectar con el motor de IA" });
        }
    }
});

// ==========================================
// RUTA PARA CONFIRMAR Y GUARDAR FACTURA EN PYTHON
// ==========================================
app.post('/confirmar-factura', async (req, res) => {
    try {
        const facturaCorregida = req.body; 

        const URL_PYTHON = "http://127.0.0.1:8000/actualizar_factura"; 

        console.log("⏳ Enviando correcciones a Python...");

        const respuesta = await axios.post(URL_PYTHON, facturaCorregida, {
            headers: { 'Content-Type': 'application/json' }
        });

        console.log("✅ Python ha guardado la factura:", respuesta.data);

        res.status(200).json(respuesta.data);

    } catch (error) {
        console.error("❌ NODE DETECTÓ ERROR EN PYTHON:", error.response?.data || error.message);
        res.status(500).json({ error: "Fallo al confirmar los datos con la IA" });
    }
});

// ==========================================
// RUTA PARA OBTENER LOS DATOS DEL GRÁFICO
// ==========================================
app.post('/get_grafico', async (req, res) => {
    try {
        const URL_PYTHON = "http://127.0.0.1:8000/get_grafico"; 

        const respuesta = await axios.post(URL_PYTHON, req.body, {
            headers: { 'Content-Type': 'application/json' }
        });

        res.status(200).json(respuesta.data);

    } catch (error) {
        console.error("❌ NODE DETECTÓ ERROR AL PEDIR EL GRÁFICO:", error.message);
        res.status(500).json({ error: "Fallo al generar los datos del gráfico" });
    }
});

// ==========================================
// RUTA PARA BUSCAR ARTÍCULO ESPECÍFICO EN EL HISTÓRICO
// ==========================================
app.post('/buscar-articulo', async (req, res) => {
    try {
        const URL_PYTHON = "http://127.0.0.1:8000/buscar_articulo";

        const respuesta = await axios.post(URL_PYTHON, req.body);

        res.json(respuesta.data);

    } catch (error) {
        console.error("❌ ERROR AL BUSCAR ARTÍCULO:", error.message);
        res.status(500).json({ error: "No se pudo realizar la búsqueda en el motor de IA" });
    }
});

// ==========================================
// ARRANCAR EL SERVIDOR
// ==========================================
const PUERTO = 3000;
app.listen(PUERTO, '0.0.0.0', () => {
    console.log(`🚀 Servidor backend corriendo en http://${IP_SERVIDOR || 'localhost'}:${PUERTO}`);
});

