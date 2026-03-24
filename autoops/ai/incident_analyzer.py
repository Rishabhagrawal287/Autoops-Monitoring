import json

class IncidentAnalyzer:

    def __init__(self, logger):
        self.logger = logger

    def analyze(self, metrics, alerts):
        """
        Perform basic incident analysis based on metrics and alerts
        """

        analysis = {
            "severity": "LOW",
            "possible_root_cause": None,
            "recommendation": None
        }

        try:

            cpu = metrics.get("cpu_usage", 0)
            memory = metrics.get("memory_usage", 0)
            disk = metrics.get("disk_usage", 0)

            if cpu > 90:
                analysis["severity"] = "CRITICAL"
                analysis["possible_root_cause"] = "High CPU utilization"
                analysis["recommendation"] = "Investigate running processes and scale compute resources"

            elif memory > 85:
                analysis["severity"] = "HIGH"
                analysis["possible_root_cause"] = "Memory exhaustion"
                analysis["recommendation"] = "Restart memory heavy services or increase memory"

            elif disk > 90:
                analysis["severity"] = "HIGH"
                analysis["possible_root_cause"] = "Disk nearly full"
                analysis["recommendation"] = "Clean temporary files or expand disk capacity"

            elif alerts:
                analysis["severity"] = "MEDIUM"
                analysis["possible_root_cause"] = "System threshold alerts detected"
                analysis["recommendation"] = "Review alerts and monitor system closely"

            return analysis

        except Exception as e:
            self.logger.error(f"Incident analysis failed: {e}")
            return analysis