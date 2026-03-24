import argparse

from autoops.core.monitor import SystemMonitor
from autoops.core.logger import Logger
from autoops.core.config import Config
from autoops.scheduler.scheduler import Scheduler


def main():
    parser = argparse.ArgumentParser(
        prog="autoops",
        description="AutoOps - System Monitoring and Automation Tool"
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("monitor", help="Run system monitoring")
    subparsers.add_parser("report", help="Generate system report")

    subparsers.add_parser("schedule", help="Run automated monitoring")

    args = parser.parse_args()

    # Load configuration
    config = Config()

    # Initialize logger correctly
    logger = Logger(
        level=config.get("logger", "level", "INFO"),
        max_size_mb=config.get("logger", "max_size_mb", 5),
        console=config.get("logger", "console", True)
    )

    # Initialize monitor
    monitor = SystemMonitor(logger)

    if args.command == "monitor":
        monitor.generate_report()

    elif args.command == "report":
        monitor.generate_report()

    elif args.command == "schedule":
        scheduler = Scheduler(monitor, interval=10, logger=logger)
        scheduler.start()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()