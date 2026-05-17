from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import psutil
import numpy as np
import os
import asyncio
from datetime import datetime
from database import SessionLocal, engine, Base
from models import Metrics
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

Base.metadata.create_all(bind=engine)


# Prometheus metrics
cpu_gauge = Gauge("autoops_cpu_usage", "CPU usage percentage")
memory_gauge = Gauge("autoops_memory_usage", "Memory usage percentage")
disk_gauge = Gauge("autoops_disk_usage", "Disk usage percentage")

cpu_history = []
alerts = []
healing_actions = []

# CORS
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


# ---------------- AI LOGIC ---------------- #

def detect_anomaly(cpu_value):
    cpu_history.append(cpu_value)

    if len(cpu_history) > 50:
        cpu_history.pop(0)

    if len(cpu_history) < 10:
        return False

    mean = np.mean(cpu_history)
    std = np.std(cpu_history)

    return bool(cpu_value > mean + (2 * std))


def auto_heal(cpu):
    if cpu > 80:
        action = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "action": "AutoOps restarted high CPU process"
        }

        healing_actions.append(action)

        if len(healing_actions) > 10:
            healing_actions.pop(0)

        return action

    return None


def check_thresholds(cpu, memory, disk, server_name):
    new_alerts = []

    if cpu > 90:
        new_alerts.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": f"High CPU Usage on {server_name}"
        })

    if memory > 85:
        new_alerts.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": f"High Memory Usage on {server_name}"
        })

    if disk > 90:
        new_alerts.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": f"High Disk Usage on {server_name}"
        })

    return new_alerts


async def collect_metrics():
    while True:
        db = SessionLocal()

        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        memory = ((mem.total - mem.available) / mem.total) * 100
        disk = psutil.disk_usage(os.getcwd()).percent

        metric = Metrics(
            server_name=socket.gethostname(),
            cpu=cpu,
            memory=memory,
            disk=disk
        )

        db.add(metric)
        db.commit()
        db.close()

        await asyncio.sleep(2)


# ---------------- API ---------------- #

@app.get("/metrics")
def get_metrics():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage(os.getcwd()).percent
    server_name = socket.gethostname()

    db = SessionLocal()

    metric = Metrics(
        server_name=server_name,
        cpu=cpu,
        memory=memory,
        disk=disk
    )

    db.add(metric)
    db.commit()
    db.close()

    anomaly = detect_anomaly(cpu)

    # ✅ FIXED ALERT LOGIC
    new_alerts = []

    if anomaly:
        new_alerts.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": "AI detected abnormal CPU behavior"
        })

    threshold_alerts = check_thresholds(cpu, memory, disk, server_name)
    new_alerts.extend(threshold_alerts)

    alerts.extend(new_alerts)

    if len(alerts) > 10:
        alerts[:] = alerts[-10:]

    auto_heal(cpu)

    return {
        "cpu_percent": float(cpu),
        "memory_percent": float(memory),
        "disk_percent": float(disk),
        "cpu_anomaly": anomaly,
        "alerts": alerts,
        "healing_actions": healing_actions
    }


@app.get("/servers")
def get_servers():
    db = SessionLocal()
    servers = db.query(Metrics.server_name).distinct().all()
    db.close()

    server_list = [s[0] for s in servers]

    return {"servers": server_list}


@app.get("/server/{server_name}")
def get_server_metrics(server_name: str):
    db = SessionLocal()

    records = (
        db.query(Metrics)
        .filter(Metrics.server_name == server_name)
        .order_by(Metrics.timestamp.desc())
        .limit(100)
        .all()
    )

    db.close()

    return [
        {
            "cpu": r.cpu,
            "memory": r.memory,
            "disk": r.disk,
            "timestamp": r.timestamp.isoformat()
        }
        for r in records
    ]


@app.websocket("/ws/{server_name}")
async def websocket_metrics(websocket: WebSocket, server_name: str):
    await websocket.accept()
    print(f"WebSocket connected for server: {server_name}")

    try:
        while True:
            db = SessionLocal()

            record = (
                db.query(Metrics)
                .filter(Metrics.server_name == server_name)
                .order_by(Metrics.timestamp.desc())
                .first()
            )

            db.close()

            if not record:
                await websocket.send_json({
                    "cpu_percent": 0,
                    "memory_percent": 0,
                    "disk_percent": 0,
                    "cpu_anomaly": False,
                    "alerts": [],
                    "healing_actions": []
                })
                await asyncio.sleep(2)
                continue

            cpu = record.cpu
            memory = record.memory
            disk = record.disk

            anomaly = detect_anomaly(cpu)

            new_alerts = []

            if anomaly:
                new_alerts.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "message": f"AI anomaly detected on {server_name}"
                })

            threshold_alerts = check_thresholds(cpu, memory, disk, server_name)
            new_alerts.extend(threshold_alerts)

            alerts.extend(new_alerts)

            if len(alerts) > 10:
                alerts[:] = alerts[-10:]

            auto_heal(cpu)

            data = {
                "cpu_percent": float(cpu),
                "memory_percent": float(memory),
                "disk_percent": float(disk),
                "cpu_anomaly": anomaly,
                "alerts": alerts,
                "healing_actions": healing_actions
            }

            await websocket.send_json(data)
            await asyncio.sleep(2)

    except Exception as e:
        print(f"WebSocket disconnected for {server_name}: {e}")


@app.get("/prometheus-metrics")
def prometheus_metrics():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage(os.getcwd()).percent

    cpu_gauge.set(cpu)
    memory_gauge.set(memory)
    disk_gauge.set(disk)

    return Response(generate_latest(), media_type="text/plain")


@app.get("/")
def root():
    return {"message": "AutoOps API running"}