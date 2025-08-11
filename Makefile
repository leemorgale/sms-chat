.PHONY: help install run run-backend run-frontend docker-up docker-down clean db-setup db-init db-migrate db-reset db-seed test lint stop reset-db kill-db db-fresh db-revision db-status

# Detect OS and set Python command accordingly
ifeq ($(OS),Windows_NT)
    PYTHON := python
    DOCKER_CHECK := docker info >nul 2>&1
else
    PYTHON := python3  # This should handle WSL
    DOCKER_CHECK := docker info >/dev/null 2>&1
endif

# Default target
help:
	@echo "🚀 SMS Chat Application - Simple Commands:"
	@echo ""
	@echo "🎯 MAIN COMMANDS (what you need):"
	@echo "  make start        - 🚀 Start the app (first time setup + run)"
	@echo "  make run          - 🏃 Run the app (daily use)"
	@echo "  make reset        - 🔄 Reset app with fresh data"
	@echo "  make stop         - 🛑 Stop the app"
	@echo ""
	@echo "📋 DATABASE COMMANDS:"
	@echo "  make db-migrate   - Run database migrations"
	@echo "  make db-reset     - Reset database (clean slate)"
	@echo "  make db-fresh     - Reset database + add demo data"
	@echo "  make db-seed      - Add demo data to existing DB"
	@echo ""
	@echo "📋 OTHER COMMANDS:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run all tests"
	@echo "  make lint         - Run linting"
	@echo "  make clean        - Clean up files"
	@echo "  make status       - Check app status"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	cd backend && pip install flake8
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Run both services locally (simplified)
run:
	@echo "🚀 Starting SMS Chat Application (Local Development)..."
	@echo "===================================================="
	@echo ""
	@# Check PostgreSQL
	@if ! docker ps | grep -q postgres; then \
		echo "❌ PostgreSQL is not running!"; \
		echo "Run: make docker-postgres"; \
		exit 1; \
	fi
	@echo "✅ PostgreSQL is running"
	@$(MAKE) db-migrate
	@echo ""
	@echo "📱 Frontend: http://localhost:3000"
	@echo "🔧 Backend API: http://localhost:8000/docs"
	@echo ""
	@echo "Press Ctrl+C to stop both services"
	@echo "===================================================="
	@echo ""
	@# Run both backend and frontend with auto-reload
	@echo "Starting both backend and frontend with auto-reload..."
	@(make run-backend &) && make run-frontend

# Run backend
run-backend:
ifeq ($(OS),Windows_NT)
	cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
else
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
endif

# Run frontend (Vite dev server) - accessible from Windows
run-frontend:
	cd frontend && npm run dev -- --host

# Docker commands
docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

docker-clean:
	docker-compose down -v
	docker system prune -f

# Start PostgreSQL database only
run-db:
	@echo "🐘 Starting PostgreSQL database..."
	@docker start postgres-sms 2>/dev/null || docker run --name postgres-sms -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15
	@sleep 2
	@$(MAKE) db-init
	@$(MAKE) db-migrate
	@echo "✅ PostgreSQL running on localhost:5432 with migrations applied"

# Stop PostgreSQL database
stop-db:
	@echo "🛑 Stopping PostgreSQL database..."
	@docker stop postgres-sms 2>/dev/null || true
	@echo "✅ PostgreSQL stopped"

# Initialize database (first time only)
db-init:
	@echo "🆕 Initializing database..."
	@docker exec postgres-sms psql -U postgres -c "DROP DATABASE IF EXISTS sms_chat_db CASCADE;" 2>/dev/null || true
	@docker exec postgres-sms psql -U postgres -c "CREATE DATABASE sms_chat_db;" 2>/dev/null || echo "Database already exists"
	@docker exec postgres-sms psql -U postgres -c "DROP USER IF EXISTS smsuser;" 2>/dev/null || true
	@docker exec postgres-sms psql -U postgres -c "CREATE USER smsuser WITH PASSWORD 'smspass';" 2>/dev/null || echo "User already exists"
	@docker exec postgres-sms psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE sms_chat_db TO smsuser;" 2>/dev/null || true
	@docker exec postgres-sms psql -U postgres -d sms_chat_db -c "GRANT ALL ON SCHEMA public TO smsuser;" 2>/dev/null || true
	@docker exec postgres-sms psql -U postgres -d sms_chat_db -c "GRANT CREATE ON SCHEMA public TO smsuser;" 2>/dev/null || true
	@docker exec postgres-sms psql -U postgres -c "ALTER USER smsuser CREATEDB;" 2>/dev/null || true
	@echo "✅ Database initialized"

# Run migrations (pure Alembic)
db-migrate:
	@echo "🔄 Running database migrations..."
	@echo "Database URL: $(shell grep DATABASE_URL backend/.env)"
	@cd backend && $(PYTHON) -c "from app.db.database import engine; print('Testing DB connection:', engine.url)"
	@cd backend && $(PYTHON) -m alembic upgrade head
	@echo "Verifying tables created..."
	@docker exec postgres-sms psql -U smsuser -d sms_chat_db -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;" || echo "❌ Could not verify tables"
	@echo "✅ Migrations completed"

# Generate new migration
db-revision:
	@echo "📝 Generating migration..."
	@cd backend && $(PYTHON) -m alembic revision --autogenerate -m "$(m)"
	@echo "✅ Migration generated"

# Reset database schema (Clean container + Alembic - Production Standard)
db-reset:
	@echo "⚠️  Resetting database schema..."
	@echo "🗑️  Removing PostgreSQL container completely..."
	@$(MAKE) kill-db
	@sleep 1
	@$(MAKE) run-db
	@echo "✅ Schema reset complete"

# Seed with demo data
db-seed:
	@echo "🌱 Seeding database..."
	@cd backend && $(PYTHON) db_manager.py seed
	@echo "✅ Data seeded"

# Full reset with seed data (alias for db-reset + seed)
db-fresh:
	@echo "⚠️  Fresh database with demo data..."
	@$(MAKE) db-reset
	@$(MAKE) db-seed
	@echo "✅ Fresh database with demo data ready"

# Check migration status
db-status:
	@echo "📊 Database migration status:"
	cd backend && alembic current
	@echo ""
	@echo "Available migrations:"
	cd backend && alembic history

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

# Run all tests (both backend and frontend)
test:
	@echo "🧪 Running all tests (backend + frontend)..."
	@make test-backend
	@make test-frontend

# Backend tests only
test-backend:
	@echo "🧪 Running backend tests..."
	@echo "Creating temporary test database..."
	@docker exec postgres-sms psql -U postgres -c "DROP DATABASE IF EXISTS sms_chat_test_db;" 2>/dev/null || true
	@docker exec postgres-sms psql -U postgres -c "CREATE DATABASE sms_chat_test_db;" 2>/dev/null || true
	@docker exec postgres-sms psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE sms_chat_test_db TO smsuser;" 2>/dev/null || true
	@docker exec postgres-sms psql -U postgres -d sms_chat_test_db -c "GRANT ALL ON SCHEMA public TO smsuser;" 2>/dev/null || true
	@echo "Running migrations on test database..."
	@cd backend && TEST_DATABASE_URL=postgresql://smsuser:smspass@localhost:5432/sms_chat_test_db $(PYTHON) -m alembic upgrade head
	@echo "Running tests..."
	@cd backend && $(PYTHON) -m pytest -p no:twisted tests/ -v
	@echo "Cleaning up test database..."
	@docker exec postgres-sms psql -U postgres -c "DROP DATABASE IF EXISTS sms_chat_test_db;" 2>/dev/null || true
	@echo "✅ Tests completed and test database cleaned up"

# Frontend tests only  
test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && npm run test

# Linting
lint:
	cd backend && $(PYTHON) -m flake8 app/
	cd frontend && npm run lint

# Development setup - installs dependencies and sets up database
dev-setup: install
	@echo "🎉 Development environment ready!"
	@echo ""
	@echo "🚀 Next steps:"
	@echo "  1. Run 'make start' for first time setup"
	@echo "  2. Or 'make run' if already set up"
	@echo "  3. Visit http://localhost:3000"

# Start the app (first time setup)
start: install
	@echo "🚀 Starting SMS Chat App (First Time Setup)..."
	@docker start postgres-sms 2>/dev/null || docker run --name postgres-sms -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15
	@sleep 3
	@$(MAKE) db-reset
	@$(MAKE) db-migrate
	@echo ""
	@echo "🌐 App URLs:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend API: http://localhost:8000/docs"
	@echo ""
	@$(MAKE) run

# Reset the app with fresh data
reset: stop
	@echo "🔄 Resetting SMS Chat App..."
	@docker start postgres-sms 2>/dev/null || docker run --name postgres-sms -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15
	@sleep 2
	@$(MAKE) db-reset
	@$(MAKE) db-migrate
	@echo "✅ App reset complete!"
	@echo ""
	@echo "🚀 Run 'make run' to start the app"

# Remove redundant local-* commands - use main commands instead

# Stop all running services
stop:
	@echo "🛑 Stopping all services..."
	@-pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@-pkill -f "npm start" 2>/dev/null || true
	@-pkill -f "react-scripts start" 2>/dev/null || true
	@-pkill -f "vite" 2>/dev/null || true
ifeq ($(OS),Windows_NT)
	@-powershell -Command "Get-NetTCPConnection -LocalPort 8000,3000,5173 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $$.OwningProcess -Force -ErrorAction SilentlyContinue }" 2>/dev/null || true
else
	@-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:5173 | xargs kill -9 2>/dev/null || true
endif
	@echo "✅ All services stopped"

# Kill all processes (more aggressive)
kill-all:
	@echo "🔪 Force killing all services..."
	@-pkill -f "python.*uvicorn" 2>/dev/null || true
	@-pkill -f "node.*vite" 2>/dev/null || true
	@-pkill -f "npm.*dev" 2>/dev/null || true
	@-killall uvicorn 2>/dev/null || true
	@-killall node 2>/dev/null || true
ifeq ($(OS),Windows_NT)
	@-powershell -Command "Get-NetTCPConnection -LocalPort 8000,3000,5173 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $$.OwningProcess -Force -ErrorAction SilentlyContinue }" 2>/dev/null || true
else
	@-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:5173 | xargs kill -9 2>/dev/null || true
endif
	@echo "✅ All services force killed"

# Debug backend (run without reload for debugging)
debug-backend:
	@echo "🐛 Starting backend in debug mode..."
	cd backend && $(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug

# Run backend with verbose logging
debug-backend-verbose:
	@echo "🐛 Starting backend with verbose logging..."
	cd backend && $(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug --access-log


# Clean start - stop everything, reset DB, and run
clean-start: stop db-fresh
	@echo "🚀 Starting fresh..."
	@make run

# Build frontend (clean install dependencies)
build-frontend:
	@echo "🔧 Building frontend dependencies..."
	cd frontend && rm -rf node_modules package-lock.json
	cd frontend && npm install
	@echo "✅ Frontend build complete"

# Build frontend for production (TypeScript + Vite)
build-frontend-prod:
	@echo "🏗️  Building frontend for production..."
	cd frontend && npm run build
	@echo "✅ Production build complete! Files in frontend/dist/"

# Run frontend TypeScript checks
frontend-typecheck:
	@echo "🔍 Running TypeScript type checking..."
	cd frontend && npx tsc --noEmit
	@echo "✅ TypeScript check complete"

# Clean and reinstall frontend with TypeScript
frontend-clean-install:
	@echo "🧹 Cleaning frontend..."
	cd frontend && rm -rf node_modules package-lock.json dist
	@echo "📦 Installing dependencies..."
	cd frontend && npm install
	@echo "✅ Frontend ready for development"

# Quick start for TypeScript frontend (clean install + run)
frontend-fresh-start:
	@echo "🚀 Fresh start for TypeScript frontend..."
	@make frontend-clean-install
	@echo "🏃 Starting Vite dev server..."
	@make run-frontend

# Alias for backward compatibility
reset-db: db-reset


# Kill database container
kill-db:
	@echo "🛑 Stopping and removing PostgreSQL container..."
	@docker stop postgres-sms 2>/dev/null || true
	@docker rm postgres-sms 2>/dev/null || true
	@echo "✅ PostgreSQL container removed"

# Show configuration status
status:
	@echo "📊 Application Configuration Status:"
	@echo "🗄️  Database:"
	@docker ps | grep -q postgres-sms && echo "  ✅ PostgreSQL running" || echo "  ❌ PostgreSQL not running"
	@echo "📱 SMS Configuration:"
	@grep -q "MOCK_SMS=true" backend/.env && echo "  ✅ Mock SMS mode (MOCK_SMS=true in .env)" || echo "  ✅ Real Twilio mode (MOCK_SMS=false in .env)"
	@echo "🌐 Services:"
	@curl -s -f http://localhost:8000/ > /dev/null && echo "  ✅ Backend (port 8000)" || echo "  ❌ Backend not running"
	@curl -s -f http://localhost:3000/ > /dev/null && echo "  ✅ Frontend (port 3000)" || echo "  ❌ Frontend not running"

# Check if app is accessible 
check-app:
	@echo "🔍 Checking app accessibility..."
	@echo "Backend (port 8000):"
	@curl -s -f http://localhost:8000/ > /dev/null && echo "✅ Backend accessible" || echo "❌ Backend not accessible"
	@echo "Frontend (port 3000):"
	@curl -s -f http://localhost:3000/ > /dev/null && echo "✅ Frontend accessible" || echo "❌ Frontend not accessible"
	@echo ""
	@echo "🌐 Access URLs:"
	@echo "  Windows: http://localhost:3000/"
	@echo "  WSL: http://localhost:3000/"