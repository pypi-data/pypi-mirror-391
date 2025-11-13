import logging.config
from typing import Type, Optional, Any, Dict, Literal


class FormatterConfig:
    """
    Конфигурация для форматтера.
    """

    def __init__(
        self,
        name: str,
        format: Optional[str] = None,
        style: Literal['%', '{', '$'] = '{',
        datefmt: str = '%Y-%m-%d %H:%M:%S %z',
        validate: bool = True,
        defaults: Optional[Dict[str, Any]] = None,
        formatter_type: Optional[Type[logging.Formatter]] = None
    ):
        self.name = name
        self.format = format
        self.style = style
        self.datefmt = datefmt
        self.validate = validate
        self.defaults = defaults or {}
        self.formatter_type = formatter_type

    def get_config(self) -> Dict[str, Dict[str, Any]]:
        config = {
            "format": self.format,
            "style": self.style,
            "datefmt": self.datefmt,
            "validate": self.validate,
            **self.defaults,
        }
        if self.formatter_type:
            config["()"] = self.formatter_type
        return {self.name: config}


class HandlerConfig:
    """
    Конфигурация для обработчика.
    """

    def __init__(
        self,
        name: str,
        formatter: str,
        level: str = "DEBUG",
        class_: Type[logging.Handler] = logging.StreamHandler,
        filename: Optional[str] = None,
        mode: Optional[str] = None,
        **kwargs: Any
    ):
        self.name = name
        self.formatter = formatter
        self.level = level
        self.class_ = class_
        self.filename = filename
        self.mode = mode
        self.kwargs = kwargs

    def get_config(self) -> Dict[str, Dict[str, Any]]:
        config = {
            "class": f"{self.class_.__module__}.{self.class_.__name__}",
            "level": self.level,
            "formatter": self.formatter,
            **self.kwargs,
        }
        if self.filename:
            config["filename"] = self.filename
        if self.mode:
            config["mode"] = self.mode
        return {self.name: config}


class LoggerConfig:
    """
    Конфигурация для логгера.
    """

    def __init__(
        self,
        name: str,
        level: str = "DEBUG",
        handlers: Optional[list[str]] = None,
        propagate: bool = True,
        **kwargs: Any
    ):
        self.name = name
        self.level = level
        self.handlers = handlers or []
        self.propagate = propagate
        self.kwargs = kwargs

    def get_config(self) -> Dict[str, Dict[str, Any]]:
        return {
            self.name: {
                "level": self.level,
                "handlers": self.handlers,
                "propagate": self.propagate,
                **self.kwargs,
            }
        }
