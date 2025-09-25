# debug_image_generation.py
# Execute para testar especificamente a geração de imagens

import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_stability_api():
    """Testa diretamente a API do Stability AI"""
    
    stability_key = os.getenv("STABILITY_API_KEY")
    
    if not stability_key:
        print("❌ STABILITY_API_KEY não encontrada no .env")
        return False
    
    print(f"🔑 Testando Stability AI: {stability_key[:20]}...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Authorization": f"Bearer {stability_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "text_prompts": [{"text": "professional product photography of iPhone, white background, studio lighting"}],
                    "cfg_scale": 7,
                    "height": 1024,  # Menor para teste
                    "width": 1024,
                    "samples": 1,
                    "steps": 20
                },
                timeout=60
            )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Stability AI funcionando!")
            print(f"📄 Resposta: {len(result.get('artifacts', []))} imagens geradas")
            
            if result.get('artifacts'):
                image_b64 = result["artifacts"][0]["base64"]
                print(f"🖼️ Imagem base64: {len(image_b64)} caracteres")
                print(f"🔗 URL: data:image/png;base64,{image_b64[:50]}...")
            
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

async def test_huggingface_api():
    """Testa API do HuggingFace para imagens"""
    
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    
    print(f"\n🤗 Testando HuggingFace...")
    print(f"🔑 Token: {hf_token[:20] if hf_token else 'Não configurado'}...")
    
    try:
        headers = {}
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
                headers=headers,
                json={"inputs": "professional product photo of iPhone, white background"},
                timeout=60
            )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            image_bytes = response.content
            print(f"✅ HuggingFace funcionando!")
            print(f"🖼️ Imagem bytes: {len(image_bytes)} bytes")
            return True
        elif response.status_code == 503:
            print("⏳ HuggingFace modelo está carregando (normal)")
            print("💡 Tente novamente em alguns minutos")
            return False
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_file_integration():
    """Verifica se os arquivos estão criados corretamente"""
    print(f"\n📁 Verificando arquivos...")
    
    files_to_check = [
        "app/services/free_image_generator.py",
        "app/services/ai_generator_real.py"
    ]
    
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        print(f"   {'✅' if exists else '❌'} {file_path}")
        
        if exists and "ai_generator_real.py" in file_path:
            # Verificar se a integração está correta
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                has_import = "free_image_generator" in content
                print(f"   {'✅' if has_import else '❌'} Import free_image_generator found")
                
                has_call = "free_image_generator.generate_product_images" in content
                print(f"   {'✅' if has_call else '❌'} Call to generate_product_images found")

async def main():
    print("🧪 DEBUG DA GERAÇÃO DE IMAGENS")
    print("="*50)
    
    # 1. Testar arquivos
    test_file_integration()
    
    # 2. Testar APIs
    stability_ok = await test_stability_api()
    hf_ok = await test_huggingface_api()
    
    print("\n" + "="*50)
    print("📊 RESUMO:")
    print(f"   Stability AI: {'✅' if stability_ok else '❌'}")
    print(f"   HuggingFace: {'✅' if hf_ok else '❌'}")
    
    if stability_ok:
        print(f"\n💡 STABILITY AI FUNCIONANDO!")
        print(f"   O problema está na integração com ai_generator_real.py")
    elif hf_ok:
        print(f"\n💡 HUGGINGFACE FUNCIONANDO!")
        print(f"   Use HuggingFace como fallback")
    else:
        print(f"\n❌ NENHUMA API DE IMAGEM FUNCIONANDO")
        print(f"   Verifique configurações e conectividade")

if __name__ == "__main__":
    asyncio.run(main())