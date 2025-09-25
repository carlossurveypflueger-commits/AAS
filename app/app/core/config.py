import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

class Settings:
    app_name = "Ads Automation System"
    debug = True
    version = "2.0.0"
    
    # APIs - agora carregando do .env
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
    
    def __init__(self):
        print(f"Config carregado:")
        print(f"- OpenAI: {'✅' if self.openai_api_key else '❌'}")
        print(f"- Anthropic: {'✅' if self.anthropic_api_key else '❌'}")
        print(f"- Replicate: {'✅' if self.replicate_api_token else '❌'}")
    
    def get_api_status(self):
        """Método que estava faltando - usado no main.py"""
        return {
            "openai": {
                "configured": bool(self.openai_api_key and self.openai_api_key.startswith('sk-')),
                "status": "active" if self.openai_api_key else "inactive"
            },
            "anthropic": {
                "configured": bool(self.anthropic_api_key and self.anthropic_api_key.startswith('sk-ant-')),
                "status": "active" if self.anthropic_api_key else "inactive"
            },
            "replicate": {
                "configured": bool(self.replicate_api_token and self.replicate_api_token.startswith('r8_')),
                "status": "active" if self.replicate_api_token else "inactive"
            }
        }

settings = Settings()

def check_api_keys():
    """Função legacy - mantida para compatibilidade"""
    status = settings.get_api_status()
    return {
        "openai": status["openai"]["configured"],
        "anthropic": status["anthropic"]["configured"],
        "replicate": status["replicate"]["configured"]
    }