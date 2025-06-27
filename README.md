# Ping Monitor

This **Ping Monitor** is a comprehensive network monitoring solution with both a Python backend and Flutter frontend. It provides continuous monitoring of websites and hosts with real-time data visualization, dynamic configuration management, and multiple alert mechanisms.

## 🚀 Overview

The Ping Monitor system consists of:

### Backend (Python)
- Resolving website URLs to their corresponding IP addresses
- Measuring precise latency values in repetitive intervals
- Alerting via email when specific ping threshold values are exceeded
- Logging timestamp, latency, and downtime information into CSV files (`ping_results.csv`)
- Triggering desktop notifications and sound alerts for critical thresholds
- HTTP API server for frontend integration

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
| Package          | Purpose                                  | Version  |
| ---------------- |------------------------------------------| -------- |
| `python-dotenv`  | Handling of environment settings         | ≈1.0.1   |
| `requests`       | Handling HTTP requests        | ≈2.32.3  |
| `plyer`          | Cross-platform notifications  | ≈2.1.0   |
| `pygame`         | Playing audio notifications   | ≈2.5.0   |
| `pync`           | macOS desktop notifications   | ≈2.0.3   |
| `notify2` *(Linux only)*     | Linux desktop notifications   | ≈0.3.1   |
| `win10toast` *(Windows only)* | Windows desktop notifications | ≈0.9     |

### Frontend (Flutter)
| Package          | Purpose                                  | Version  |
| ---------------- |------------------------------------------| -------- |
| `http`           | HTTP client for API communication       | ^1.4.0   |
| `path_provider`  | File system access                       | ^2.1.2   |
| `csv`            | CSV data parsing                         | ^6.0.0   |
| `fl_chart`       | Charts and data visualization            | ^0.68.0  |

> *Dependencies are managed through `requirements.txt` (Python) and `pubspec.yaml` (Flutter).*

---

## 🏗️ Architecture

The Ping Monitor system uses a modern three-tier architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PING MONITOR SYSTEM                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter Web   │◄──►│   HTTP API      │◄──►│ Python Monitor  │
│  localhost:8080 │    │  localhost:8000 │    │  PingMonitor.py │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • REST API      │    │ • Multi-URL     │
│ • Settings      │    │ • CORS Enabled  │    │   Monitoring    │
│ • Analytics     │    │ • Config Mgmt   │    │ • CSV Logging   │
│ • URL Manager   │    │ • Data Serving  │    │ • Alerts        │
│ • Charts        │    │ • Health Check  │    │ • Notifications │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Layer    │    │  Service Layer  │    │   Data Layer    │
│                 │    │                 │    │                 │
│ • Web Browser   │    │ • csv_server.py │    │ • .env config   │
│ • Mobile App    │    │ • JSON API      │    │ • CSV files     │
│ • Desktop App   │    │ • HTTP Endpoints│    │ • Log files     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔄 Data Flow

1. **Configuration**: Flutter frontend reads/writes to `.env` via API
2. **Monitoring**: Python backend pings URLs and logs to CSV
3. **API**: HTTP server serves CSV data and configuration to frontend
4. **Visualization**: Flutter displays real-time charts and status
5. **Alerts**: Python triggers notifications (email, desktop, audio)

### 🌐 Communication Protocols

| Component | Protocol | Port | Purpose |
|-----------|----------|------|----------|
| Flutter Web | HTTP | 8080 | User interface |
| API Server | HTTP/REST | 8000 | Data & config API |
| Python Monitor | File I/O | - | CSV logging |
| SMTP Alerts | SMTP | 587 | Email notifications |

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
- Python 3.8+ installed
- Flutter SDK installed (for frontend)
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
   
   # Install Python dependencies and start monitoring
   make run
   ```

3. **🌟 One-command startup** (recommended):
   ```bash
   make start-all
   ```
   
   **OR manually** (in separate terminals):
   ```bash
   # Install Flutter dependencies
   make flutter-setup
   
   # Start the API server
   make api-server
   
   # Run Flutter app (in another terminal)
   make flutter-web
   ```

---

## 🟢 Usage

### Backend Only
Run the Python monitoring script:

```bash
make run
```

### 🌟 Full System (Recommended)
**One command to start everything:**
```bash
make start-all
```

**To stop everything:**
```bash
make stop-all
```

### Manual Setup (Alternative)
1. **Start the Python monitoring** (Terminal 1):
   ```bash
   make run
   ```

2. **Start the API server** (Terminal 2):
   ```bash
   make api-server
   ```

3. **Launch Flutter frontend** (Terminal 3):
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
The Python monitor logs ping values to terminal and `ping_results.csv`. During alert events, notifications (email, desktop pop-ups, audible alerts) are triggered for immediate issue awareness.

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

## 🗂 Logging Results 

Ping records are logged into `ping_results.csv`, structured clearly:

Example:
2025-03-11 13:52:48,21.579,0 2025-03-11 13:58:26,3458.861,0 2025-03-11 14:10:26,5566.672,0 2025-03-11 14:30:08,23.563,1 2025-03-11 14:30:28,24.035,3 ...


- **warnings** count consecutive pings above your defined threshold.
- Actual timestamps provide clear records of ping performance and historical data.

---

## 📥 Project Structure

```
PingMonitor/
├── Backend (Python)
│   ├── .venv/                 # Virtual environment
│   ├── PingMonitor.py         # Main monitoring script
│   ├── csv_server.py          # HTTP API server
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment configuration
│   ├── sample.env             # Sample configuration
│   ├── ping_results.csv       # Generated monitoring data
│   └── alert.mp3              # Alert sound file
│
├── Frontend (Flutter)
│   ├── pingmonitorflutter/
│   │   ├── lib/
│   │   │   ├── main.dart      # App entry point
│   │   │   ├── models/        # Data models
│   │   │   ├── screens/       # UI screens
│   │   │   ├── services/      # API services
│   │   │   └── widgets/       # Reusable components
│   │   ├── pubspec.yaml       # Flutter dependencies
│   │   └── web/               # Web platform files
│
├── Makefile                   # Build automation
├── README.md                  # This file
└── LICENSE                    # MIT License
```
---

## 🌐 API Endpoints

The HTTP API server provides the following endpoints for frontend integration:

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/health` | GET | Health check and system status | None |
| `/ping-data` | GET | Retrieve ping monitoring data | `url` (filter), `limit` (count) |
| `/url-statuses` | GET | Aggregated status for all URLs | None |
| `/env-config` | GET | Current .env configuration | None |
| `/env-config` | POST | Update .env configuration | JSON body with config |

**Example Usage:**
```bash
# Get health status
curl http://localhost:8000/health

# Get recent ping data for specific URL
curl "http://localhost:8000/ping-data?url=google.com&limit=10"

# Get all URL statuses
curl http://localhost:8000/url-statuses

# Get current configuration
curl http://localhost:8000/env-config
```

---

## ✅ Supported Platforms

### Backend (Python)
- 🟢 **macOS**
- 🟢 **Linux (notify2 library)**
- 🟢 **Windows (win10toast library)**

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

🎉 **Thank you for using Ping Monitor! Please reach out if you have any questions, found any bugs, or have some features you'd like to see. Happy Monitoring.**
