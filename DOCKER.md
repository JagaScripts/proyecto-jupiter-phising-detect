# Arquitectura de Microservicios - Proyecto Júpiter

## 🏗️ Arquitectura

```bash
┌─────────────────┐
│   Nginx :80     │ ← Reverse Proxy + Load Balancer
└────────┬────────┘
         │
┌────────▼────────┐
│ API Gateway     │ ← Orquestador de servicios
│   :8000         │
└────┬────────────┘
     │
     ├───────────┬─────────────┬────────────┐
     │           │             │            │
┌────▼────┐ ┌───▼──────┐ ┌───▼──────┐ ┌──▼─────┐
│ DNS     │ │Reputation│ │Domain    │ │Redis   │
│Service  │ │Service   │ │CRUD      │ │Cache   │
│ :8001   │ │ :8002    │ │ :8003    │ │ :6379  │
└─────────┘ └──────────┘ └────┬─────┘ └────────┘
                               │
                          ┌────▼──────┐
                          │PostgreSQL │
                          │  :5432    │
                          └───────────┘
```

## 📦 Microservicios

### 1. **API Gateway** (Puerto 8000)

- Punto de entrada único
- Orquesta llamadas a microservicios
- Maneja peticiones asíncronas
- Valida datos de entrada

### 2. **DNS Service** (Puerto 8001)

- Consultas DNS (IP, MX)
- Servicio ligero y rápido
- Sin dependencias externas pesadas

### 3. **Reputation Service** (Puerto 8002)

- Consultas a VirusTotal y Urlscan
- Cache con Redis (TTL 1 hora)
- Manejo de rate limits
- Timeouts configurables

### 4. **Domain CRUD** (Puerto 8003)

- Operaciones CRUD en PostgreSQL
- Gestión de estado de dominios
- Cálculo de scores
- Filtros y búsquedas

### 5. **PostgreSQL** (Puerto 5432)

- Base de datos principal
- Persistencia de dominios
- Reemplaza SQLite para producción

### 6. **Redis** (Puerto 6379)

- Cache de reputación
- Reduce llamadas a APIs externas
- Mejora rendimiento

### 7. **Nginx** (Puerto 80/443)

- Reverse proxy
- Rate limiting (10 req/s)
- Compresión gzip
- HTTPS (opcional)

## 🚀 Despliegue

### Requisitos previos

- Docker
- Docker Compose
- API Keys de VirusTotal y Urlscan

### Configuración

1. **Copiar variables de entorno**:

```bash
cp .env.example .env
```

2. **Editar `.env`** con tus API keys:

```env
API_KEY_VT=tu_api_key_virustotal
API_URLSCAN=tu_api_key_urlscan
API_TIMEOUT=6
```

3. **Construir y levantar servicios**:

```bash
docker-compose up --build
```

4. **Verificar servicios**:

```bash
# Health check general
curl http://localhost/health

# Servicios individuales
curl http://localhost:8000/health  # Gateway
curl http://localhost:8001/health  # DNS
curl http://localhost:8002/health  # Reputation
curl http://localhost:8003/health  # Domain CRUD
```

### Comandos útiles

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f api-gateway

# Reiniciar un servicio
docker-compose restart reputation-service

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (¡cuidado, borra la BD!)
docker-compose down -v

# Escalar un servicio
docker-compose up --scale reputation-service=3
```

## 📊 Endpoints

### A través de Nginx (Puerto 80)

```bash
http://localhost/                    - Bienvenida
http://localhost/health              - Health check
http://localhost/docs                - Documentación Swagger
http://localhost/dominio             - CRUD dominios
http://localhost/dominios            - Listar dominios
http://localhost/dominios/estado/... - Filtros
```

### Acceso directo a servicios (para desarrollo)

```bash
http://localhost:8000  - API Gateway
http://localhost:8001  - DNS Service
http://localhost:8002  - Reputation Service
http://localhost:8003  - Domain CRUD
```

## 🔧 Configuración Avanzada

### Habilitar HTTPS en Nginx

1. **Generar certificados autofirmados** (desarrollo):

```bash
cd nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem \
  -subj "/C=ES/ST=Madrid/L=Madrid/O=PontIA/CN=localhost"
```

2. **Descomentar sección HTTPS** en `nginx/nginx.conf`

3. **Reiniciar Nginx**:

```bash
docker-compose restart nginx
```

### Ajustar Rate Limiting

Editar `nginx/nginx.conf`:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=20r/s;
```

### Cambiar TTL del Cache Redis

Editar en `docker-compose.yml`:

```yaml
environment:
  CACHE_TTL: 7200  # 2 horas
```

## 🧪 Testing

### Tests de integración

```bash
# Asegurarse de que los servicios están levantados
docker-compose up -d

# Ejecutar tests
pytest tests/ -v

# O con el script manual
python tests/test_api_dominios.py
```

### Probar servicios individualmente

```bash
# DNS
curl http://localhost:8001/dns/google.com

# Reputation (requiere API keys)
curl http://localhost:8002/reputation/google.com

# CRUD
curl -X POST http://localhost:8003/dominios \
  -H "Content-Type: application/json" \
  -d '{"nombre": "example.com", "etiquetas": ["test"]}'
```

## 📈 Monitoreo

### Ver estado de contenedores

```bash
docker-compose ps
```

### Ver uso de recursos

```bash
docker stats
```

### Acceder a logs de PostgreSQL

```bash
docker-compose logs postgres
```

### Conectar a PostgreSQL

```bash
docker exec -it phising-postgres psql -U postgres -d dominios
```

### Conectar a Redis CLI

```bash
docker exec -it phising-redis redis-cli

# Ver todas las keys
KEYS *

# Ver contenido de cache
GET reputation:google.com
```

## 🐛 Troubleshooting

### Servicios no levantan

```bash
# Ver logs detallados
docker-compose logs --tail=100

# Reconstruir imágenes
docker-compose build --no-cache

# Limpiar volúmenes y reiniciar
docker-compose down -v
docker-compose up --build
```

### PostgreSQL no acepta conexiones

```bash
# Verificar que el contenedor está healthy
docker-compose ps

# Esperar a que termine de inicializar
docker-compose logs postgres | grep "ready to accept connections"
```

### Redis desconectado

```bash
# Verificar conexión
docker exec -it phising-redis redis-cli ping

# Reiniciar Redis
docker-compose restart redis
```

### APIs externas fallan

- Verificar que las API keys están correctamente configuradas en `.env`
- Revisar logs del reputation-service
- Verificar conectividad a Internet desde el contenedor

## 🎓 Ventajas de esta Arquitectura

✅ **Escalabilidad**: Cada servicio se escala independientemente  
✅ **Resiliencia**: Un fallo no tumba todo el sistema  
✅ **Mantenibilidad**: Código separado por responsabilidades  
✅ **Performance**: Cache reduce latencia de APIs externas  
✅ **Producción-ready**: PostgreSQL, Redis, Nginx configurados  
✅ **Observabilidad**: Logs centralizados y health checks  

## 📝 Notas para el TFM

- Arquitectura basada en principios de microservicios
- Patrón API Gateway para orquestación
- Cache distribuido con Redis
- Base de datos relacional PostgreSQL
- Proxy reverso Nginx con rate limiting
- Contenerización completa con Docker
- Orquestación con Docker Compose
- Health checks y reinicio automático
- Preparado para despliegue en cloud (AWS ECS, GCP Cloud Run, Azure Container Apps)
