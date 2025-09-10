import logging
import sys
from pathlib import Path
from typing import Optional
import logging.handlers

class CustomLogger:
    """Custom logger configuration"""
    
    @staticmethod
    def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Create Formatters
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create file handler if log_file specified
        if log_file:
            # Create logs directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create rotating file handler
            file_handler = logging.handlers.TimedRotatingFileHandler(
                log_file,
                when='midnight',
                interval=1,
                backupCount=7
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        return logger

default_logger = CustomLogger.setup_logger(
    'question_answering',
    log_file='logs/question_answering'
)