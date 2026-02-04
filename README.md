# Proyecto Júpiter - Phishing Detect IA

## Máster en IA, Cloud Computing & DevOps - PontIA.tech**

### Autores

- Jose Antonio González Alcántara - <jagascripts@gmail.com>
- Enrique Cogolludo Fernández - <enriquecogolludoglvz@gmail.com>
- Julián García Campos - <juliusgc@msn.com>

---

## 📋 Descripción General

API REST para gestión y análisis de reputación de dominios mediante integración con servicios externos (VirusTotal, Urlscan). Permite crear, actualizar, listar y eliminar dominios, consultar su reputación automáticamente y calcular un score de confianza.

## 🎯 Funcionalidades

- CRUD completo de dominios con persistencia en SQLite
- Consulta automática de reputación en VirusTotal y Urlscan
- Cálculo de score de reputación agregado
- Consulta DNS (IP, registros MX)
- Filtrado por estado, score y disponibilidad de servidor de correo
- Sistema de etiquetado
- Logging estructurado (consola, debug, warnings)

## 📁 Estructura del Proyecto

```bash
proyecto-jupiter-phising-detect/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuración centralizada
│   ├── logging_config.py      # Configuración de logging
│   ├── database.py            # Conexión a BD
│   ├── models.py              # Modelos SQLAlchemy
│   ├── schemas.py             # Modelos Pydantic (validación)
│   ├── crud.py                # Operaciones de BD
│   ├── servicios_ext.py       # Integraciones externas (VT, Urlscan, DNS)
│   ├── main.py                # Aplicación FastAPI
│   ├── requirements.txt       # Dependencias de ejecución
│   └── requirements-dev.txt   # Dependencias de desarrollo
├── tests/
│   └── test_api_dominios.py   # Suite de tests con pytest
├── docs/
│   └── Enunciado Proyecto Jupyter.pdf
├── .env.example               # Plantilla de variables de entorno
├── .gitignore
├── LICENSE
└── README.md
```

## 🛠️ Tecnologías Utilizadas

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI
- **dnspython** - Consultas DNS
- **requests** - Cliente HTTP
- **pytest** - Testing

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/proyecto-jupiter-phising-detect.git
cd proyecto-jupiter-phising-detect
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate # Linux/macOS
```

### 3. Instalar dependencias

```bash
cd app
pip install -r requirements.txt
```

Para desarrollo (incluye pytest):

```bash
pip install -r requirements-dev.txt
```

### 4. Configurar variables de entorno

Copiar `.env.example` a `.env` y añadir las API keys:

```bash
cp ..\.env.example .env
```

Editar `.env`:

```env
API_KEY_VT=tu_api_key_virustotal
API_URLSCAN=tu_api_key_urlscan
DATABASE_URL=sqlite:///./dominios.db
API_TIMEOUT=6
LOG_DIR=logs
```

### 5. Ejecutar la API

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

La API estará disponible en `http://localhost:8080`

Documentación interactiva: `http://localhost:8080/docs`

### 6. Ejecutar tests

```bash
cd ..
pytest tests/ -v
```

O ejecutar el script de pruebas manual:

```bash
cd tests
python test_api_dominios.py
```

## 📚 Endpoints Principales

### Crear dominio

```http
POST /dominio
Content-Type: application/json

{
  "nombre": "example.com",
  "etiquetas": ["phishing", "sospechoso"]
}
```

### Listar todos los dominios

```http
GET /dominios
```

### Obtener dominio específico

```http
GET /dominio/{nombre_dominio}
```

### Actualizar dominio

```http
PATCH /dominio/{nombre_dominio}
Content-Type: application/json

{
  "estado_dominio": "Malicioso",
  "etiquetas": ["c2"],
  "fuentes_reputacion": [{"manual": 85}]
}
```

### Filtrar por estado

```http
GET /dominios/estado/{estado}
```

Estados válidos: `Limpio`, `Sospechoso`, `Malicioso`, `Desconocido`

### Filtrar por score

```http
GET /dominios/reputacion/{score}
```

Devuelve dominios con score **menor** al indicado.

### Filtrar por MX

```http
GET /dominios/mx/{tiene_mx}
```

Valores: `true` o `false`

### Eliminar dominio

```http
DELETE /dominio/{nombre_dominio}
```

## 📊 Modelo de Datos

### Dominio

- `nombre` (str, PK) - Dominio (FQDN)
- `ip_actual` (str) - IP actual
- `tiene_mx` (bool) - ¿Tiene servidor de correo?
- `estado_dominio` (Enum) - Limpio | Sospechoso | Malicioso | Desconocido
- `etiquetas` (list[str]) - Etiquetas personalizadas
- `fuentes_reputacion` (list[dict]) - Scores por fuente
- `score` (int) - Score promedio agregado
- `creado_el` (datetime)
- `modificado_el` (datetime)

## 🔒 Notas de Seguridad

- No subir el archivo `.env` al repositorio
- Las API keys deben mantenerse privadas
- Los logs pueden contener información sensible

## 📖 Referencias

- [FastAPI](https://fastapi.tiangolo.com/)
- [VirusTotal API](https://developers.virustotal.com/)
- [Urlscan.io API](https://urlscan.io/docs/api/)

---

**Estado del Proyecto:** ✅ **EN DESARROLLO**
