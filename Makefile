.PHONY: help up down dev logs build clean train init

help:
	@echo "Federated Learning Swipe Keyboard"
	@echo ""
	@echo "Commands:"
	@echo "  make init      - Initialize git submodules"
	@echo "  make up        - Start full system (with server)"
	@echo "  make dev       - Start dev mode (client only)"
	@echo "  make down      - Stop all containers"
	@echo "  make logs      - Show logs"
	@echo "  make build     - Rebuild containers"
	@echo "  make clean     - Remove all containers and volumes"
	@echo "  make train     - Run training in container"
	@echo "  make status    - Check status"

init:
	@echo "Initializing git submodules..."
	git submodule update --init --recursive
	@echo "✅ Submodules initialized!"

up: init
	docker-compose up -d
	@echo ""
	@echo "✅ System started!"
	@echo "Frontend: http://localhost:3000/demo/index.html"
	@echo "API: http://localhost:8000"
	@echo "MinIO: http://localhost:9001 (admin/admin12345)"

dev: init
	docker-compose -f docker-compose.dev.yml up -d
	@echo ""
	@echo "✅ Dev mode started!"
	@echo "Frontend: http://localhost:3000/demo/index.html"
	@echo "API: http://localhost:8000"

down:
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

logs:
	docker-compose logs -f

build:
	docker-compose build

clean:
	docker-compose down -v
	docker-compose -f docker-compose.dev.yml down -v
	@echo "✅ Cleaned up!"

train:
	docker exec -it fl-client python scripts/federated_cycle.py

status:
	@echo "Container status:"
	@docker-compose ps
	@echo ""
	@echo "Health checks:"
	@curl -s http://localhost:8000/health || echo "Client: Not running"
	@echo ""
