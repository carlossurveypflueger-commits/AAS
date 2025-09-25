import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("=== DEBUGGING DO SISTEMA DE IA ===")
print()

# 1. Verificar se o .env existe
env_file_exists = os.path.exists('.env')
print(f"Arquivo .env existe: {'✅' if env_file_exists else '❌'}")

if env_file_exists:
    with open('.env', 'r') as f:
        content = f.read()
        print(f"Conteúdo do .env (primeiros 100 chars): {content[:100]}...")

print()

# 2. Verificar variáveis de ambiente
openai_key = os.getenv("OPENAI_API_KEY")
replicate_token = os.getenv("REPLICATE_API_TOKEN")

print("CHAVES DE API:")
print(f"OpenAI: {'✅ Configurada' if openai_key else '❌ Não encontrada'}")
if openai_key:
    print(f"  - Começa com sk-: {'✅' if openai_key.startswith('sk-') else '❌'}")
    print(f"  - Tamanho: {len(openai_key)} caracteres")

print(f"Replicate: {'✅ Configurada' if replicate_token else '❌ Não encontrada'}")
if replicate_token:
    print(f"  - Começa com r8_: {'✅' if replicate_token.startswith('r8_') else '❌'}")
    print(f"  - Tamanho: {len(replicate_token)} caracteres")

print()

# 3. Testar imports
print("TESTE DE BIBLIOTECAS:")
try:
    from openai import OpenAI
    print("✅ OpenAI library instalada")
except ImportError as e:
    print(f"❌ OpenAI library: {e}")

try:
    import replicate
    print("✅ Replicate library instalada")
except ImportError as e:
    print(f"❌ Replicate library: {e}")

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv instalada")
except ImportError as e:
    print(f"❌ python-dotenv: {e}")

print()

# 4. Testar criação de clientes
print("TESTE DE CLIENTES:")
if openai_key:
    try:
        client = OpenAI(api_key=openai_key)
        print("✅ Cliente OpenAI criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar cliente OpenAI: {e}")

if replicate_token:
    try:
        import replicate
        client = replicate.Client(api_token=replicate_token)
        print("✅ Cliente Replicate criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar cliente Replicate: {e}")

print()
print("=== FIM DO DEBUG ===")