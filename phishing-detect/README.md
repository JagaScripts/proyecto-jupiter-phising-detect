<h1>DIRECTORIOS</h1>

**api**: Endpoints de la API
**core**: Configuración de la app y loggings
**db**: Configuraciones y modelos para la base de datos
**middelware**: Contiene componentes que se ejecutan en todas las peticiones (contexto, logs, auditoría, etc)
**models**: DSL (Domain-Specific Language): estructura declarativa que permite definir reglas de alerta sin necesidad de código.
**orchestrator**: LLM orquestador que se encarga de llamar a tool calls u otros LLMs
**storage**: Base de datos SLQLite para auditoría
**tools**: Herramientas para cada caso de uso