import schedule
import time


class Scheduler:

    def __init__(self, monitor, interval, logger):
        self.monitor = monitor
        self.interval = interval
        self.logger = logger

    def start(self):

        self.logger.info(f"Starting monitoring scheduler (every {self.interval} seconds)")

        schedule.every(self.interval).seconds.do(self.monitor.generate_report)

        while True:
            schedule.run_pending()
            time.sleep(1)