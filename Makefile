.PHONY: install run clean setup-env help flutter-setup flutter-web flutter-macos flutter-clean api-server dev-full start-all stop-all
default: help

# Default help
help:
	@echo "🔍 Ping Monitor - Available Commands:"
	@echo ""
	@echo "📦 Backend (Python):"
	@echo "  make install       - Create virtual environment and install Python dependencies"
	@echo "  make run           - Install dependencies and run PingMonitor.py"
	@echo "  make api-server    - Start HTTP API server for Flutter frontend"
	@echo "  make setup-env     - Create .env file from sample.env"
	@echo "  make clean         - Clean up Python virtual environment and cache files"
	@echo ""
	@echo "📱 Frontend (Flutter):"
	@echo "  make flutter-setup - Install Flutter dependencies"
	@echo "  make flutter-web   - Run Flutter web app (requires api-server)"
	@echo "  make flutter-macos - Run Flutter macOS app (requires api-server)"
	@echo "  make flutter-clean - Clean Flutter build cache"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make dev-full      - Setup complete development environment"
	@echo "  make start-all     - 🌟 Start everything (monitor + API + frontend)"
	@echo "  make stop-all      - Stop all running processes"
	@echo "  make help          - Show this help message"
	@echo ""
	@echo "📋 Quick Start:"
	@echo "  make start-all     - One command to rule them all! 🎆"
	@echo ""
	@echo "📋 Manual Setup:"
	@echo "  Terminal 1: make run"
	@echo "  Terminal 2: make api-server"
	@echo "  Terminal 3: make flutter-web"

# Backend Python commands
setup-env:
	@if [ ! -f .env ]; then \
		cp sample.env .env; \
		echo "📄 .env file created from sample.env"; \
		echo "✏️  Please edit .env file with your configuration"; \
	else \
		echo "📄 .env file already exists"; \
	fi

install: setup-env
	@echo "🐍 Creating Python virtual environment..."
	test -d .venv || python3 -m venv .venv
	@echo "📦 Installing Python dependencies..."
	. .venv/bin/activate && \
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements.txt
	@echo "✅ Python dependencies installed successfully!"

run: install
	@echo "🚀 Starting Ping Monitor..."
	PYTHONPATH=. .venv/bin/python PingMonitor.py

api-server: install
	@echo "🌐 Starting HTTP API server on port 8000..."
	@echo "📡 API endpoints available at http://localhost:8000"
	PYTHONPATH=. .venv/bin/python csv_server.py 8000

clean:
	@echo "🧹 Cleaning Python environment..."
	rm -rf .venv
	rm -rf __pycache__
	rm -rf *.pyc
	@echo "✅ Python environment cleaned!"

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
	@echo "📡 Make sure API server is running: make api-server"
	cd pingmonitorflutter && flutter run -d chrome --web-port 8080

flutter-macos: flutter-setup
	@echo "🖥️  Starting Flutter macOS app..."
	@echo "📡 Make sure API server is running: make api-server"
	cd pingmonitorflutter && flutter run -d macos

flutter-clean:
	@echo "🧹 Cleaning Flutter build cache..."
	cd pingmonitorflutter && flutter clean
	@echo "✅ Flutter cache cleaned!"

# Development environment
start-all: dev-full
	@echo "🚀 Starting complete Ping Monitor system..."
	@echo "🔄 Launching all components in background..."
	@echo ""
	@echo "🐍 Starting Python Ping Monitor with .venv..."
	@bash -c 'PYTHONPATH=. .venv/bin/python PingMonitor.py > ping_monitor.log 2>&1 &'
	@sleep 3
	@echo "🌐 Starting API server with .venv..."
	@bash -c 'PYTHONPATH=. .venv/bin/python csv_server.py 8000 > api_server.log 2>&1 &'
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
	@pkill -f "PingMonitor.py" || true
	@pkill -f "csv_server.py" || true
	@pkill -f "flutter run" || true
	@rm -f ping_monitor.log api_server.log || true
	@echo "✅ All processes stopped and logs cleaned!"

dev-full: install flutter-setup
	@echo "🚀 Complete development environment ready!"
	@echo ""
	@echo "🎯 Next steps:"
	@echo "  1. Terminal 1: make run"
	@echo "  2. Terminal 2: make api-server"
	@echo "  3. Terminal 3: make flutter-web"
	@echo ""
	@echo "📱 Flutter app will be available at: http://localhost:8080"
	@echo "📡 API server will be available at: http://localhost:8000"
