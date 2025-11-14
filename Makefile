.PHONY: setup dev build edge logs db shell tests migrate

setup:
	pip install -r aurumai-api/requirements.txt

dev:
	uvicorn aurumai-api.app.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-rebuild:
	docker compose down -v
	docker compose up --build -d

logs:
	docker compose logs -f api

edge:
	docker exec -it aurumai_edge bash

api-shell:
	docker exec -it aurumai_api bash

tests:
	pytest -q

migrate:
	alembic upgrade head

makemigration:
	alembic revision --autogenerate -m "$(msg)"

db:
	docker exec -it aurumai_db psql -U aurumai -d aurumai

tree:
	tree -L 3 .

lint:
	ruff aurumai-api

format:
	ruff aurumai-api --fix

