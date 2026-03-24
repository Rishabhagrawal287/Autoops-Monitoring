import argparse
from autoops.core.logger import Logger
from autoops.core.monitor import SystemMonitor
from autoops.core.config import Config


def main():
    parser = argparse.ArgumentParser(description="AutoOps Automation Tool")
    parser.add_argument("--monitor", action="store_true", help="Run system monitor")

    args = parser.parse_args()

    config = Config()

    logger = Logger(
        level=config.get("logger", "level", "INFO"),
        max_size_mb=config.get("logger", "max_size_mb", 5),
        console=config.get("logger", "console", True)
    )

    monitor = SystemMonitor(logger)

    if args.monitor:
        monitor.generate_report()


if __name__ == "__main__":
    main()