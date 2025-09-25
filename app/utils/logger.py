# app/utils/logger.py
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Detectar se é Windows e configurar encoding adequado
is_windows = os.name == 'nt'
if is_windows:
    # Forçar UTF-8 no Windows
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Criar diretório de logs se não existir
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Função para remover emojis se necessário (Windows)
def clean_message(message: str) -> str:
    """Remove emojis problemáticos no Windows"""
    if not is_windows:
        return message
    
    # Mapeamento de emojis para texto simples
    emoji_map = {
        '🚀': '[START]',
        '🔧': '[CONFIG]',
        '🤖': '[AI]',
        '✅': '[OK]',
        '❌': '[ERROR]', 
        '⚠️': '[WARNING]',
        '📊': '[STATUS]',
        '🎨': '[IMAGE]',
        '✍️': '[COPY]',
        '📝': '[REQUEST]',
        '🔄': '[FALLBACK]',
        '🎉': '[SUCCESS]',
        '💡': '[INFO]'
    }
    
    clean_msg = message
    for emoji, replacement in emoji_map.items():
        clean_msg = clean_msg.replace(emoji, replacement)
    
    # Remover outros caracteres Unicode problemáticos
    clean_msg = clean_msg.encode('ascii', 'replace').decode('ascii')
    
    return clean_msg

# Configurar formato de log
class WindowsSafeFormatter(logging.Formatter):
    def format(self, record):
        # Limpar mensagem antes de formatar
        record.msg = clean_message(str(record.msg))
        return super().format(record)

log_format = WindowsSafeFormatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Criar logger principal
logger = logging.getLogger("ads_automation")
logger.setLevel(logging.DEBUG)

# Handler para console (com encoding UTF-8)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)

# Handler para arquivo (sempre UTF-8)
file_handler = logging.FileHandler(
    log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log",
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)

# Adicionar handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Funções auxiliares seguras
def debug(msg: str):
    logger.debug(clean_message(str(msg)))

def info(msg: str):
    logger.info(clean_message(str(msg)))

def warning(msg: str):
    logger.warning(clean_message(str(msg)))

def error(msg: str):
    logger.error(clean_message(str(msg)))

def critical(msg: str):
    logger.critical(clean_message(str(msg)))

# Teste de compatibilidade
if __name__ == "__main__":
    info("Testando logger compatível com Windows")
    info("🚀 Emojis serão convertidos automaticamente")
    info("✅ Sistema funcionando corretamente")

# Exportar tudo que precisa
__all__ = ['logger', 'debug', 'info', 'warning', 'error', 'critical']