class AlertManager:

    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def check_alerts(self, metrics):

        alerts = []

        cpu_threshold = self.config.get("thresholds", "cpu", 90)
        mem_threshold = self.config.get("thresholds", "memory", 90)
        disk_threshold = self.config.get("thresholds", "disk", 95)

        if metrics["cpu_percent"] > cpu_threshold:
            alerts.append("High CPU usage detected")

        if metrics["memory_percent"] > mem_threshold:
            alerts.append("High memory usage detected")

        if metrics["disk_percent"] > disk_threshold:
            alerts.append("Disk usage critical")

        for alert in alerts:
            self.logger.warning(alert)

        return alerts