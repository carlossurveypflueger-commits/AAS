import os
from dotenv import load_dotenv

load_dotenv()

def test_replicate_fixed():
    """Teste Replicate com modelo correto"""
    
    token = os.getenv("REPLICATE_API_TOKEN")
    
    if not token:
        print("❌ Token Replicate não encontrado")
        return False
    
    try:
        import replicate
        
        print("✅ Biblioteca Replicate importada")
        
        # Usar replicate.run diretamente (método mais simples)
        print("🎨 Gerando imagem de teste...")
        
        output = replicate.run(
            "black-forest-labs/flux-schnell:f1394c3c0e6e9741cb46c02bf3ab5ad999fdbcfd9370b4a90b6e1dd10e5e0ad8",
            input={
                "prompt": "red apple on white background, product photography",
                "width": 512,
                "height": 512,
                "num_outputs": 1,
                "num_inference_steps": 4
            }
        )
        
        if output and len(output) > 0:
            url = output[0]
            print(f"📤 Imagem gerada: {url[:50]}...")
            print(f"🔗 URL completa: {url}")
            return True
        else:
            print("❌ Nenhuma imagem retornada")
            return False
            
    except Exception as e:
        print(f"❌ Erro detalhado: {type(e).__name__}: {e}")
        
        # Tentar com modelo diferente
        try:
            print("🔄 Tentando modelo alternativo...")
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={
                    "prompt": "simple red apple, white background",
                    "width": 512,
                    "height": 512
                }
            )
            
            if output and len(output) > 0:
                print("✅ Modelo alternativo funcionou")
                return True
                
        except Exception as e2:
            print(f"❌ Modelo alternativo também falhou: {e2}")
            
        return False

if __name__ == "__main__":
    success = test_replicate_fixed()
    print(f"🎯 Resultado: {'✅ SUCESSO' if success else '❌ FALHOU'}")