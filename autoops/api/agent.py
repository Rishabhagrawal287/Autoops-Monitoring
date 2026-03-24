import psutil
import requests
import time
import socket

SERVER_NAME = socket.gethostname()
AUTOOPS_API = "http://127.0.0.1:8000/ingest"

INTERVAL = 5


def collect_metrics():

    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    return {
        "server_name": SERVER_NAME,
        "cpu": cpu,
        "memory": memory,
        "disk": disk
    }


def send_metrics(data):

    try:

        response = requests.post(
            AUTOOPS_API,
            json=data,
            timeout=5
        )

        if response.status_code == 200:
            print(f"[{SERVER_NAME}] metrics sent")

    except Exception as e:

        print(f"[{SERVER_NAME}] failed to send metrics:", e)


while True:

    metrics = collect_metrics()

    send_metrics(metrics)

    time.sleep(INTERVAL)