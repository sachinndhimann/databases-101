# Database Engineering 101 — convenience commands
# Usage: make <target>

.PHONY: up down logs psql mysql redis-cli seed-ch1 clean venv install

up:
	docker compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 5
	docker compose ps

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker compose down -v

venv:
	python3 -m venv .venv
	@echo "Run: source .venv/bin/activate"

install:
	pip install -r requirements.txt

psql:
	docker exec -it db101-postgres psql -U $${POSTGRES_USER:-db101} -d $${POSTGRES_DB:-db101}

mysql:
	docker exec -it db101-mysql mysql -u $${MYSQL_USER:-db101} -p$${MYSQL_PASSWORD:-db101pass} $${MYSQL_DATABASE:-db101}

redis-cli:
	docker exec -it db101-redis redis-cli

seed-ch1:
	docker exec -i db101-postgres psql -U $${POSTGRES_USER:-db101} -d $${POSTGRES_DB:-db101} < chapter1/sql/setup.sql
	docker exec -i db101-postgres psql -U $${POSTGRES_USER:-db101} -d $${POSTGRES_DB:-db101} < chapter1/sql/seed.sql
