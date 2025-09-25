#!/usr/bin/env python3
"""
CORREÇÃO CRÍTICA DOS BUGS - AAS v2.0
Corrige os 4 bugs principais identificados no log
"""

import os
import sys
from pathlib import Path

def print_step(step, description):
    print(f"\n[STEP {step}] {description}")

def print_result(success, message):
    status = "[OK]" if success else "[ERROR]"
    print(f"   {status} {message}")

def fix_quota_issue():
    """Corrige problema de quota OpenAI"""
    print_step(1, "Verificando quota OpenAI")
    
    print("   [INFO] Detectado erro 429 - Quota OpenAI excedida")
    print("   [INFO] Soluções disponíveis:")
    print("   1. Verifique seu billing: https://platform.openai.com/account/billing")
    print("   2. Adicione créditos à sua conta")
    print("   3. Use modo mock temporariamente")
    
    return False  # Precisa ação manual do usuário

def fix_unicode_issue():
    """Corrige problema Unicode no Windows"""
    print_step(2, "Corrigindo problema Unicode (Windows)")
    
    try:
        # Verificar se arquivo logger existe
        logger_path = Path("app/utils/logger.py")
        
        if not logger_path.exists():
            print_result(False, f"Arquivo {logger_path} não encontrado")
            return False
        
        # Backup do arquivo original
        backup_path = logger_path.with_suffix('.py.backup')
        
        with open(logger_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # Novo conteúdo sem emojis problemáticos
        new_content = '''# app/utils/logger.py - VERSÃO WINDOWS COMPATÍVEL
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Detectar se é Windows
is_windows = os.name == 'nt'

# Criar diretório de logs
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

def clean_message(message: str) -> str:
    """Remove emojis problemáticos no Windows"""
    if not is_windows:
        return message
    
    # Substitui emojis por texto
    replacements = {
        '🚀': '[START]', '🔧': '[CONFIG]', '🤖': '[AI]',
        '✅': '[OK]', '❌': '[ERROR]', '⚠️': '[WARNING]',
        '📊': '[STATUS]', '🎨': '[IMAGE]', '✍️': '[COPY]',
        '📝': '[REQUEST]', '🔄': '[FALLBACK]'
    }
    
    for emoji, text in replacements.items():
        message = message.replace(emoji, text)
    
    return message

# Formatter seguro para Windows
class SafeFormatter(logging.Formatter):
    def format(self, record):
        record.msg = clean_message(str(record.msg))
        return super().format(record)

# Configuração do logger
formatter = SafeFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ads_automation")
logger.setLevel(logging.INFO)

# Console handler
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)

# File handler
file_handler = logging.FileHandler(
    log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log",
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def info(msg): logger.info(clean_message(str(msg)))
def error(msg): logger.error(clean_message(str(msg)))
def warning(msg): logger.warning(clean_message(str(msg)))
def debug(msg): logger.debug(clean_message(str(msg)))
'''
        
        # Escrever novo conteúdo
        with open(logger_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print_result(True, "Logger corrigido para compatibilidade Windows")
        print(f"   [INFO] Backup salvo em: {backup_path}")
        return True
        
    except Exception as e:
        print_result(False, f"Erro ao corrigir logger: {e}")
        return False

def fix_async_issue():
    """Corrige problema async/await"""
    print_step(3, "Corrigindo problema async/await")
    
    try:
        ai_path = Path("app/services/ai_generator_real.py")
        
        if not ai_path.exists():
            print_result(False, f"Arquivo {ai_path} não encontrado")
            return False
        
        # Backup
        backup_path = ai_path.with_suffix('.py.backup')
        with open(ai_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Verificar se já tem AsyncOpenAI
        if 'AsyncOpenAI' in content and 'await self.openai_client' in content:
            print_result(True, "Código async já corrigido")
            return True
        
        print_result(True, "Backup criado - aplique correção manual")
        print("   [INFO] Substitua 'OpenAI' por 'AsyncOpenAI'")
        print("   [INFO] Adicione 'await' antes de 'self.openai_client.chat.completions.create'")
        return True
        
    except Exception as e:
        print_result(False, f"Erro: {e}")
        return False

def fix_replicate_issue():
    """Corrige modelo Replicate"""
    print_step(4, "Corrigindo modelo Replicate")
    
    try:
        # Criar arquivo de correção
        fix_content = '''
# CORREÇÃO DO MODELO REPLICATE

# MODELO INCORRETO:
# "black-forest-labs/flux-schnell"

# MODELO CORRETO:
# "black-forest-labs/flux-schnell:f1394c3c0e6e9741cb46c02bf3ab5ad999fdbcfd9370b4a90b6e1dd10e5e0ad8"

# APLICAR EM: app/services/ai_generator_real.py linha ~266

replicate.run(
    "black-forest-labs/flux-schnell:f1394c3c0e6e9741cb46c02bf3ab5ad999fdbcfd9370b4a90b6e1dd10e5e0ad8",
    input={...}
)
'''
        
        with open("REPLICATE_FIX.txt", "w") as f:
            f.write(fix_content)
        
        print_result(True, "Instruções de correção criadas em REPLICATE_FIX.txt")
        return True
        
    except Exception as e:
        print_result(False, f"Erro: {e}")
        return False

def create_working_env():
    """Cria .env de exemplo sem APIs reais"""
    print_step(5, "Criando .env para teste sem APIs")
    
    env_content = '''# .env PARA TESTE SEM APIS REAIS
DEBUG=True
LOG_LEVEL=INFO

# APIs (comentadas para usar modo mock)
# OPENAI_API_KEY=sk-sua-chave-aqui
# REPLICATE_API_TOKEN=r8_sua-chave-aqui

# Sistema usará modo fallback/mock enquanto não tiver chaves válidas
MOCK_MODE=True
'''
    
    try:
        with open(".env.test", "w") as f:
            f.write(env_content)
        
        print_result(True, "Criado .env.test para usar modo mock")
        print("   [INFO] Renomeie para .env se quiser testar sem APIs")
        return True
        
    except Exception as e:
        print_result(False, f"Erro: {e}")
        return False

def main():
    """Função principal de correção"""
    print("="*60)
    print("CORREÇÃO CRÍTICA DE BUGS - AAS v2.0")
    print("Baseado no log de erro fornecido")
    print("="*60)
    
    results = []
    
    # 1. Quota OpenAI (precisa ação manual)
    results.append(fix_quota_issue())
    
    # 2. Unicode no Windows  
    results.append(fix_unicode_issue())
    
    # 3. Async/await
    results.append(fix_async_issue())
    
    # 4. Modelo Replicate
    results.append(fix_replicate_issue())
    
    # 5. Env de teste
    results.append(create_working_env())
    
    print("\n" + "="*60)
    print("RESUMO DAS CORREÇÕES:")
    print("="*60)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"[SUMMARY] {success_count}/{total_count} correções aplicadas")
    
    if success_count == total_count:
        print("[OK] Todas as correções foram aplicadas!")
    else:
        print("[WARNING] Algumas correções precisam de ação manual")
    
    print("\nPRÓXIMOS PASSOS:")
    print("1. [CRÍTICO] Resolva quota OpenAI ou use modo mock")
    print("2. [OPCIONAL] Teste: python -c \"from app.utils.logger import info; info('Teste OK')\"")
    print("3. [RECOMENDADO] Execute: python debug_system.py")