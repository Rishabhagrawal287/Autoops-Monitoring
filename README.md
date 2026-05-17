# AutoOps — Real-Time Infrastructure Monitoring Platform

> Production-grade, self-hosted server monitoring with AI-powered anomaly detection, auto-healing, JWT authentication, multi-server support, and a live React dashboard deployed on Netlify.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-green)
![React](https://img.shields.io/badge/React-18-61dafb)
![Docker](https://img.shields.io/badge/Docker-ready-2496ed)
![Netlify](https://img.shields.io/badge/Netlify-deployed-00c7b7)

**Live Demo:** https://lighthearted-begonia-4340cd.netlify.app

---

## Screenshots

| Dark Theme | Light Theme |
|---|---|
| ![Dark](docs/screenshots/dashboard-dark.png) | ![Light](docs/screenshots/dashboard-light.png) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AutoOps Platform                         │
│                                                                 │
│   ┌──────────────┐        ┌─────────────────┐                  │
│   │ Remote Agent │─POST──▶│  FastAPI        │◀── Prometheus    │
│   │  (agent.py)  │ /ingest│  Backend        │    (port 9090)   │
│   │ Win Service  │        │  (Docker)       │                  │
│   └──────────────┘        │                 │                  │
│                            │  JWT Auth       │                  │
│   ┌──────────────┐  psutil │  Rate Limiting  │                  │
│   │  Local Host  │────────▶│  Anomaly Det.   │                  │
│   └──────────────┘         │  Auto-Healing   │                  │
│                            └────────┬────────┘                  │
│                                     │                           │
│                            ┌────────▼────────┐                  │
│                            │  SQLite DB      │                  │
│                            │  (SQLAlchemy)   │                  │
│                            │  Alerts Table   │                  │
│                            │  Healing Table  │                  │
│                            │  Status Table   │                  │
│                            └────────┬────────┘                  │
│                                     │                           │
│                            ┌────────▼────────┐                  │
│                            │  WebSocket      │                  │
│                            │  /ws/{server}   │                  │
│                            └────────┬────────┘                  │
│                                     │                           │
│                   ngrok tunnel      │                           │
│                   (public URL) ─────┘                           │
│                            ┌────────▼────────┐                  │
│                            │  React Dashboard│                  │
│                            │  Netlify CDN    │                  │
│                            │  Dark/Light     │                  │
│                            └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

| Feature | Details |
|---|---|
| **Real-time Monitoring** | CPU, Memory, Disk streamed via WebSocket every 2 seconds |
| **JWT Authentication** | Login-protected dashboard and API endpoints |
| **Rate Limiting** | 60 requests/minute per IP on `/ingest` via slowapi |
| **Multi-Server Support** | Distributed agents POST metrics; switch servers in UI |
| **AI Anomaly Detection** | Z-score analysis over 50-sample rolling window |
| **Auto-Healing** | Automatic remediation for CPU > 80%, Memory > 92%, Disk > 90% |
| **Persistent Storage** | Alerts and healing actions saved to SQLite, survive restarts |
| **Historical Data** | Filterable by 1H / 6H / 24H / All with up to 500 records |
| **Offline Detection** | 🟢/🔴 server status — offline if no data for 30+ seconds |
| **All-Servers Overview** | Grid view showing all servers with live metric bars |
| **Dark/Light Theme** | Persistent theme toggle saved in localStorage |
| **Alert Sound** | Browser audio notification on new alerts |
| **Prometheus Export** | `/prometheus-metrics` endpoint for Grafana integration |
| **Grafana Dashboards** | CPU, Memory, Disk gauge panels with color thresholds |
| **Docker Deployment** | Single `docker-compose up -d` starts the full backend |
| **Netlify Frontend** | React dashboard deployed to global CDN |
| **Windows Service** | Agent runs as auto-starting Windows Service via pywin32 |
| **Agent Retry Backoff** | Exponential backoff (5s → 10s → 20s → 60s max) on failure |
| **Structured Logging** | File-rotating logger with INFO/ERROR levels |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.12) |
| Authentication | JWT via python-jose + passlib/bcrypt |
| Rate Limiting | slowapi |
| System Metrics | psutil |
| Anomaly Detection | NumPy (rolling Z-score) |
| Database | SQLite via SQLAlchemy |
| Real-time Transport | WebSockets (FastAPI native) |
| Metrics Export | prometheus_client |
| Frontend Framework | React 18 + Vite |
| Charts | Recharts |
| Styling | Custom CSS (dark/light theme) |
| Containerization | Docker + Docker Compose |
| Frontend Hosting | Netlify |
| Tunnel (dev) | ngrok |
| Monitoring | Prometheus + Grafana |
| Distributed Agents | Python requests + pywin32 |

---

## Project Structure

```
AutoOps/
├── autoops/
│   ├── api/
│   │   ├── server.py          # FastAPI backend — all endpoints & WebSocket
│   │   ├── database.py        # SQLAlchemy engine + session factory
│   │   ├── models.py          # Metrics, Alert, HealingAction, ServerStatus ORM models
│   │   ├── auth.py            # JWT authentication logic
│   │   └── agent.py           # Distributed agent with retry backoff + auth
│   │   └── agent_service.py   # Windows Service wrapper for agent
│   └── core/
│       ├── monitor.py         # SystemMonitor class
│       ├── metrics.py         # collect_metrics helper
│       ├── config.py          # Loads thresholds from config.yaml
│       ├── logger.py          # File-rotating singleton logger
│       └── exceptions.py      # Custom exception types
├── autoops-dashboard/
│   └── src/
│       ├── App.jsx            # Main dashboard — auth, WebSocket, views
│       ├── App.css            # Dark/light theme stylesheet
│       ├── alert.mp3          # Alert sound
│       └── components/
│           ├── CPUChart.jsx
│           ├── MemoryChart.jsx
│           ├── DiskChart.jsx
│           ├── HistoryChart.jsx
│           └── ServerGrid.jsx # All-servers overview grid
├── Dockerfile                 # Backend container definition
├── docker-compose.yml         # Container orchestration
├── config.yaml                # Alert threshold configuration
├── requirements.txt
├── docs/
│   ├── architecture.png
│   └── screenshots/
└── .gitignore
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker Desktop

### Option A — Run with Docker (recommended)

```bash
# Clone the repo
git clone https://github.com/Rishabhagrawal287/Autoops-Monitoring-Dashboard.git
cd Autoops-Monitoring-Dashboard

# Build and start the backend
docker build -t autoops-backend .
docker-compose up -d

# Verify it's running
curl http://localhost:8000/health
# → {"status":"AutoOps running"}
```

### Option B — Run manually

```bash
# Backend
cd autoops/api
pip install -r ../../requirements.txt
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd autoops-dashboard
npm install
npm run dev
# Open http://localhost:5173
```

**Default credentials:** `admin` / `secret`

---

## Configuration

Edit `config.yaml` to tune thresholds:

```yaml
thresholds:
  cpu_warning:      70
  cpu_critical:     90
  memory_warning:   80
  memory_critical:  92
  disk_warning:     75
  disk_critical:    90

collection_interval_seconds: 2
history_limit: 100
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/token` | ❌ | Login — returns JWT token |
| `GET` | `/health` | ❌ | Health check |
| `GET` | `/` | ❌ | API status |
| `GET` | `/metrics` | ✅ | Live metrics for host server |
| `GET` | `/history` | ✅ | Records filtered by server + range |
| `GET` | `/servers` | ✅ | List servers with online/offline status |
| `GET` | `/server/{name}` | ✅ | Last 100 records for a server |
| `POST` | `/ingest` | ✅ | Receive metrics from remote agent (60/min limit) |
| `GET` | `/prometheus-metrics` | ❌ | Prometheus text-format export |
| `WS` | `/ws/{server_name}` | ❌ | Live WebSocket stream |

### Login Example

```bash
curl -X POST http://localhost:8000/token \
  -d "username=admin&password=secret"
# → {"access_token": "eyJ...", "token_type": "bearer"}
```

### Authenticated Request Example

```bash
curl http://localhost:8000/metrics \
  -H "Authorization: Bearer eyJ..."
```

---

## Remote Agent Setup

Copy `autoops/api/agent.py` to each remote server, update the credentials, and run:

```bash
pip install psutil requests
python agent.py
```

### Run as Windows Service

```powershell
# Install
python agent_service.py install
python agent_service.py start

# Check status
Get-Service -Name "AutoOpsAgent"

# Stop / Remove
python agent_service.py stop
python agent_service.py remove
```

---

## Prometheus + Grafana

**prometheus.yml:**

```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "autoops"
    metrics_path: "/prometheus-metrics"
    static_configs:
      - targets: ["localhost:8000"]
```

**Exposed gauges:**

| Gauge | Description |
|---|---|
| `autoops_cpu_usage` | CPU usage % |
| `autoops_memory_usage` | Memory usage % |
| `autoops_disk_usage` | Disk usage % |

---

## Auto-Healing Logic

| Trigger | Threshold | Action |
|---|---|---|
| High CPU | > 80% | Restart high CPU process |
| High Memory | > 92% | Clear page cache, restart services |
| High Disk | > 90% | Purge temp files, rotate logs |

All actions are persisted to the database and displayed in the dashboard.

---

## Deployment

### Backend (Docker)

```bash
docker-compose up -d        # Start
docker-compose down         # Stop
docker logs autoops-backend # View logs
```

### Frontend (Netlify)

```bash
cd autoops-dashboard
npm run build
# Drag dist/ folder to https://app.netlify.com/drop
```

Set environment variable in Netlify:
- `VITE_API_URL` = your backend public URL

### Public Tunnel (development)

```bash
ngrok http 8000
# Use the generated https:// URL as VITE_API_URL
```

---

## Docker Commands Reference

```bash
docker ps                          # Check running containers
docker logs autoops-backend -f     # Live logs
docker-compose restart             # Restart
docker build --no-cache -t autoops-backend .  # Force rebuild
```

---

## License

MIT © 2026 Rishabh Agrawal

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.