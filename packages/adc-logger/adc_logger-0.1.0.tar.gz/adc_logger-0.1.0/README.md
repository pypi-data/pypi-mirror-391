# ADC Logger

A flexible and configurable Python logging library with support for JSON formatting and colored console output.

## Features

- **JSON Logging**: Structured JSON log output with timestamps, log levels, and messages
- **Colored Console Output**: Beautiful colored logging using `colorlog`
- **Flexible Configuration**: Easy-to-use configuration classes for formatters, handlers, and loggers
- **Multiple Formatters**: Support for JSON, generic colored, and access log formats
- **Extensible**: Easy to extend with custom formatters and handlers

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from adc_logger import BaseLoggingConfig
import logging

# Create a custom configuration
config = BaseLoggingConfig()

# Add a logger
from adc_logger.configs import LoggerConfig
config.loggers.append(
    LoggerConfig(
        name="my_app",
        level="INFO",
        handlers=["console_json"]
    )
)

# Setup logging
config.setup_logging()

# Use the logger
logger = logging.getLogger("my_app")
logger.info("Hello, World!")
```

## Configuration

### Formatters

The library provides three built-in formatters:

1. **JSON Formatter**: Outputs structured JSON logs
2. **Generic Formatter**: Colored console output with standard format
3. **Access Formatter**: Simplified format for access logs

### Handlers

Built-in handlers include:
- `console_json`: JSON output to console
- `console_generic`: Colored output to console
- `console_access`: Access log format to console

### Custom Configuration

You can create custom formatters, handlers, and loggers:

```python
from adc_logger.configs import FormatterConfig, HandlerConfig, LoggerConfig

# Custom formatter
custom_formatter = FormatterConfig(
    name="custom",
    format="{asctime} - {name} - {levelname} - {message}",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Custom handler
file_handler = HandlerConfig(
    name="file_handler",
    formatter="json",
    class_=logging.FileHandler,
    filename="app.log"
)

# Custom logger
app_logger = LoggerConfig(
    name="my_app",
    level="DEBUG",
    handlers=["console_json", "file_handler"]
)
```

## Examples

### Basic Usage

```python
from adc_logger import BaseLoggingConfig
import logging

config = BaseLoggingConfig()
config.setup_logging()

logger = logging.getLogger(__name__)
logger.info("Application started")
logger.error("An error occurred")
```

### JSON Logging

```python
from adc_logger import BaseLoggingConfig
from adc_logger.configs import LoggerConfig
import logging

config = BaseLoggingConfig()
config.loggers.append(
    LoggerConfig(
        name="api",
        handlers=["console_json"]
    )
)
config.setup_logging()

logger = logging.getLogger("api")
logger.info("API request received", extra={"user_id": 123, "endpoint": "/users"})
```

### Multiple Handlers

```python
from adc_logger import BaseLoggingConfig
from adc_logger.configs import LoggerConfig, HandlerConfig
import logging

config = BaseLoggingConfig()

# Add file handler
file_handler = HandlerConfig(
    name="file_handler",
    formatter="json",
    class_=logging.FileHandler,
    filename="app.log"
)
config.handlers.append(file_handler)

# Configure logger with multiple handlers
config.loggers.append(
    LoggerConfig(
        name="my_app",
        handlers=["console_generic", "file_handler"]
    )
)

config.setup_logging()
```

## Development

### Project Structure

```
adc_logger/
├── __init__.py      # Main exports
├── main.py          # BaseLoggingConfig class
├── configs.py       # Configuration classes
└── formatters.py    # Custom formatters
```

### Dependencies

- `colorlog>=6.7.0`: For colored console output
- Python 3.8+

## License

MIT License 