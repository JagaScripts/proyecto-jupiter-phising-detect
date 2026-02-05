# Arquitectura Técnica y Flujo de Trabajo - Proyecto Jupiter Phishing Detect

Este documento define los estándares arquitectónicos, la estrategia de desarrollo y el flujo de trabajo para el equipo del proyecto "Phishing Detect". 

## 1. Visión General: Arquitectura de Microservicios

El sistema sigue una arquitectura de microservicios distribuidos, orquestados mediante **Docker Compose** para desarrollo local y despliegue.

*   **Patrón:** API Gateway (Nginx) + Servicios Especializados.
*   **Comunicación:** REST (HTTP) interna entre servicios.
*   **Persistencia:** Servicios desacoplados, aunque inicialmente soportados por una infraestructura de datos compartida (PostgreSQL/Redis) facilitada mediante contenedores.

## 2. Estandarización de Microservicios ("The Golden Rule")

Para garantizar la mantenibilidad y permitir que cualquier miembro del equipo trabaje en cualquier servicio sin fricción, **todos** los microservicios deben seguir estrictamente la **Arquitectura Hexagonal (Puertos y Adaptadores)** simplificada:

```text
nombre-servicio/
├── app/
│   ├── controllers/    # Rutas y Endpoints (API Layer)
│   ├── services/       # Lógica de Negocio Pura (Core)
│   ├── models/         # Definición de Datos / ORM (Data Layer)
│   └── schemas/        # Contratos de Datos (Pydantic/DTOs)
├── tests/              # Tests Unitarios e Integración específicos
├── Dockerfile          # Definición de construcción optimizada
└── requirements.txt    # Dependencias específicas
```

> **Regla:** No se permite lógica de negocio en los controladores. Los controladores solo orquestan y llaman a servicios.

## 3. Estrategia Monorepo: Código Compartido

Adoptamos un enfoque de **Monorepo** para agilizar el desarrollo colaborativo en esta fase académica.

### La Carpeta `services/shared`
Todo código que deba ser reutilizado por más de un microservicio (ej: logs estandarizados, modelos base de respuesta, utilidades de seguridad) residirá en:

`services/shared/`

*   **Manejo:** Esta carpeta se trata como una "librería interna".
*   **Integración:** En tiempo de construcción (Docker build), esta carpeta se copia dentro de cada contenedor para asegurar que todos usen la misma versión de las utilidades sin necesidad de gestionar paquetes PyPI privados.

## 4. Flujo de Trabajo Git (GitFlow Simplificado)

Nuestro árbol de trabajo se estructura para garantizar la estabilidad de la integración continua.

### Ramas Principales
*   **`main`**: Producción estable. Intocable directamente.
*   **`develop`**: Rama de integración. Aquí convergen las features terminadas.

### Ramas de Trabajo
*   **`feature/nombre-funcionalidad`**: Para nuevo desarrollo. Nace de `develop` y se mezcla en `develop`.
*   **`fix/descripcion-error`**: Para correcciones de errores.

### Integración (Pull Requests & Gatekeeping)
La integración de código se realiza **exclusivamente mediante Pull Requests (PR)**.
*   **Bloqueo Automático:** Se han configurado **Git Workflows** que ejecutan tests automáticos al crear una PR.
    *   🛑 Si los tests fallan, el botón de "Merge" se deshabilita.
    *   ✅ Solo código verificado entra en `develop` o `main`.

## 5. Infraestructura y DevOps

*   **Docker Compose:** Es la fuente de verdad para levantar el entorno. Cada desarrollador puede levantar el sistema completo con `docker-compose up`.
*   **Nginx Gateway:** Centraliza el acceso. No exponemos puertos de microservicios individuales innecesariamente; todo pasa por el Gateway.

---
*Documento aprobado para referencia del equipo de desarrollo.*
