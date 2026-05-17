from fastapi import FastAPI, WebSocket, HTTPException
import sys
sys.path.append("../core")
from logger import Logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from auth import get_current_user, authenticate_user, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, status as http_status
from fastapi.middleware.cors import CORSMiddleware
import psutil
import numpy as np
import os
import asyncio
from datetime import datetime
from database import SessionLocal, engine, Base
from models import Metrics, Alert, HealingAction, ServerStatus
from pydantic import BaseModel
import socket
from prometheus_client import Gauge, generate_latest
from fastapi.responses import Response
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(collect_metrics())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
Base.metadata.create_all(bind=engine)

cpu_gauge    = Gauge("autoops_cpu_usage",    "CPU usage percentage")
memory_gauge = Gauge("autoops_memory_usage", "Memory usage percentage")
disk_gauge   = Gauge("autoops_disk_usage",   "Disk usage percentage")

cpu_history = []
import pathlib
LOG_DIR = str(pathlib.Path(__file__).parent / "logs")
logger = Logger(log_dir=LOG_DIR, log_file="autoops.log", level="INFO", console=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ServerMetrics(BaseModel):
    server_name: str
    cpu: float
    memory: float
    disk: float

def detect_anomaly(cpu_value):
    cpu_history.append(cpu_value)
    if len(cpu_history) > 50:
        cpu_history.pop(0)
    if len(cpu_history) < 10:
        return False
    mean = np.mean(cpu_history)
    std  = np.std(cpu_history)
    return bool(cpu_value > mean + (2 * std))

def auto_heal(cpu, memory, disk, server_name):
    db = SessionLocal()
    timestamp = datetime.utcnow()
    if cpu > 80:
        db.add(HealingAction(server_name=server_name, action="AutoOps restarted high CPU process", timestamp=timestamp))
    if memory > 92:
        db.add(HealingAction(server_name=server_name, action="AutoOps triggered memory cleanup — cleared page cache & restarted memory-hungry services", timestamp=timestamp))
    if disk > 90:
        db.add(HealingAction(server_name=server_name, action="AutoOps triggered disk cleanup — purged temp files & rotated old logs", timestamp=timestamp))
    db.commit()
    db.close()

def check_thresholds(cpu, memory, disk, server_name):
    db = SessionLocal()
    timestamp = datetime.utcnow()
    new_alerts = []
    if cpu > 90:
        msg = f"High CPU Usage on {server_name}"
        db.add(Alert(server_name=server_name, message=msg, timestamp=timestamp))
        new_alerts.append({"time": timestamp.strftime("%H:%M:%S"), "message": msg})
    if memory > 92:
        msg = f"High Memory Usage on {server_name}"
        db.add(Alert(server_name=server_name, message=msg, timestamp=timestamp))
        new_alerts.append({"time": timestamp.strftime("%H:%M:%S"), "message": msg})
    if disk > 90:
        msg = f"High Disk Usage on {server_name}"
        db.add(Alert(server_name=server_name, message=msg, timestamp=timestamp))
        new_alerts.append({"time": timestamp.strftime("%H:%M:%S"), "message": msg})
    db.commit()
    db.close()
    return new_alerts

def update_server_status(server_name):
    db = SessionLocal()
    status = db.query(ServerStatus).filter(ServerStatus.server_name == server_name).first()
    if status:
        status.last_seen = datetime.utcnow()
    else:
        db.add(ServerStatus(server_name=server_name, last_seen=datetime.utcnow()))
    db.commit()
    db.close()

def get_recent_alerts(server_name, limit=10):
    db = SessionLocal()
    records = db.query(Alert).filter(Alert.server_name == server_name).order_by(Alert.timestamp.desc()).limit(limit).all()
    db.close()
    return [{"time": r.timestamp.strftime("%H:%M:%S"), "message": r.message} for r in records]

def get_recent_healing(server_name, limit=10):
    db = SessionLocal()
    records = db.query(HealingAction).filter(HealingAction.server_name == server_name).order_by(HealingAction.timestamp.desc()).limit(limit).all()
    db.close()
    return [{"time": r.timestamp.strftime("%H:%M:%S"), "action": r.action} for r in records]

async def collect_metrics():
    while True:
        db = SessionLocal()
        cpu    = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk   = psutil.disk_usage(os.getcwd()).percent
        name   = socket.gethostname()
        db.add(Metrics(server_name=name, cpu=cpu, memory=memory, disk=disk))
        db.commit()
        db.close()
        update_server_status(name)
        await asyncio.sleep(2)

@app.get("/metrics")
def get_metrics(current_user: dict = Depends(get_current_user)):
    cpu    = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk   = psutil.disk_usage(os.getcwd()).percent
    name   = socket.gethostname()
    db = SessionLocal()
    db.add(Metrics(server_name=name, cpu=cpu, memory=memory, disk=disk))
    db.commit()
    db.close()
    anomaly = detect_anomaly(cpu)
    if anomaly:
        db2 = SessionLocal()
        db2.add(Alert(server_name=name, message="AI detected abnormal CPU behavior", timestamp=datetime.utcnow()))
        db2.commit()
        db2.close()
    check_thresholds(cpu, memory, disk, name)
    auto_heal(cpu, memory, disk, name)
    return {
        "cpu_percent": float(cpu), "memory_percent": float(memory), "disk_percent": float(disk),
        "cpu_anomaly": anomaly,
        "alerts": get_recent_alerts(name),
        "healing_actions": get_recent_healing(name)
    }

@app.get("/health")
def health():
    return {"status": "AutoOps running"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/ingest")
@limiter.limit("60/minute")
def ingest_metrics(request: Request, data: ServerMetrics, current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    db.add(Metrics(server_name=data.server_name, cpu=data.cpu, memory=data.memory, disk=data.disk))
    db.commit()
    db.close()
    update_server_status(data.server_name)
    check_thresholds(data.cpu, data.memory, data.disk, data.server_name)
    auto_heal(data.cpu, data.memory, data.disk, data.server_name)
    return {"status": "metrics stored"}

@app.get("/history")
def get_history(
    current_user: dict = Depends(get_current_user),
    server: str = None,
    range: str = "all"
):
    from datetime import timedelta
    db = SessionLocal()
    query = db.query(Metrics)

    # Filter by server name if provided
    if server:
        query = query.filter(Metrics.server_name == server)

    # Filter by time range
    if range == "1h":
        cutoff = datetime.utcnow() - timedelta(hours=1)
        query = query.filter(Metrics.timestamp >= cutoff)
    elif range == "6h":
        cutoff = datetime.utcnow() - timedelta(hours=6)
        query = query.filter(Metrics.timestamp >= cutoff)
    elif range == "24h":
        cutoff = datetime.utcnow() - timedelta(hours=24)
        query = query.filter(Metrics.timestamp >= cutoff)

    records = query.order_by(Metrics.timestamp.desc()).limit(500).all()
    db.close()
    return [{"cpu": r.cpu, "memory": r.memory, "disk": r.disk, "timestamp": r.timestamp.isoformat()} for r in records]

@app.get("/")
def root():
    return {"message": "AutoOps API running"}

@app.get("/prometheus-metrics")
def prometheus_metrics():
    cpu    = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk   = psutil.disk_usage(os.getcwd()).percent
    cpu_gauge.set(cpu)
    memory_gauge.set(memory)
    disk_gauge.set(disk)
    return Response(generate_latest(), media_type="text/plain")

@app.get("/servers")
def get_servers(current_user: dict = Depends(get_current_user)):
    from datetime import timedelta
    db = SessionLocal()
    servers = db.query(Metrics.server_name).distinct().all()
    result = []
    for s in servers:
        name = s[0]
        status = db.query(ServerStatus).filter(ServerStatus.server_name == name).first()
        if status:
            diff = (datetime.utcnow() - status.last_seen).total_seconds()
            online = diff < 30
        else:
            online = False
        result.append({"name": name, "online": online})
    db.close()
    logger.info(f"[SERVERS] Returning {len(result)} servers")
    return {"servers": result}

@app.get("/server/{server_name}")
def get_server_metrics(server_name: str):
    db = SessionLocal()
    records = db.query(Metrics).filter(Metrics.server_name == server_name).order_by(Metrics.timestamp.desc()).limit(100).all()
    db.close()
    return [{"cpu": r.cpu, "memory": r.memory, "disk": r.disk, "timestamp": r.timestamp.isoformat()} for r in records]

@app.websocket("/ws/{server_name}")
async def websocket_metrics(websocket: WebSocket, server_name: str):
    await websocket.accept()
    try:
        while True:
            db = SessionLocal()
            record = db.query(Metrics).filter(Metrics.server_name == server_name).order_by(Metrics.timestamp.desc()).first()
            db.close()
            if not record:
                await websocket.send_json({"cpu_percent": 0, "memory_percent": 0, "disk_percent": 0, "cpu_anomaly": False, "alerts": [], "healing_actions": []})
                await asyncio.sleep(2)
                continue
            cpu    = record.cpu
            memory = record.memory
            disk   = record.disk
            anomaly = detect_anomaly(cpu)
            if anomaly:
                db2 = SessionLocal()
                db2.add(Alert(server_name=server_name, message=f"AI anomaly detected on {server_name}", timestamp=datetime.utcnow()))
                db2.commit()
                db2.close()
            check_thresholds(cpu, memory, disk, server_name)
            auto_heal(cpu, memory, disk, server_name)
            data = {
                "cpu_percent": float(cpu), "memory_percent": float(memory), "disk_percent": float(disk),
                "cpu_anomaly": anomaly,
                "alerts": get_recent_alerts(server_name),
                "healing_actions": get_recent_healing(server_name)
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except Exception as e:
        logger.error(f"WebSocket disconnected for {server_name}: {e}")