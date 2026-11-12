import logging
import logging.handlers
import sys
from typing import TextIO

import structlog

from my_lib.logs.settings import LogSettings


class _AppFileHandler(logging.handlers.RotatingFileHandler):
    """Mark file handlers for replacement when logging is reconfigured."""


class _AppConsoleHandler(logging.StreamHandler[TextIO]):
    """Mark console handlers for replacement when logging is reconfigured."""


def _prepare_handlers(
    config: LogSettings,
    console_formatter: logging.Formatter,
    json_processors: list[structlog.types.Processor],
    shared_processors: list[structlog.types.Processor],
) -> list[logging.Handler]:
    """Create all handlers before touching the root logger, closing them if one fails."""
    handlers: list[logging.Handler] = []
    try:
        sh = _AppConsoleHandler(sys.stderr)
        sh.setLevel(config.console_level)
        sh.setFormatter(console_formatter)
        handlers.append(sh)

        if config.dir is not None:
            logs_dir_path = config.dir.resolve()
            logs_dir_path.mkdir(parents=True, exist_ok=True)
            fh = _AppFileHandler(
                filename=logs_dir_path / config.file_name,
                maxBytes=config.file_max_bytes,
                backupCount=config.file_backup_count,
            )
            fh.setLevel(config.file_level)
            fh.setFormatter(
                structlog.stdlib.ProcessorFormatter(
                    processors=json_processors, foreign_pre_chain=shared_processors
                )
            )
            handlers.append(fh)
    except Exception:
        for handler in handlers:
            handler.close()
        raise
    return handlers


def setup_logging(config: LogSettings | None = None) -> None:
    """Configure structlog and stdlib handlers for an application that uses the library."""
    if config is None:
        config = LogSettings()

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    # Only JSON output formats exceptions as text; ConsoleRenderer renders exc_info itself.
    json_processors: list[structlog.types.Processor] = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]

    console_processors: list[structlog.types.Processor] = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.dev.ConsoleRenderer(),
    ]
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processors=json_processors if config.format == "json" else console_processors,
        foreign_pre_chain=shared_processors,
    )

    handlers = _prepare_handlers(config, console_formatter, json_processors, shared_processors)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, (_AppFileHandler, _AppConsoleHandler)):
            root_logger.removeHandler(handler)
            handler.close()

    for handler in handlers:
        root_logger.addHandler(handler)
    root_logger.setLevel(config.level)

    structlog.configure(
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
