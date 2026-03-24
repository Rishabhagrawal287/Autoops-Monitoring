import psutil
from datetime import datetime


def collect_metrics():

    metrics = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return metrics