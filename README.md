# Proyecto Júpiter - Phishing Detect IA

## Máster en IA, Cloud Computing & DevOps - PontIA.tech

### Autores

- Jose Antonio González Alcántara - <jagascripts@gmail.com>
- Enrique Cogolludo Fernández - <enriquecogolludoglvz@gmail.com>
- Julián García Campos - <juliusgc@msn.com>

---

## 📋 Descripción General

**Arquitectura de microservicios** para gestión y análisis de reputación de dominios. Sistema escalable y resiliente con servicios independientes para DNS, reputación, CRUD de dominios, cache distribuido (Redis) y base de datos (PostgreSQL). API Gateway orquesta las peticiones y Nginx actúa como reverse proxy.

**Características principales**: Contenerización completa con Docker, cache inteligente, alta disponibilidad, monitoreo y health checks.

## 🎯 Funcionalidades

- CRUD completo de dominios con persistencia en PostgreSQL
- Consulta automática de reputación en VirusTotal y Urlscan (con cache Redis)
- Cálculo de score de reputación agregado
- Consulta DNS (IP, registros MX)
- Filtrado por estado, score y disponibilidad de servidor de correo
- Sistema de etiquetado
- Logging estructurado y health checks por servicio
- Orquestación con Docker Compose + Nginx (reverse proxy)

## 📁 Estructura del Proyecto

```bash
proyecto-jupiter-phising-detect/
├── services/                   # Microservicios
│   ├── api-gateway/           # API Gateway (Puerto 8000)
│   ├── dns-service/           # Servicio DNS (Puerto 8001)
│   ├── reputation-service/    # Servicio Reputación (Puerto 8002)
│   └── domain-crud/           # Servicio CRUD (Puerto 8003)
├── shared/                    # Código compartido
├── nginx/                     # Configuración Nginx
├── app/                       # Código monolítico legacy
├── tests/                     # Tests
├── docs/                      # Documentación
├── docker-compose.yml         # Orquestación de servicios
├── .env.example               # Plantilla de variables de entorno
├── DOCKER.md                  # Guía de Docker
├── Makefile                   # Comandos útiles
└── README.md
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web para microservicios
- **SQLAlchemy** - ORM para PostgreSQL
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI
- **httpx** - Cliente HTTP asíncrono

### Infraestructura
- **Docker** - Contenerización
- **Docker Compose** - Orquestación multi-contenedor
- **PostgreSQL** - Base de datos relacional
- **Redis** - Cache distribuido
- **Nginx** - Reverse proxy y load balancer

### Integraciones
- **dnspython** - Consultas DNS
- **VirusTotal API** - Análisis de reputación
- **Urlscan.io API** - Análisis de URLs

### Testing & CI/CD
- **pytest** - Testing
- **GitHub Actions** - CI/CD
- **ruff** - Linting y formatting

## 🚀 Instalación y Ejecución

### Opción A: Docker (Recomendado - Arquitectura de Microservicios)

#### Requisitos previos
- Docker
- Docker Compose

#### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/proyecto-jupiter-phising-detect.git
cd proyecto-jupiter-phising-detect
```

#### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus API keys:

```env
API_KEY_VT=tu_api_key_virustotal
API_URLSCAN=tu_api_key_urlscan
```

#### 3. Levantar servicios

```bash
docker-compose up --build
```

#### 4. Verificar que todo funciona

```bash
curl http://localhost/health
```

**URLs disponibles:**
- API: `http://localhost` (vía Nginx)
- Documentación: `http://localhost/docs`
- Gateway directo: `http://localhost:8000`

**Ver documentación completa de Docker**: [DOCKER.md](DOCKER.md)

---

### Opción B: Ejecución Local (Desarrollo)

#### 1. Crear entorno virtual

```bash
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate # Linux/macOS
```

#### 2. Instalar dependencias

```bash
cd app
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 3. Configurar `.env` para local

```env
API_KEY_VT=tu_api_key_virustotal
API_URLSCAN=tu_api_key_urlscan
DATABASE_URL=sqlite:///./dominios.db
```

#### 4. Ejecutar la API monolítica

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

#### 5. Tests

```bash
cd ..
pytest tests/ -v
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
