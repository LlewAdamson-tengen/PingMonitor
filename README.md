# Ping Monitor

This **Ping Monitor** is a comprehensive network monitoring solution with both a Python backend and Flutter frontend. It provides continuous monitoring of websites and hosts with real-time data visualization, dynamic configuration management, PostgreSQL database storage, and multiple alert mechanisms.

## 🚀 Overview

The Ping Monitor system consists of:

### Backend (Python)
- Resolving website URLs to their corresponding IP addresses
- Measuring precise latency values in repetitive intervals
- Alerting via email when specific ping threshold values are exceeded
- **PostgreSQL database storage** for scalable data management
- **CSV file fallback** for legacy compatibility (`ping_results.csv`)
- Triggering desktop notifications and sound alerts for critical thresholds
- **FastAPI HTTP server** for modern REST API integration
- **Docker-based PostgreSQL** for easy database deployment

### Frontend (Flutter)
- Real-time dashboard showing all monitored URLs
- Interactive configuration management
- Historical data visualization with charts
- Dynamic URL management (add/edit/delete targets)
- Detailed per-URL statistics and performance metrics
- Cross-platform support (Web, macOS, iOS, Android)

---

## 🛠 Technologies & Dependencies

### Backend (Python)

| Package                           | Purpose                                  | Version    |
|-----------------------------------|------------------------------------------|------------|
| `python-dotenv`                   | Handling of environment settings         | ~1.0.1     |
| `requests`                        | Handling HTTP requests                   | ~2.32.3    |
| `plyer`                           | Cross-platform notifications             | ~2.1.0     |
| `pygame`                          | Playing audio notifications              | ~2.6.1     |
| `pync`                            | macOS desktop notifications              | ~2.0.3     |
| `notify2` \(\*Linux only\*\)      | Linux desktop notifications              | ~0.3.1     |
| `win10toast` \(\*Windows only\*\) | Windows desktop notifications            | ~0.9       |
| `asyncpg`                         | PostgreSQL async database driver         | ≥0.30.0    |
| `pydantic`                        | Data validation and serialization        | ≥2.10.0    |
| `fastapi`                         | Modern Python web framework              | ≥0.115.2   |
| `uvicorn`                         | ASGI server for FastAPI                  | ≥0.27.1    |

### Frontend (Flutter)
| Package         | Purpose                              | Version  |
|-----------------|--------------------------------------|----------|
| `http`          | HTTP client for API communication    | ^1.4.0   |
| `path_provider` | File system access                   | ^2.1.2   |
| `csv`           | CSV data parsing                     | ^6.0.0   |
| `fl_chart`      | Charts and data visualization        | ^0.68.0  |

> *Dependencies are managed through `requirements.txt` (Python) and `pubspec.yaml` (Flutter).*

---

## 🏗️ Architecture

The Ping Monitor system uses a modern four-tier architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PING MONITOR SYSTEM                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter Web   │◄──►│   FastAPI       │◄──►│ Python Monitor  │◄──►│   PostgreSQL    │
│  localhost:8080 │    │  localhost:8000 │    │database_ping_   │    │  localhost:5432 │
│                 │    │                 │    │  monitor.py     │    │                 │
│ • Dashboard     │    │ • REST API      │    │ • Multi-URL     │    │ • ping_results  │
│ • Settings      │    │ • CORS Enabled  │    │   Monitoring    │    │ • Indexed Data  │
│ • Analytics     │    │ • PostgreSQL    │    │ • DB Logging    │    │ • Async Pool    │
│ • URL Manager   │    │ • Data API      │    │ • Alerts        │    │ • Docker        │
│ • Charts        │    │ • Type Safety   │    │ • Notifications │    │ • Persistence   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Layer    │    │  Service Layer  │    │ Monitor Layer   │    │   Data Layer    │
│                 │    │                 │    │                 │    │                 │
│ • Web Browser   │    │ • fastapi_app.py│    │ • Ping Engine   │    │ • PostgreSQL DB │
│ • Mobile App    │    │ • JSON API      │    │ • Thread Mgmt   │    │ • .env config   │
│ • Desktop App   │    │ • DB Queries    │    │ • Config Watch  │    │ • CSV fallback  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔄 Data Flow

1. **Configuration**: Flutter frontend reads/writes to `.env` via FastAPI
2. **Monitoring**: Python backend pings URLs and logs to **PostgreSQL database**
3. **Database**: PostgreSQL stores ping results with indexing for fast queries
4. **API**: FastAPI serves structured data from database to frontend
5. **Visualization**: Flutter displays real-time charts and status with proper data types
6. **Alerts**: Python triggers notifications (email, desktop, audio)
7. **Persistence**: Data survives restarts and provides historical analytics

### 🌐 Communication Protocols

| Component      | Protocol  | Port | Purpose                   |
|----------------|-----------|------|---------------------------|
| Flutter Web    | HTTP      | 8080 | User interface            |
| FastAPI Server | HTTP/REST | 8000 | Data & config API         |
| PostgreSQL     | TCP/IP    | 5432 | Database storage          |
| Python Monitor | AsyncPG   | -    | Database logging          |
| Docker Compose | HTTP      | -    | Container orchestration   |
| SMTP Alerts    | SMTP      | 587  | Email notifications       |

### 📊 Real-time Updates

- **Frontend**: Auto-refresh every 10 seconds
- **Backend**: Configurable ping intervals (default: 30s)
- **API**: On-demand data serving with filtering
- **Configuration**: Live updates without restart

### 🔄 Dynamic Configuration

**Zero-Downtime URL Management:**
- Add/remove target URLs via Flutter frontend
- Automatic `.env` file monitoring every 2 seconds
- Dynamic thread management for new/removed URLs
- No restart required for configuration changes

**How it works:**
1. Edit URLs in Flutter settings
2. Configuration saved to `.env` file
3. Python monitor detects file changes
4. Automatically starts monitoring new URLs
5. Stops monitoring removed URLs
6. All without interrupting existing monitoring

---

## 📦 Installation

To set up and run your Ping Monitor project:

**Prerequisites:**
- Python 3.13+ installed (Python 3.8+ supported)
- Flutter SDK installed (for frontend)
- Docker and Docker Compose (for PostgreSQL)
- Git

**Step-by-step:**

1. **Clone** this repository:
   ```bash
   git clone git@github.com:LlewAdamson-tengen/PingMonitor.git
   cd PingMonitor
   ```

2. **Set up the backend:**
   ```bash
   # Create .env file from sample
   make setup-env
   
   # Install Python dependencies 
   make install
   ```

3. **🌟 One-command startup** (recommended):
   ```bash
   make start-all    # Starts PostgreSQL + Monitor + FastAPI + Flutter
   ```
   
   **OR manually** (in separate terminals):
   ```bash
   # Start PostgreSQL database
   make database
   
   # Start monitoring with database
   make run-db
   
   # Start FastAPI server (in another terminal)
   make fastapi-server
   
   # Run Flutter app (in another terminal)
   make flutter-web
   ```

---

## 🟢 Usage

### Available Systems

#### 🎆 **Database System (Recommended)**
```bash
make start-all    # Complete system with PostgreSQL
make stop-all     # Stop everything
```

#### 📜 **Legacy CSV System**
```bash
make start-csv    # Original CSV-based system
make stop-all     # Stop everything
```

### 🌟 Full System Commands
| Command               | Description                                               |
|-----------------------|-----------------------------------------------------------|
| `make start-all`      | Start PostgreSQL \+ Monitor \+ FastAPI \+ Flutter         |
| `make start-csv`      | Start legacy CSV\-based system                          s |
| `make stop-all`       | Stop all running processes and containers                 |
| `make database`       | Start and initialize PostgreSQL only                      |
| `make run-db`         | Start database\-enabled monitoring only                   |
| `make fastapi-server` | Start FastAPI server only                                 |
| `make flutter-web`    | Start Flutter web app only                                |

### Manual Setup (Step-by-Step)
1. **Start the database** (Terminal 1):
   ```bash
   make database
   ```

2. **Start database monitoring** (Terminal 2):
   ```bash
   make run-db
   ```

3. **Start the FastAPI server** (Terminal 3):
   ```bash
   make fastapi-server
   ```

4. **Launch Flutter frontend** (Terminal 4):
   ```bash
   make flutter-web    # For web app
   make flutter-macos  # For macOS app
   ```

### Flutter Frontend Features
- **Dashboard**: Real-time monitoring overview with status cards for each URL
- **Settings**: Dynamic configuration management with live editing of:
  - Target URLs (add/edit/delete)
  - SMTP settings
  - Ping thresholds and intervals
  - Alert configurations
- **URL Details**: Per-URL analytics with:
  - Latency charts
  - Status distribution pie charts
  - Recent ping history
  - Uptime statistics

### Backend Features

#### 📋 **Database System (Recommended)**
- PostgreSQL database storage with indexing
- Real-time structured data with proper types
- Persistent historical data across restarts
- FastAPI REST endpoints with automatic documentation
- Async database connections for high performance

#### 📜 **Legacy CSV System**
- CSV file logging (`ping_results.csv`)
- Simple HTTP API server
- File-based data storage

#### 🔔 **Alert Features (Both Systems)**
During alert events, notifications (email, desktop pop-ups, audible alerts) are triggered for immediate issue awareness.

---

## 🧹 Cleaning & Reset

To clean and reset your entire environment:

```bash
make clean
```

This command:

- Deletes your current Python virtual environment (`.venv`) 
- Clears Python caches (`__pycache__`)
- Reinstalls all requirements and runs the monitor fresh

---

## 🗂 Data Storage 

### 📋 **PostgreSQL Database (Recommended)**
Ping records are stored in a structured PostgreSQL database:

**Table: `ping_results`**
```sql
COLUMN           | TYPE      | DESCRIPTION
-----------------|-----------|---------------------------
id               | SERIAL    | Unique record identifier
timestamp        | TIMESTAMP | When the ping was performed
url              | VARCHAR   | Target URL being monitored
ip               | INET      | Resolved IP address
status           | VARCHAR   | Success/High Latency/Ping Failure
response_time_ms | DECIMAL   | Response time in milliseconds
count            | INTEGER   | Consecutive ping counter
```

**Benefits:**
- ✅ **Indexed queries** for fast data retrieval
- ✅ **Proper data types** for charts and analytics
- ✅ **Persistent storage** across system restarts
- ✅ **Structured queries** with filtering and aggregation

### 📜 **CSV Fallback (Legacy)**
Ping records can also be logged to `ping_results.csv`:
```
2025-03-11 13:52:48,21.579,0
2025-03-11 13:58:26,3458.861,0 
2025-03-11 14:10:26,5566.672,0
```

- **warnings** count consecutive pings above your defined threshold
- Actual timestamps provide clear records of ping performance and historical data

---

## 📅 Project Structure

```
PingMonitor/
├── Backend (Python)
│   ├── .venv/                      # Virtual environment
│   ├── database_ping_monitor.py    # Database-enabled monitor (recommended)
│   ├── PingMonitor.py              # Legacy CSV-based monitor
│   ├── fastapi_app.py              # FastAPI server (PostgreSQL)
│   ├── csv_server.py               # Legacy HTTP API server
│   ├── db_connect.py               # Database connection manager
│   ├── requirements.txt            # Python dependencies
│   ├── docker-compose.yml          # PostgreSQL container config
│   ├── scripts/db_init.sql         # Database schema
│   ├── .env                        # Environment configuration
│   ├── sample.env                  # Sample configuration
│   ├── ping_results.csv            # Generated CSV data (legacy)
│   └── alert.mp3                   # Alert sound file
│
├── Frontend (Flutter)
│   ├── pingmonitorflutter/
│   │   ├── lib/
│   │   │   ├── main.dart           # App entry point
│   │   │   ├── models/             # Data models (updated for PostgreSQL)
│   │   │   ├── screens/            # UI screens
│   │   │   ├── services/           # API services
│   │   │   └── widgets/            # Reusable components
│   │   ├── pubspec.yaml            # Flutter dependencies
│   │   └── web/                    # Web platform files
│
├── Makefile                        # Build automation (updated commands)
├── README.md                       # This file
└── LICENSE                         # MIT License
```
---

## 🌐 API Endpoints

### 🚀 **FastAPI Server (PostgreSQL) - Recommended**

| Endpoint             | Method | Description                         | Parameters                |
|----------------------|--------|-------------------------------------|---------------------------|
| `/`                  | GET    | API information and version         | None                      |
| `/health`            | GET    | Health check and database status    | None                      |
| `/ping-results/`     | GET    | Retrieve ping data from database    | `url`, `limit`, `offset`  |
| `/ping-data`         | GET    | Flutter-compatible ping data alias  | `url`, `limit`, `offset`  |
| `/latest-status/`    | GET    | Latest status for each monitored URL| None                      |
| `/statistics/{url}/` | GET    | Detailed statistics for specific URL| `hours` (time range)      |
| `/cleanup/`          | DELETE | Clean up old ping results           | `days_to_keep`            |

### 📜 **Legacy CSV API Server**

```markdown
| Endpoint        | Method | Description                          | Parameters     |
|-----------------|--------|--------------------------------------|----------------|
| `/health`       | GET    | Health check and system status       | None           |
| `/ping-data`    | GET    | Retrieve ping data from CSV          | `url`, `limit` |
| `/url-statuses` | GET    | Aggregated status for all URLs       | None           |
| `/env-config`   | GET    | Current `.env` configuration         | None           |
| `/env-config`   | POST   | Update `.env` configuration          | JSON body      |```

**Example Usage (FastAPI):**
```bash
# Get health status and database connection
curl http://localhost:8000/health

# Get recent ping data for specific URL
curl "http://localhost:8000/ping-data?url=google.com&limit=10"

# Get latest status for all monitored URLs
curl http://localhost:8000/latest-status/

# Get detailed statistics for a URL
curl http://localhost:8000/statistics/google.com/?hours=24

# View API documentation (FastAPI auto-generated)
open http://localhost:8000/docs
```

---

## 🛠️ Recent Fixes & Improvements

### ✅ **Python 3.13 Compatibility** 
Updated all dependencies to support Python 3.13:
- `pygame` upgraded from 2.5.0 → 2.6.1
- `asyncpg` upgraded to ≥0.30.0 with proper wheel support
- `pydantic` upgraded to ≥2.10.0 with Python 3.13 compatibility

### ✅ **Database Architecture Overhaul**
- Added PostgreSQL database support with Docker
- Implemented FastAPI for modern REST API
- Fixed data serialization issues (IP addresses, response times)
- Added proper indexing for fast queries

### ✅ **macOS Compatibility Fixes**
- Replaced `timeout` command with macOS-compatible shell scripts
- Fixed background process management in Makefile
- Resolved Docker Compose environment variable issues

### ✅ **Flutter Chart Fixes**
- Fixed data type mismatches (`response_time_ms` string → number)
- Corrected IP address serialization (removed CIDR notation)
- Updated Flutter models to match new API response format
- Enhanced debugging and error handling

### ✅ **System Integration**
- Fixed `make start-all` and `make stop-all` commands
- Improved background process management
- Added comprehensive database connection pooling
- Enhanced error handling and logging

---

## ✅ Supported Platforms

### Backend (Python)
- 🟢 **macOS** (with Docker Desktop)
- 🟢 **Linux** (with Docker and notify2 library)
- 🟢 **Windows** (with Docker Desktop and win10toast library)

### Frontend (Flutter)
- 🟢 **Web browsers** (Chrome, Firefox, Safari, Edge)
- 🟢 **macOS** (native app)
- 🟢 **iOS** (with Xcode)
- 🟢 **Android** (with Android Studio)
- 🟢 **Linux** (with Flutter Linux support)
- 🟢 **Windows** (with Flutter Windows support)

---

## 🙋‍♂️ Contribute & Feedback

- Open issues clearly, make pull requests, and provide any feedback!
- Contributions (feature requests, bug fixes, enhancements) are welcome.

---

## ⚠️ Security Notice

- **DO NOT** commit sensitive `.env` files to version control as they might contain password/private credentials.
- Use secure application-specific passwords for SMTP email integration.

---

## 📜 Licensing

MIT License © 2025 Llew Adamson

---

🎉 **Thank you for using Ping Monitor! 
Please reach out if you have any questions, found any bugs, or have some features you'd like to see. Happy Monitoring.**