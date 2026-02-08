<h1>DIRECTORIOS</h1>

**api**: Endpoints de la API  
**core**: Configuración de la app y loggings  
**db**: Configuraciones y modelos para la base de datos  
**middelware**: Contiene componentes que se ejecutan en todas las peticiones (contexto, logs, auditoría, etc)  
**models**: DSL (Domain-Specific Language): estructura declarativa que permite definir reglas de alerta sin necesidad de código.  
**orchestrator**: LLM orquestador que se encarga de llamar a tool calls u otros LLMs  
**storage**: Base de datos SLQLite para auditoría  
**tools**: Herramientas para cada caso de uso  


<h1>DOCKER</h1>

De momento se levantan 3 servicios.
* **postgress**: Base de datos principal con persistencia en volumen y healthcheck (verificación funcionamiento del servicio).
* **redis**: Almacenamiento en memoria para caché o mensajería, con persistencia AOF (Append Only File).
* **pgadmin**: Interfaz web para administrar PostgreSQL desde el navegador

<h3>Ejecución</h3>
1. Arrancar Docker Desktop  
2. Situarnos en la carpeta phishing-detect
3. Levantar los sercicios con ```docker compose up -d```
4. Comprobamos con ```docker compose ps``` que los servicios estan activos

