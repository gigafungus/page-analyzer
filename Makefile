setup: install build-css

install:
	uv sync
	npm ci

build-css:
	npm run build:css

dev:
	uv run flask --debug --app page_analyzer:app run

watch:
	npx tailwindcss --input assets/css/source.css --output page_analyzer/static/css/main.css --watch

lint:
	uv run ruff check

fix:
	uv run ruff check --fix

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

-include .env
export
dbsetup:
	psql "$(DATABASE_URL)" -f database.sql