# app/utils/logger.py
import logging
import sys
from datetime import datetime
from pathlib import Path

# Criar diretório de logs se não existir
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configurar formato de log
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Criar logger principal
logger = logging.getLogger("ads_automation")
logger.setLevel(logging.DEBUG)

# Handler para console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)

# Handler para arquivo
file_handler = logging.FileHandler(
    log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)

# Adicionar handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Funções auxiliares para diferentes níveis
def debug(msg: str):
    logger.debug(msg)

def info(msg: str):
    logger.info(msg)

def warning(msg: str):
    logger.warning(msg)

def error(msg: str):
    logger.error(msg)

def critical(msg: str):
    logger.critical(msg)

# Exportar tudo que precisa
__all__ = ['logger', 'debug', 'info', 'warning', 'error', 'critical']