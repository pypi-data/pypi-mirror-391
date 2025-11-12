"""Logging configuration for BugBountyCrawler."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json
import hashlib
import re

from .config import Settings


class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from logs."""
    
    def __init__(self):
        """Initialize sensitive data filter."""
        super().__init__()
        
        # Patterns for sensitive data
        self.patterns = [
            # API keys and tokens
            (r'(?i)(api[_-]?key|token|secret|password|auth[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9+/=]{20,})["\']?', r'\1=***REDACTED***'),
            # JWT tokens
            (r'(?i)(jwt|bearer)\s+([a-zA-Z0-9._-]+)', r'\1 ***REDACTED***'),
            # Email addresses
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***'),
            # Credit card numbers
            (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '****-****-****-****'),
            # SSN
            (r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****'),
            # IP addresses (optional - can be enabled for debugging)
            # (r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '***.***.***.***'),
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [(re.compile(pattern), replacement) 
                                 for pattern, replacement in self.patterns]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and redact sensitive data from log record."""
        if hasattr(record, 'msg') and record.msg:
            # Redact sensitive data in the message
            record.msg = self._redact_string(str(record.msg))
        
        if hasattr(record, 'args') and record.args:
            # Redact sensitive data in format arguments
            new_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    new_args.append(self._redact_string(arg))
                else:
                    new_args.append(arg)
            record.args = tuple(new_args)
        
        return True
    
    def _redact_string(self, text: str) -> str:
        """Redact sensitive data from a string."""
        for pattern, replacement in self.compiled_patterns:
            text = pattern.sub(replacement, text)
        return text


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def __init__(self, include_extra: bool = True):
        """Initialize JSON formatter."""
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if requested
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 
                              'msecs', 'relativeCreated', 'thread', 'threadName', 
                              'processName', 'process', 'getMessage', 'exc_info', 
                              'exc_text', 'stack_info']:
                    log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        """Initialize colored formatter."""
        super().__init__(fmt, datefmt)
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(settings: Settings) -> None:
    """Set up logging configuration."""
    
    # Create log directory if it doesn't exist
    if settings.log_file:
        settings.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level))
    
    if settings.log_level == 'DEBUG':
        console_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    else:
        console_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    console_formatter = ColoredFormatter(console_format)
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(SensitiveDataFilter())
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if settings.log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Use JSON format for file logs
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(SensitiveDataFilter())
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('playwright').setLevel(logging.WARNING)
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


class ScanLogger:
    """Specialized logger for scan operations."""
    
    def __init__(self, scan_id: str, settings: Settings):
        """Initialize scan logger."""
        self.scan_id = scan_id
        self.settings = settings
        self.logger = logging.getLogger(f"scan.{scan_id}")
        
        # Create scan-specific log file
        scan_log_file = settings.data_dir / "scans" / f"{scan_id}.log"
        scan_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Add file handler for this scan
        file_handler = logging.FileHandler(scan_log_file)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = JSONFormatter()
        file_handler.setFormatter(formatter)
        file_handler.addFilter(SensitiveDataFilter())
        
        self.logger.addHandler(file_handler)
    
    def log_request(self, method: str, url: str, status_code: int, 
                   response_time: float, **kwargs) -> None:
        """Log an HTTP request."""
        self.logger.info(
            "HTTP request",
            extra={
                'scan_id': self.scan_id,
                'method': method,
                'url': url,
                'status_code': status_code,
                'response_time': response_time,
                **kwargs
            }
        )
    
    def log_finding(self, finding_type: str, severity: str, 
                   description: str, **kwargs) -> None:
        """Log a security finding."""
        self.logger.warning(
            "Security finding",
            extra={
                'scan_id': self.scan_id,
                'finding_type': finding_type,
                'severity': severity,
                'description': description,
                **kwargs
            }
        )
    
    def log_error(self, error: str, **kwargs) -> None:
        """Log an error."""
        self.logger.error(
            "Scan error",
            extra={
                'scan_id': self.scan_id,
                'error': error,
                **kwargs
            }
        )
    
    def log_scope_violation(self, target: str, **kwargs) -> None:
        """Log a scope violation attempt."""
        self.logger.error(
            "Scope violation",
            extra={
                'scan_id': self.scan_id,
                'target': target,
                **kwargs
            }
        )

