
.PHONY: install run clean setup-env help flutter-setup flutter-web flutter-macos flutter-clean api-server dev-full start-all stop-all db-start db-stop db-init db-logs run-db fastapi-server database

default: help

# Default help
help:
	@echo "🔍 Ping Monitor - Available Commands:"
	@echo ""
	@echo "📦 Backend (Python):"
	@echo "  make install          - Create virtual environment and install Python dependencies"
	@echo "  make run              - Install dependencies and run original PingMonitor.py (CSV-based)"
	@echo "  make run-db           - Install dependencies and run database_ping_monitor.py"
	@echo "  make api-server       - Start CSV-based HTTP API server for Flutter frontend"
	@echo "  make fastapi-server   - Start FastAPI server with PostgreSQL backend"
	@echo "  make setup-env        - Create .env file from sample.env"
	@echo "  make clean            - Clean up Python virtual environment and cache files"
	@echo ""
	@echo "🗄️  Database:"
	@echo "  make db-start         - Start PostgreSQL database with Docker"
	@echo "  make db-stop          - Stop PostgreSQL database"
	@echo "  make db-init          - Initialize database schema and tables"
	@echo "  make db-logs          - Show database logs"
	@echo "  make database         - Setup complete database environment (start + init)"
	@echo ""
	@echo "📱 Frontend (Flutter):"
	@echo "  make flutter-setup    - Install Flutter dependencies"
	@echo "  make flutter-web      - Run Flutter web app (requires api-server or fastapi-server)"
	@echo "  make flutter-macos    - Run Flutter macOS app (requires api-server or fastapi-server)"
	@echo "  make flutter-clean    - Clean Flutter build cache"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make dev-full         - Setup complete development environment"
	@echo "  make start-all        - 🌟 Start everything (database + monitor + FastAPI + frontend)"
	@echo "  make start-csv        - Start CSV-based system (original)"
	@echo "  make stop-all         - Stop all running processes"
	@echo "  make help             - Show this help message"
	@echo ""
	@echo "📋 Quick Start (Database-enabled - Recommended):"
	@echo "  make start-all        - One command to rule them all! 🎆"
	@echo ""
	@echo "📋 Quick Start (CSV-based - Legacy):"
	@echo "  make start-csv        - Start original CSV-based system"
	@echo ""
	@echo "📋 Manual Setup (Database):"
	@echo "  Terminal 1: make database"
	@echo "  Terminal 2: make run-db"
	@echo "  Terminal 3: make fastapi-server"
	@echo "  Terminal 4: make flutter-web"

# Backend Python commands
setup-env:
	@if [ ! -f .env ]; then \
		cp sample.env .env; \
		echo "📄 .env file created from sample.env"; \
		echo "✏️  Please edit .env file with your configuration"; \
		echo ""; \
		echo "🗄️  Database configuration added to .env:"; \
		echo "DB_HOST=localhost" >> .env; \
		echo "DB_PORT=5432" >> .env; \
		echo "DB_NAME=ping_monitor" >> .env; \
		echo "DB_USER=admin" >> .env; \
		echo "DB_PASSWORD=password" >> .env; \
		echo "  ✅ Database settings added"; \
	else \
		echo "📄 .env file already exists"; \
		if ! grep -q "DB_HOST" .env; then \
			echo ""; \
			echo "🗄️  Adding database configuration to existing .env:"; \
			echo "DB_HOST=localhost" >> .env; \
			echo "DB_PORT=5432" >> .env; \
			echo "DB_NAME=ping_monitor" >> .env; \
			echo "DB_USER=admin" >> .env; \
			echo "DB_PASSWORD=password" >> .env; \
			echo "  ✅ Database settings added"; \
		fi \
	fi

install: setup-env
	@echo "🐍 Creating Python virtual environment..."
	test -d .venv || python3 -m venv .venv
	@echo "📦 Installing Python dependencies..."
	. .venv/bin/activate && \
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements.txt
	@echo "✅ Python dependencies installed successfully!"

# Create database.py file if it doesn't exist
database.py:
	@if [ ! -f database.py ]; then \
		echo "📁 Creating database.py module..."; \
		echo 'from db_connect import db_manager' > database.py; \
		echo '' >> database.py; \
		echo '# Re-export the db_manager for easier imports' >> database.py; \
		echo "__all__ = ['db_manager']" >> database.py; \
		echo "  ✅ database.py created"; \
	fi

run: install
	@echo "🚀 Starting original CSV-based Ping Monitor..."
	PYTHONPATH=. .venv/bin/python PingMonitor.py

run-db: install database.py
	@echo "🚀 Starting database-enabled Ping Monitor..."
	@echo "📊 Make sure PostgreSQL is running: make database"
	PYTHONPATH=. .venv/bin/python database_ping_monitor.py

api-server: install
	@echo "🌐 Starting CSV-based HTTP API server on port 8000..."
	@echo "📡 API endpoints available at http://localhost:8000"
	PYTHONPATH=. .venv/bin/python csv_server.py 8000

fastapi-server: install database.py
	@echo "🚀 Starting FastAPI server with PostgreSQL backend on port 8000..."
	@echo "📡 API documentation available at http://localhost:8000/docs"
	@echo "📊 Make sure PostgreSQL is running: make database"
	PYTHONPATH=. .venv/bin/python fastapi_app.py

clean:
	@echo "🧹 Cleaning Python environment..."
	rm -rf .venv
	rm -rf __pycache__
	rm -rf *.pyc
	rm -f database.py
	@echo "✅ Python environment cleaned!"

# Database commands
db-start:
	@echo "🐳 Starting PostgreSQL database with Docker..."
	docker-compose up -d postgres
	@echo "⏳ Waiting for database to be ready..."
	@bash -c 'counter=0; until docker-compose exec postgres pg_isready -U admin -d ping_monitor 2>/dev/null || [ $$counter -eq 15 ]; do sleep 2; counter=$$((counter+1)); done; if [ $$counter -eq 15 ]; then echo "❌ Database failed to start within 30 seconds" && exit 1; fi'
	@echo "✅ Database is ready!"

db-stop:
	@echo "🛑 Stopping PostgreSQL database..."
	docker-compose down
	@echo "✅ Database stopped!"

db-init:
	@echo "🗄️  Initializing database schema..."
	@if [ -f scripts/db_init.sql ]; then \
		docker-compose exec -T postgres psql -U admin -d ping_monitor < scripts/db_init.sql; \
		echo "✅ Database schema initialized!"; \
	else \
		echo "❌ Database initialization file not found at scripts/db_init.sql"; \
		exit 1; \
	fi

db-logs:
	@echo "📋 Database logs:"
	docker-compose logs postgres

database: db-start db-init
	@echo "✅ Database environment ready!"
	@echo "📊 PostgreSQL running on localhost:5432"
	@echo "🗄️  Database: ping_monitor"
	@echo "👤 User: admin"

# Flutter frontend commands
flutter-setup:
	@echo "📱 Installing Flutter dependencies..."
	@if [ ! -d "pingmonitorflutter" ]; then \
		echo "❌ Flutter project directory not found. Run from project root."; \
		exit 1; \
	fi
	cd pingmonitorflutter && flutter pub get
	@echo "✅ Flutter dependencies installed!"

flutter-web: flutter-setup
	@echo "🌐 Starting Flutter web app on http://localhost:8080..."
	@echo "📡 Make sure API server is running:"
	@echo "    CSV-based: make api-server"
	@echo "    Database:  make fastapi-server"
	cd pingmonitorflutter && flutter run -d chrome --web-port 8080

flutter-macos: flutter-setup
	@echo "🖥️  Starting Flutter macOS app..."
	@echo "📡 Make sure API server is running:"
	@echo "    CSV-based: make api-server"
	@echo "    Database:  make fastapi-server"
	cd pingmonitorflutter && flutter run -d macos

flutter-clean:
	@echo "🧹 Cleaning Flutter build cache..."
	cd pingmonitorflutter && flutter clean
	@echo "✅ Flutter cache cleaned!"

# Development environment
start-all: dev-full database database.py
	@echo "🚀 Starting complete Ping Monitor system with PostgreSQL..."
	@echo "🔄 Launching all components in background..."
	@echo ""
	@echo "🐍 Starting database-enabled Ping Monitor..."
	@PYTHONPATH=. nohup .venv/bin/python database_ping_monitor.py > ping_monitor.log 2>&1 &
	@sleep 3
	@echo "🚀 Starting FastAPI server..."
	@PYTHONPATH=. nohup .venv/bin/python fastapi_app.py > fastapi_server.log 2>&1 &
	@sleep 3
	@echo "📱 Starting Flutter web app..."
	@echo ""
	@echo "✨ System Status:"
	@echo "  ✅ PostgreSQL Database: Running (docker-compose)"
	@echo "  ✅ Python Monitor: Running in background (check ping_monitor.log)"
	@echo "  ✅ FastAPI Server: http://localhost:8000 (check fastapi_server.log)"
	@echo "  ✅ API Docs: http://localhost:8000/docs"
	@echo "  🔄 Flutter App: Launching..."
	@echo ""
	@echo "👀 Opening Flutter app in browser..."
	cd pingmonitorflutter && flutter run -d chrome --web-port 8080

start-csv: dev-full
	@echo "🚀 Starting CSV-based Ping Monitor system (legacy)..."
	@echo "🔄 Launching all components in background..."
	@echo ""
	@echo "🐍 Starting CSV-based Python Monitor..."
	@PYTHONPATH=. nohup .venv/bin/python PingMonitor.py > ping_monitor.log 2>&1 &
	@sleep 3
	@echo "🌐 Starting CSV API server..."
	@PYTHONPATH=. nohup .venv/bin/python csv_server.py 8000 > api_server.log 2>&1 &
	@sleep 3
	@echo "📱 Starting Flutter web app..."
	@echo ""
	@echo "✨ System Status:"
	@echo "  ✅ Python Monitor: Running in background (check ping_monitor.log)"
	@echo "  ✅ API Server: http://localhost:8000 (check api_server.log)"
	@echo "  🔄 Flutter App: Launching..."
	@echo ""
	@echo "👀 Opening Flutter app in browser..."
	cd pingmonitorflutter && flutter run -d chrome --web-port 8080

stop-all:
	@echo "🛑 Stopping all Ping Monitor processes..."
	@pkill -f "database_ping_monitor.py" || true
	@pkill -f "PingMonitor.py" || true
	@pkill -f "fastapi_app.py" || true
	@pkill -f "csv_server.py" || true
	@pkill -f "flutter run" || true
	@rm -f ping_monitor.log api_server.log fastapi_server.log || true
	@echo "🐳 Stopping database..."
	@docker-compose down || true
	@echo "✅ All processes stopped and logs cleaned!"

dev-full: install flutter-setup
	@echo "🚀 Complete development environment ready!"
	@echo ""
	@echo "🎯 Next steps for Database system (Recommended):"
	@echo "  1. make database      # Start & initialize PostgreSQL"
	@echo "  2. make run-db        # Start database monitor"
	@echo "  3. make fastapi-server # Start FastAPI server"
	@echo "  4. make flutter-web   # Start Flutter frontend"
	@echo ""
	@echo "🎯 Or use one command: make start-all"
	@echo ""
	@echo "📱 Flutter app will be available at: http://localhost:8080"
	@echo "🚀 FastAPI server will be available at: http://localhost:8000"
	@echo "📖 API docs will be available at: http://localhost:8000/docs"