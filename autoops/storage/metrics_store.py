import json
import os


class MetricsStore:

    def __init__(self, file_path="metrics_history.json"):
        self.file_path = file_path

    def save(self, metrics):

        history = self.load()

        history.append([
            metrics.get("cpu_usage", 0),
            metrics.get("memory_usage", 0),
            metrics.get("disk_usage", 0)
        ])

        with open(self.file_path, "w") as f:
            json.dump(history, f)

    def load(self):

        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path) as f:
            return json.load(f)