# Makefile para facilitar comandos Docker

.PHONY: help build up down logs restart clean test health

help:  ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build:  ## Construir todas las imágenes Docker
	docker-compose build

up:  ## Levantar todos los servicios
	docker-compose up -d

down:  ## Detener todos los servicios
	docker-compose down

logs:  ## Ver logs de todos los servicios
	docker-compose logs -f

restart:  ## Reiniciar todos los servicios
	docker-compose restart

clean:  ## Detener servicios y eliminar volúmenes (¡BORRA LA BD!)
	docker-compose down -v

test:  ## Ejecutar tests
	pytest tests/ -v

health:  ## Verificar health de servicios
	@echo "Gateway:"
	@curl -s http://localhost/health | python -m json.tool
	@echo "\nDNS Service:"
	@curl -s http://localhost:8001/health | python -m json.tool
	@echo "\nReputation Service:"
	@curl -s http://localhost:8002/health | python -m json.tool
	@echo "\nDomain CRUD:"
	@curl -s http://localhost:8003/health | python -m json.tool

ps:  ## Ver estado de contenedores
	docker-compose ps

stats:  ## Ver uso de recursos
	docker stats --no-stream

redis-cli:  ## Conectar a Redis CLI
	docker exec -it phising-redis redis-cli

psql:  ## Conectar a PostgreSQL
	docker exec -it phising-postgres psql -U postgres -d dominios
