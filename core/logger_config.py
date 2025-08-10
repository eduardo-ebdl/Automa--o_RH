# core/logger_config.py
import logging
import sys
import os
from datetime import datetime
import config

def setup_logger():
    """Configures a shared logger for the project."""
    log_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S' # Formato de data e hora -- ponto de atencao para o formato yyyy-mm-dd
    )
    
    logger = logging.getLogger("automacao_rh")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # Console handler
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(log_format)
        logger.addHandler(stream_handler)
        
        # File handler
        log_dir = os.path.join(config.BASE_DIR, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_filename = f"log_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_filepath = os.path.join(log_dir, log_filename)
        
        file_handler = logging.FileHandler(log_filepath, mode='a', encoding='utf-8')
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
        
    return logger

logger = setup_logger()