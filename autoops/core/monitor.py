import psutil
import json
import os
from datetime import datetime

from autoops.core.exceptions import MonitoringError
from autoops.core.metrics import collect_metrics
from autoops.alerts.alert_manager import AlertManager
from autoops.core.config import Config
from autoops.remediation.auto_heal import AutoHealer
from autoops.ai.incident_analyzer import IncidentAnalyzer
from autoops.logs.log_analyzer import LogAnalyzer


class SystemMonitor:

    def __init__(self, logger, report_dir="reports"):
        self.logger = logger
        self.report_dir = report_dir
        self._ensure_report_directory()

        self.config = Config()
        self.alert_manager = AlertManager(self.logger, self.config)
        self.auto_healer = AutoHealer(self.logger)
        self.incident_analyzer = IncidentAnalyzer(self.logger)
        self.loganalyzer = LogAnalyzer(self.logger)

    def _ensure_report_directory(self):
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def generate_report(self):
        try:
            metrics = collect_metrics()
            log_analysis = self.log_analyzer.analyze_logs()
            self.logger.debug("System metrics collected successfully.")

            alerts = self.alert_manager.check_alerts(metrics)
            actions = self.auto_healer.remediate(alerts)
            analysis = self.incident_analyzer.analyze(metrics, alerts)

            filename = f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.report_dir, filename)

            report = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "metrics": metrics,
                "log_analysis": log_analysis,
                "alerts": alerts,
                "actions": actions
            }

            with open(filepath, "w") as file:
                json.dump(report, file, indent=4)

            self.logger.info(f"Report generated at {filepath}")

            return filepath

        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            raise MonitoringError(str(e))


# -------- EXECUTION ENTRY POINT --------

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger("AutoOps")

    monitor = SystemMonitor(logger)
    monitor.generate_report()