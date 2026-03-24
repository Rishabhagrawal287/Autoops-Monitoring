import unittest
from autoops.core.logger import Logger
from autoops.core.monitor import SystemMonitor


class TestMonitor(unittest.TestCase):

    def test_collect_metrics(self):
        logger = Logger(console=False)
        monitor = SystemMonitor(logger)

        metrics = monitor.collect_metrics()

        self.assertIn("cpu_percent", metrics)
        self.assertIn("memory_percent", metrics)
        self.assertIn("disk_percent", metrics)


if __name__ == "__main__":
    unittest.main()