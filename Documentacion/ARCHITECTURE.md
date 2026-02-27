# Arquitectura Técnica y Ecosistema de Servicios - Proyecto Jupiter Phishing Detect

Este documento define la arquitectura técnica actual, la estrategia de empaquetado y el flujo de trabajo del ecosistema "Phishing Detect", desarrollado para el Máster en IA, Cloud Computing & DevOps.

## 1. Visión General: Arquitectura de Microservicios

El sistema implementa una arquitectura de microservicios distribuidos, altamente desacoplados y orientados al dominio, orquestados mediante **Docker Compose** para los entornos de desarrollo local y despliegue.

*   **Modelo de Integración:** APIs RESTful síncronas y eventos asíncronos (soporte vía Redis).
*   **Gestión del Ecosistema:** Orquestación centralizada a través de un repositorio "paraguas" (Umbrella Repository) apoyado en Git Submodules.
*   **Persistencia:** Infraestructura de datos compartida gestionada vía contenedores (PostgreSQL y Redis).

## 2. Estrategia de Repositorios Estructurados (`.gitmodules`)

El proyecto ha evolucionado de una estructura monolítica a un modelo modular gestionado por **Git Submodules**. Esta decisión arquitectónica se materializa en el archivo `.gitmodules` y separa físicamente el código fuente en repositorios independientes.

### Justificación de la Arquitectura basada en Submódulos

1.  **Desacoplamiento del Ciclo de Vida:** Cada microservicio tiene su propio control de versiones, pipeline de CI/CD (GitHub Actions) y ritmo de despliegue. Un fallo en la pipeline de un servicio no bloquea al resto del equipo.
2.  **Aislamiento de Dominios:** Obliga a mantener fronteras claras de dominio (Bounded Contexts). Es imposible introducir acoplamiento oculto entre base de código de diferentes servicios sin hacerlo a través de interfaces explícitas.
3.  **Gestión de Dependencias (El `Shared Kernel`):** Al extraer el código común en `lib-shared-kernel`, este puede ser versionado como una dependencia más, asegurando integridad en los contratos HTTP y modelos de datos.

### Topología de Submódulos

El ecosistema principal se compone de los siguientes submódulos:

| Componente                   | Tipo          | Descripción                                                                                                          |
| :--------------------------- | :------------ | :------------------------------------------------------------------------------------------------------------------- |
| `services/srv-orchestrator`  | Microservicio | Actúa como API Gateway / Orquestador central, enrutando tráfico y componiendo respuestas para los frontends.         |
| `services/srv-reputation`    | Microservicio | Encargado de analizar y determinar la reputación de las URLs y metadatos extraídos.                                  |
| `services/srv-knowledge-rag` | Microservicio | Implementa el sistema RAG (Retrieval-Augmented Generation) integrando modelos de IA para análisis de phishing.       |
| `services/lib-shared-kernel` | Librería      | Contratos, esquemas globales, utilidades de seguridad y formateo de respuestas reutilizables por todos los backends. |
| `frontends/fnd-chatbot`      | Frontend      | Interfaz de usuario conversacional (Chatbot) orientada al usuario final.                                             |

### Operativa Básica (Git Submodules)

Para trabajar en el entorno, el desarrollador debe sincronizar los submódulos:

```bash
# Clonar por primera vez con submódulos
git clone --recurse-submodules <url-del-repo-principal>

# Actualizar submódulos si ya se clonó previamente
git submodule update --init --recursive
```

## 3. Arquitectura Interna de Microservicios ("The Golden Rule")

Para garantizar coherencia y mantenibilidad, cada repositorio de backend implementa una estructura inspirada en la **Arquitectura Hexagonal (Puertos y Adaptadores)**:

```text
src/
├── controllers/    # Rutas y Endpoints (Capa de Presentación / API)
├── services/       # Lógica de Negocio Pura (Capa de Dominio / Core)
├── models/         # Definición de Entidades ORM (Capa de Datos)
└── schemas/        # Contratos DTO de entrada y salida (Pydantic)
```

> **Regla Inquebrantable:** Los `controllers` no contienen lógica de negocio. Se limitan a validar el acceso, delegar el trabajo al servicio correspondiente y estructurar la respuesta HTTP correspondientes.

## 4. Infraestructura Core y Backing Services

El orquestador de infraestructura principal es el archivo `docker-compose.yml` del repositorio central, el cual define los *backing services* necesarios para el funcionamiento del ecosistema. En lugar de embeber las bases de datos en los repositorios de los servicios individuales, se centraliza su despliegue:

*   **PostgreSQL 16 (`postgres-phishing`):** Base de datos relacional principal.
*   **Redis 7 (`redis-phishing`):** Almacén clave-valor en memoria. Usado para caché veloz, sesión de usuarios o enrutamiento de pub/sub.
*   **PgAdmin 4 (`pgadmin-phishing`):** Interfaz web de consola para administración local de la base de datos de manera visual (Puerto HTTP 5050).

## 5. Flujo de Integración Continua (CI/CD)

1.  **Desarrollo Focado:** Las *features* tecnológicas se implementan en ramas designadas (`feature/...`) dentro del propio repo del submódulo.
2.  **Validación de Submódulos:** Cada PR creada dentro del submódulo activa su propia Pipeline de CI validando sus Unidades Funcionales (Tests y Linters).
3.  **Integración en Umbrella:** Tras integrar satisfactoriamente una funcionalidad a un microservicio, se levanta una PR en este repositorio principal referenciando el avance del submodulo, documentando la cohesión del sistema global sin colisiones.
