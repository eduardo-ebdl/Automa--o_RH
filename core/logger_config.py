import logging
import sys
import os
from datetime import datetime
import config

def setup_logger():
    """Configura e retorna um logger compartilhado para o projeto."""

    # formato único de log
    log_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'  # padrão yyyy-mm-dd HH:MM:SS
    )

    logger = logging.getLogger("automacao_rh")
    logger.setLevel(logging.INFO)  # N=nível fixo em INFO

    if not logger.handlers:
        # saída no console
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(log_format)
        logger.addHandler(stream_handler)

        # saída em arquivo
        log_dir = os.path.join(config.BASE_DIR, 'logs')
        os.makedirs(log_dir, exist_ok=True)

        log_filename = f"log_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_filepath = os.path.join(log_dir, log_filename)

        file_handler = logging.FileHandler(log_filepath, mode='a', encoding='utf-8')
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    return logger

# logger global do projeto
logger = setup_logger()