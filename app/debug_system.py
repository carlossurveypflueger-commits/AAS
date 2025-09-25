# teste_rapido.py
import asyncio
import sys
sys.path.append('.')

async def test():
    try:
        from app.services.ai_generator_real import ai_generator_real
        
        # Testar análise
        print("Testando análise...")
        analysis = await ai_generator_real.analyze_with_openai("iPhone 15 Pro Max 256GB seminovo")
        print(f"Produto: {analysis['produto_identificado']}")
        print(f"Marca: {analysis['marca']}")
        print(f"Preço: {analysis['preco_estimado']}")
        
        # Testar copies
        print("\nTestando copies...")
        copies = await ai_generator_real.generate_copies_with_openai(analysis, 2)
        for copy in copies:
            print(f"- {copy['estrategia']}: {copy['texto']}")
        
        # Testar imagens
        print("\nTestando imagens...")
        images = await ai_generator_real.generate_images_with_replicate(analysis, 1)
        for img in images:
            print(f"- {img['style']}: {img['url'][:50]}...")
        
        print("\n✅ TUDO FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test())
    if result:
        print("\n🚀 PRÓXIMO PASSO: uvicorn app.main:app --reload --port 8080")