import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import time
import psutil
import requests

# ── Configuration — must match agent.py ───────────────────────
SERVER_NAME  = socket.gethostname()
API_BASE     = "http://127.0.0.1:8000"
INGEST_URL   = f"{API_BASE}/ingest"
TOKEN_URL    = f"{API_BASE}/token"
INTERVAL     = 5
USERNAME     = "admin"
PASSWORD     = "secret"
RETRY_INITIAL  = 5
RETRY_MAX      = 60
RETRY_BACKOFF  = 2

token = None

def get_token():
    global token
    wait = RETRY_INITIAL
    while True:
        try:
            response = requests.post(TOKEN_URL, data={
                "username": USERNAME,
                "password": PASSWORD
            }, timeout=5)
            if response.status_code == 200:
                token = response.json()["access_token"]
                servicemanager.LogInfoMsg(f"AutoOps Agent authenticated successfully")
                return
        except Exception as e:
            servicemanager.LogWarningMsg(f"AutoOps Agent auth failed: {e} — retrying in {wait}s")
        time.sleep(wait)
        wait = min(wait * RETRY_BACKOFF, RETRY_MAX)

def collect_metrics():
    return {
        "server_name": SERVER_NAME,
        "cpu":    psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk":   psutil.disk_usage('/').percent
    }

def send_metrics(data):
    global token
    wait = RETRY_INITIAL
    while True:
        try:
            response = requests.post(
                INGEST_URL,
                json=data,
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            if response.status_code == 200:
                return
            elif response.status_code == 401:
                get_token()
                wait = RETRY_INITIAL
            else:
                time.sleep(wait)
                wait = min(wait * RETRY_BACKOFF, RETRY_MAX)
        except Exception:
            time.sleep(wait)
            wait = min(wait * RETRY_BACKOFF, RETRY_MAX)


class AutoOpsAgentService(win32serviceutil.ServiceFramework):
    _svc_name_         = "AutoOpsAgent"
    _svc_display_name_ = "AutoOps Monitoring Agent"
    _svc_description_  = "Sends system metrics to the AutoOps monitoring platform"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False
        servicemanager.LogInfoMsg("AutoOps Agent service stopping")

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("AutoOps Agent service starting")
        get_token()
        while self.running:
            metrics = collect_metrics()
            send_metrics(metrics)
            # Check stop event every second during the sleep interval
            for _ in range(INTERVAL):
                if not self.running:
                    break
                time.sleep(1)
        servicemanager.LogInfoMsg("AutoOps Agent service stopped")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AutoOpsAgentService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AutoOpsAgentService)