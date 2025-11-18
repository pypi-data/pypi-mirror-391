"""Logging configuration for Neuron CLI"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "neuron-cli",
    level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """Setup and configure logger"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # More verbose in file
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Default logger instance
logger = setup_logger(
    log_file=Path.home() / ".neuron" / "agent.log"
)
