import logging
import logging.config
from typing import Any, Dict, List

import colorlog

from .configs import FormatterConfig, HandlerConfig, LoggerConfig
from .formatters import JsonFormatter


class BaseLoggingConfig:
    """
    Базовая конфигурация логгера, состоящая из экземпляров классов для форматтеров и обработчиков.
    """

    version: int = 1
    disable_existing_logger: bool = False

    formatters: List[FormatterConfig] = [
        FormatterConfig(
            name="json",
            formatter_type=JsonFormatter,
            datefmt='%Y-%m-%d %H:%M:%S %z',
        ),
        FormatterConfig(
            name="generic",
            formatter_type=colorlog.ColoredFormatter,
            format="{log_color}{asctime} - {name} - {levelname} - {message}",
            datefmt="%Y-%m-%d %H:%M:%S %z",
            defaults={
                'log_colors': {
                    'DEBUG': 'bold_cyan',
                    'INFO': 'bold_green',
                    'WARNING': 'bold_yellow',
                    'ERROR': 'bold_red',
                    'CRITICAL': 'bold_red,bg_white',
                }
            },
        ),
        FormatterConfig(
            name="access",
            formatter_type=colorlog.ColoredFormatter,
            format="{light_purple}{asctime} - {message}",
        ),
    ]

    handlers: List[HandlerConfig] = [
        HandlerConfig(
            name="console_json",
            formatter="json",
            class_=logging.StreamHandler,
        ),
        HandlerConfig(
            name="console_generic",
            formatter="generic",
            class_=logging.StreamHandler,
        ),
        HandlerConfig(
            name="console_access",
            formatter="access",
            class_=logging.StreamHandler,
            level="INFO"
        ),
    ]

    loggers: List[LoggerConfig] = []

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Возвращает сконфигурированный словарь для настройки логгера.
        """
        formatters = {}
        for formatter in self.formatters:
            formatters.update(formatter.get_config())

        handlers = {}
        for handler in self.handlers:
            handlers.update(handler.get_config())

        loggers = {}
        for logger in self.loggers:
            loggers.update(logger.get_config())

        return {
            "version": self.version,
            "disable_existing_loggers": self.disable_existing_logger,
            "formatters": formatters,
            "handlers": handlers,
            "loggers": loggers,
        }

    def setup_logging(self):
        """
        Настраивает логгирование, используя текущую конфигурацию.
        """
        logging_config = self.get_logging_config()
        logging.config.dictConfig(logging_config)
