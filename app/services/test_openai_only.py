import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_openai_fixed():
    """Teste OpenAI com tratamento de versões"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ Chave OpenAI não encontrada")
        return False
    
    try:
        # Importar de forma mais compatível
        from openai import OpenAI
        
        # Criar cliente sem parâmetros problemáticos
        client = OpenAI(
            api_key=api_key
            # Não passar outros parâmetros que podem causar conflito
        )
        print("✅ Cliente OpenAI criado")
        
        # Teste simples
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Diga apenas: TESTE OK"}
            ],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        print(f"📤 Resposta: {result}")
        
        return "TESTE" in result or "OK" in result
        
    except Exception as e:
        print(f"❌ Erro detalhado: {type(e).__name__}: {e}")
        
        # Tentar versão síncrona se a assíncrona falhar
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Teste"}],
                max_tokens=5
            )
            
            print("✅ Versão síncrona funcionou")
            return True
            
        except Exception as e2:
            print(f"❌ Erro versão síncrona: {e2}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_openai_fixed())
    print(f"🎯 Resultado: {'✅ SUCESSO' if success else '❌ FALHOU'}")