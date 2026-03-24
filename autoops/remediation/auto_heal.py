import os


class AutoHealer:

    def __init__(self, logger):
        self.logger = logger

    def remediate(self, alerts):

        actions = []

        for alert in alerts:

            alert_lower = alert.lower()

            if "cpu" in alert_lower:
                self.logger.info("Attempting CPU remediation")
                os.system("echo Simulated CPU process cleanup")
                actions.append("CPU cleanup attempted")

            if "memory" in alert_lower:
                self.logger.info("Attempting memory cleanup")
                os.system("echo Simulated memory cleanup")
                actions.append("Memory cleanup attempted")

            if "disk" in alert_lower:
                self.logger.info("Checking disk cleanup options")
                os.system("echo Simulated disk cleanup check")
                actions.append("Disk cleanup recommended")

        return actions