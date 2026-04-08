.PHONY: setup dev start test lint clean

setup:
	@echo "==> Configurando backend..."
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "==> Configurando frontend..."
	cd frontend && npm ci
	@echo "==> Setup completo!"

dev:
	@echo "==> Iniciando em modo desenvolvimento..."
	@bash scripts/dev.sh

start:
	@echo "==> Build frontend + start backend..."
	cd frontend && npm run build
	cd backend && . venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000

test:
	cd backend && . venv/bin/activate && python -m pytest

lint:
	cd backend && . venv/bin/activate && python -m ruff check app/
	cd frontend && npx tsc --noEmit

clean:
	rm -rf backend/venv backend/__pycache__ backend/app/__pycache__
	rm -rf frontend/node_modules frontend/dist
