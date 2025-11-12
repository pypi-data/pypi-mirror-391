import json
import logging
from datetime import datetime
from typing import Optional

_AZURE_ENABLED = False
_logger_provider = None

def _setup_azure_logging(connection_string: str):
    global _AZURE_ENABLED, _logger_provider
    try:
        # Optional OpenTelemetry → Azure Monitor logs
        from opentelemetry.sdk._logs import LoggerProvider
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

        if _logger_provider is None:
            _logger_provider = LoggerProvider()
            _logger_provider.add_log_record_processor(
                BatchLogRecordProcessor(AzureMonitorLogExporter(
                    connection_string=connection_string
                ))
            )
            _AZURE_ENABLED = True
    except Exception:
        # Azure exporter not available; fall back to console-only
        _AZURE_ENABLED = False


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # Optional context passed via logger.*(..., extra={...})
        for k in ("correlation_id", "user_id", "service_name"):
            if hasattr(record, k):
                payload[k] = getattr(record, k)
        return json.dumps(payload, ensure_ascii=False)


class TextronLogger:
    """
    Minimal, uniform logger for Textron apps.
    Schema: timestamp, level, message, correlation_id, user_id, service_name
    """

    def __init__(self,
                 service_name: str,
                 azure_connection_string: Optional[str] = None):
        self.service_name = service_name

        # Console logger
        self._logger = logging.getLogger(f"textron.{service_name}")
        self._logger.setLevel(logging.INFO)

        if not self._logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(_JsonFormatter())
            self._logger.addHandler(h)
            self._logger.propagate = False

        if azure_connection_string:
            _setup_azure_logging(azure_connection_string)

    # ----- public API -----
    def info(self, message: str, user_id: str = None, correlation_id: str = None):
        self._emit(logging.INFO, message, user_id, correlation_id)

    def warning(self, message: str, user_id: str = None, correlation_id: str = None):
        self._emit(logging.WARNING, message, user_id, correlation_id)

    def error(self, message: str, user_id: str = None, correlation_id: str = None):
        self._emit(logging.ERROR, message, user_id, correlation_id)

    # ----- internal -----
    def _emit(self, level: int, message: str, user_id: str, correlation_id: str):
        extra = {
            "service_name": self.service_name,
            "user_id": user_id,
            "correlation_id": correlation_id,
        }
        # Console JSON log
        self._logger.log(level, message, extra=extra)

        # Optional Azure log via OpenTelemetry (if exporter available)
        if _AZURE_ENABLED:
            try:
                from opentelemetry._logs import get_logger_provider
                from opentelemetry._logs.severity import SeverityNumber
                provider = get_logger_provider()
                if provider is None:
                    provider = _logger_provider
                otel_logger = provider.get_logger(self.service_name)
                sev = {logging.INFO: SeverityNumber.INFO,
                       logging.WARNING: SeverityNumber.WARN,
                       logging.ERROR: SeverityNumber.ERROR}.get(level, SeverityNumber.INFO)
                otel_logger.emit(
                    message=message,
                    severity_number=sev,
                    attributes={k: v for k, v in extra.items() if v is not None},
                )
            except Exception:
                # swallow exporter errors—console logs still work
                pass
