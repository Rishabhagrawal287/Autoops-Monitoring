class AutoOpsError(Exception):
    """Base exception for AutoOps"""


class MonitoringError(AutoOpsError):
    """Raised when system monitoring fails"""


class LoggingError(AutoOpsError):
    """Raised when logging fails"""