.PHONY: help install run run-backend run-frontend docker-up docker-down clean db-init test lint

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install all dependencies"
	@echo "  make run          - Run both backend and frontend"
	@echo "  make run-backend  - Run backend only"
	@echo "  make run-frontend - Run frontend only"
	@echo "  make docker-up    - Run with Docker Compose"
	@echo "  make docker-down  - Stop Docker Compose"
	@echo "  make clean        - Clean up generated files"
	@echo "  make db-init      - Initialize database"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Run both services
run:
	@echo "Starting SMS Chat Application..."
	@if [ ! -f backend/.env ]; then \
		echo "Creating .env file from example..."; \
		cp backend/.env.example backend/.env; \
		echo "Please update backend/.env with your Twilio credentials"; \
	fi
	@echo "Starting backend and frontend..."
	make -j 2 run-backend run-frontend

# Run backend
run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend
run-frontend:
	cd frontend && npm start

# Docker commands
docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

docker-clean:
	docker-compose down -v
	docker system prune -f

# Database operations
db-init:
	cd backend && python -c "from app.db.database import engine, Base; Base.metadata.create_all(bind=engine)"

db-reset:
	@echo "Resetting database..."
	cd backend && python -c "from app.db.database import engine, Base; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
	@echo "Database reset complete!"

db-reset-with-demo: db-reset seed-demo
	@echo "Database reset with demo data complete!"

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.db" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf frontend/build
	rm -rf frontend/node_modules
	rm -rf backend/.pytest_cache

# Testing
test:
	@echo "Running backend tests..."
	cd backend && pytest -v
	@echo "Running frontend tests..."
	cd frontend && npm test -- --watchAll=false

test-coverage:
	@echo "Running backend tests with coverage..."
	cd backend && pytest --cov=app --cov-report=html --cov-report=term-missing

test-requirements:
	@echo "Testing all task requirements..."
	cd backend && pytest tests/test_task_requirements.py -v

# Linting
lint:
	cd backend && python -m flake8 app/
	cd frontend && npm run lint

# Demo data
seed-demo:
	@echo "Seeding demo data..."
	cd backend && python seed_demo_data.py

# Development setup
dev-setup: install db-init seed-demo
	@echo "Development environment ready!"
	@echo "Run 'make run' to start the application"

# Quick demo setup
demo: dev-setup
	@echo "🎬 Demo environment ready!"
	@echo "Visit http://localhost:3000 to start"
	@echo "Try logging in with: Alice Johnson (+1555001001)"