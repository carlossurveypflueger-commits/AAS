import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

class Settings:
    app_name = "Ads Automation System"
    debug = True
    version = "1.0.0"
    
    # APIs - agora carregando do .env
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
    
    def __init__(self):
        print(f"Config carregado:")
        print(f"- OpenAI: {'✅' if self.openai_api_key else '❌'}")
        print(f"- Replicate: {'✅' if self.replicate_api_token else '❌'}")

settings = Settings()

def check_api_keys():
    return {
        "openai": bool(settings.openai_api_key and settings.openai_api_key.startswith('sk-')),
        "anthropic": bool(settings.anthropic_api_key and settings.anthropic_api_key.startswith('sk-ant-')),
        "replicate": bool(settings.replicate_api_token and settings.replicate_api_token.startswith('r8_'))
    }