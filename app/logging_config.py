import logging
import logging.handlers
import os
from datetime import datetime

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


def setup_logging():
    """Configure structured logging for FastAPI application."""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    # Clear any existing handlers
    root_logger.handlers = []
    
    # Formatter with timestamp, level, module, and message
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (stdout) - this works in serverless
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler only for non-Vercel environments
    if not os.getenv('VERCEL') and not os.getenv('VERCEL_ENV'):
        try:
            LOG_DIR = 'logs'
            os.makedirs(LOG_DIR, exist_ok=True)
            LOG_FILE = os.path.join(LOG_DIR, 'voter_api.log')
            
            file_handler = logging.handlers.RotatingFileHandler(
                LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(LOG_LEVEL)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            # Fail silently if file logging not available
            pass
    
    # Suppress noisy third-party loggers
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    
    return root_logger


# Initialize logger for this module
logger = logging.getLogger(__name__)
