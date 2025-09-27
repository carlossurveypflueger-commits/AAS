# app/main.py
"""
Sistema de Automação de Anúncios v2.3 - SISTEMA GRATUITO
- Busca real de produtos na internet (Pexels/Unsplash/Pixabay)
- IA real para análise e geração (Groq + HuggingFace)
- 100% gratuito para desenvolvimento
- Universal: funciona para qualquer produto
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

from app.core.config import settings
from app.utils.logger import logger

# Configuração da aplicação
app = FastAPI(
    title="Sistema de Automação de Anúncios",
    description="Sistema universal com busca real + IA - 100% gratuito para desenvolvimento",
    version="2.3.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== CARREGAMENTO DOS SISTEMAS ====================

SYSTEM_STATUS = {}

# Sistema Principal: Busca Real + IA Gratuita
try:
    from app.services.free_search_ai_system import free_search_ai
    SYSTEM_STATUS["free_search_ai"] = "active"
    main_system = free_search_ai
    logger.info("[OK] Sistema Gratuito carregado - Busca Real + IA")
except Exception as e:
    SYSTEM_STATUS["free_search_ai"] = f"error: {str(e)}"
    logger.error(f"[ERROR] Sistema Gratuito falhou: {e}")
    
    # Fallback para sistema anterior
    try:
        from app.services.ai_generator_real import ai_generator_real
        main_system = ai_generator_real
        SYSTEM_STATUS["fallback"] = "ai_generator_real"
        logger.info("[FALLBACK] Usando sistema anterior")
    except Exception as e2:
        SYSTEM_STATUS["fallback"] = f"error: {str(e2)}"
        main_system = None
        logger.error(f"[ERROR] Todos os sistemas falharam")

# ==================== ENDPOINTS PRINCIPAIS ====================

@app.get("/")
async def root():
    """Endpoint raiz com status do sistema"""
    try:
        if main_system and hasattr(main_system, 'get_free_status'):
            # Sistema gratuito
            system_status = main_system.get_free_status()
            mode = "FREE_DEVELOPMENT"
            features = [
                "🔍 Busca real de produtos na internet",
                "🤖 IA real para análise (Groq gratuito)",
                "🎨 IA real para imagens (HuggingFace gratuito)", 
                "🌍 Universal: qualquer produto/segmento",
                "💰 Custo: $0.00 para desenvolvimento"
            ]
        elif main_system and hasattr(main_system, 'is_available'):
            # Sistema anterior
            system_status = main_system.is_available()
            mode = "STANDARD"
            features = ["Sistema padrão ativo"]
        else:
            system_status = {"status": "offline"}
            mode = "OFFLINE"
            features = ["Nenhum sistema disponível"]
        
        return {
            "message": "Sistema de Automação de Anúncios v2.3",
            "status": "online",
            "version": "2.3.0",
            "mode": mode,
            "system_status": SYSTEM_STATUS,
            "capabilities": system_status,
            "features": features,
            "endpoints": {
                "docs": "/docs",
                "generate_free": "/api/ai/generate-free",
                "generate_standard": "/api/ai/generate", 
                "test": "/test",
                "health": "/health"
            },
            "recommended_setup": [
                "PEXELS_API_KEY (pexels.com/api) - GRATUITO",
                "GROQ_API_KEY (console.groq.com) - GRATUITO",
                "HUGGINGFACE_TOKEN (huggingface.co) - GRATUITO"
            ] if mode == "FREE_DEVELOPMENT" else []
        }
    except Exception as e:
        return {
            "message": "Sistema de Automação de Anúncios v2.3",
            "status": "online_with_errors",
            "error": str(e),
            "mode": "ERROR"
        }

@app.get("/health")
async def health_check():
    """Verificação de saúde detalhada"""
    try:
        health_data = {
            "status": "healthy",
            "version": "2.3.0",
            "systems": SYSTEM_STATUS,
            "main_system": type(main_system).__name__ if main_system else "None"
        }
        
        if main_system and hasattr(main_system, 'get_free_status'):
            # Status do sistema gratuito
            free_status = main_system.get_free_status()
            health_data["free_system"] = free_status
            health_data["development_ready"] = free_status.get("development_ready", False)
            health_data["production_ready"] = free_status.get("production_ready", False)
            
        elif main_system and hasattr(main_system, 'is_available'):
            # Status do sistema padrão
            standard_status = main_system.is_available()
            health_data["standard_system"] = standard_status
        
        return health_data
        
    except Exception as e:
        return {
            "status": "healthy_with_errors",
            "error": str(e),
            "main_system": "None"
        }

@app.post("/api/ai/generate-free")
async def generate_free_campaign(request: dict):
    """
    Endpoint GRATUITO: Busca real + IA gratuita
    Funciona para QUALQUER produto
    """
    try:
        prompt = request.get("prompt", "")
        if not prompt:
            raise HTTPException(400, "Prompt é obrigatório")
        
        if not main_system or not hasattr(main_system, 'generate_images_with_free_search'):
            raise HTTPException(503, "Sistema gratuito não disponível")
        
        logger.info(f"[FREE] 🆓 Nova campanha gratuita: {prompt[:50]}...")
        
        # 1. ANÁLISE com Groq gratuito (se disponível)
        logger.info("[1/4] 🧠 Analisando produto...")
        if hasattr(main_system, 'analyze_with_openai'):
            analysis = await main_system.analyze_with_openai(prompt)
        else:
            # Análise básica
            analysis = {
                "produto_identificado": prompt,
                "tipo_produto": "produto",
                "marca": "Genérico",
                "estrategia_recomendada": "comercial"
            }
        
        # 2. COPIES com Groq gratuito (se disponível)
        logger.info("[2/4] ✍️ Gerando copies...")
        if hasattr(main_system, 'generate_copies_with_openai'):
            copies = await main_system.generate_copies_with_openai(analysis, num_copies=3)
        else:
            # Copies básicas
            copies = [
                {"id": 1, "estrategia": "URGÊNCIA", "texto": f"🔥 {prompt} - Imperdível!"},
                {"id": 2, "estrategia": "PREMIUM", "texto": f"✨ {prompt} - Qualidade premium!"},
                {"id": 3, "estrategia": "COMERCIAL", "texto": f"📱 {prompt} - Oportunidade única!"}
            ]
        
        # 3. IMAGENS com busca real + IA gratuita
        logger.info("[3/4] 🎨 Buscando referências reais + gerando imagens...")
        images = await main_system.generate_images_with_free_search(analysis, copies, num_images=3)
        
        # 4. CAMPANHA completa
        logger.info("[4/4] 📋 Criando campanha...")
        campaign = create_free_campaign(analysis, copies, images)
        
        # Status e estatísticas
        system_status = main_system.get_free_status()
        
        # Contar gerações reais vs mock
        real_images = len([img for img in images if 'free' in img.get('generated_by', '') and 'mock' not in img.get('generated_by', '')])
        real_copies = len([copy for copy in copies if copy.get('generated_by') == 'groq_real'])
        
        logger.info(f"[SUCCESS] 🎉 Campanha gratuita: {real_copies} copies reais, {real_images} imagens reais")
        
        return {
            "success": True,
            "version": "2.3.0",
            "system": "FREE_SEARCH_AI",
            "cost": "$0.00",
            "generation_stats": {
                "real_analysis": hasattr(main_system, 'analyze_with_openai'),
                "real_copies": real_copies,
                "mock_copies": len(copies) - real_copies,
                "real_images": real_images,
                "mock_images": len(images) - real_images,
                "total_references_found": sum([img.get('reference_count', 0) for img in images])
            },
            "input": {
                "prompt_original": prompt
            },
            "output": {
                "analise_produto": analysis,
                "copies_geradas": copies,
                "imagens_geradas": images,
                "campanha_completa": campaign
            },
            "system_capabilities": system_status,
            "metadata": {
                "generated_at": "2024-12-25T00:00:00Z",
                "universal_system": True,
                "works_for": "ANY product/service/segment"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Erro na geração gratuita: {str(e)}")
        raise HTTPException(500, f"Erro no processamento gratuito: {str(e)}")

@app.post("/api/ai/generate")
async def generate_standard_campaign(request: dict):
    """
    Endpoint padrão (compatibilidade com sistema anterior)
    """
    try:
        # Se sistema gratuito disponível, usar ele
        if main_system and hasattr(main_system, 'generate_images_with_free_search'):
            return await generate_free_campaign(request)
        
        # Senão, tentar sistema anterior
        prompt = request.get("prompt", "")
        if not prompt:
            raise HTTPException(400, "Prompt é obrigatório")
        
        if not main_system:
            raise HTTPException(503, "Nenhum sistema disponível")
        
        logger.info(f"[STANDARD] Campanha padrão: {prompt[:50]}...")
        
        # Usar sistema anterior
        analysis = await main_system.analyze_with_openai(prompt)
        copies = await main_system.generate_copies_with_openai(analysis, 3)
        
        # Tentar método novo primeiro, depois antigo
        if hasattr(main_system, 'generate_images_with_replicate'):
            if 'copies' in main_system.generate_images_with_replicate.__code__.co_varnames:
                images = await main_system.generate_images_with_replicate(analysis, copies, 3)
            else:
                images = await main_system.generate_images_with_replicate(analysis, 3)
        else:
            images = []
        
        campaign = create_free_campaign(analysis, copies, images)
        
        return {
            "success": True,
            "version": "2.3.0",
            "system": "STANDARD",
            "output": {
                "analise_produto": analysis,
                "copies_geradas": copies,
                "imagens_geradas": images,
                "campanha_completa": campaign
            }
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Erro padrão: {str(e)}")
        raise HTTPException(500, f"Erro no processamento: {str(e)}")
@app.post("/api/ai/generate-free")
async def generate_free_campaign(request: dict):
    """
    Endpoint GRATUITO: Busca real + IA gratuita
    Funciona para QUALQUER produto
    """
    try:
        prompt = request.get("prompt", "")
        if not prompt:
            raise HTTPException(400, "Prompt é obrigatório")
        
        if not main_system or not hasattr(main_system, 'generate_images_with_free_search'):
            raise HTTPException(503, "Sistema gratuito não disponível")
        
        logger.info(f"[FREE] 🆓 Nova campanha gratuita: {prompt[:50]}...")
        
        # 1. ANÁLISE com Groq gratuito (se disponível) - USANDO MÉTODO CORRETO
        logger.info("[1/4] 🧠 Analisando produto...")
        if hasattr(main_system, 'analyze_with_openai'):
            analysis = await main_system.analyze_with_openai(prompt)
        else:
            # Análise básica fallback
            analysis = {
                "produto_identificado": prompt,
                "tipo_produto": "produto",
                "marca": "Genérico",
                "estrategia_recomendada": "comercial",
                "publico_alvo_sugerido": "Público geral brasileiro",
                "preco_estimado": "R$ 500 - R$ 1.500",
                "pontos_de_venda": ["Qualidade", "Preço justo", "Entrega rápida"]
            }
        
        # 2. COPIES com Groq gratuito (se disponível) - USANDO MÉTODO CORRETO
        logger.info("[2/4] ✍️ Gerando copies...")
        if hasattr(main_system, 'generate_copies_with_openai'):
            copies = await main_system.generate_copies_with_openai(analysis, num_copies=3)
        else:
            # Copies básicas fallback
            copies = [
                {"id": 1, "estrategia": "URGÊNCIA", "texto": f"🔥 {prompt} - Imperdível!", "generated_by": "fallback"},
                {"id": 2, "estrategia": "PREMIUM", "texto": f"✨ {prompt} - Qualidade premium!", "generated_by": "fallback"},
                {"id": 3, "estrategia": "COMERCIAL", "texto": f"📱 {prompt} - Oportunidade única!", "generated_by": "fallback"}
            ]
        
        # 3. IMAGENS com busca real + IA gratuita
        logger.info("[3/4] 🎨 Buscando referências reais + gerando imagens...")
        images = await main_system.generate_images_with_free_search(analysis, copies, num_images=3)
        
        # 4. CAMPANHA completa
        logger.info("[4/4] 📋 Criando campanha...")
        campaign = create_free_campaign(analysis, copies, images)
        
        # Status e estatísticas
        system_status = main_system.get_free_status()
        
        # Contar gerações reais vs mock - CORRIGIDO
        real_images = len([img for img in images if img.get('generated_by') in ['huggingface_free']])
        mock_images = len(images) - real_images
        
        # Contar copies reais vs mock - CORRIGIDO  
        real_copies = len([copy for copy in copies if copy.get('generated_by') == 'groq_real'])
        mock_copies = len(copies) - real_copies
        
        # Verificar se análise foi real
        real_analysis = hasattr(main_system, 'analyze_with_openai') and analysis.get('produto_identificado') != prompt
        
        logger.info(f"[SUCCESS] 🎉 Campanha gratuita: {real_copies} copies reais, {real_images} imagens reais")
        
        return {
            "success": True,
            "version": "2.3.0",
            "system": "FREE_SEARCH_AI",
            "cost": "$0.00",
            "generation_stats": {
                "real_analysis": real_analysis,
                "real_copies": real_copies,
                "mock_copies": mock_copies,
                "real_images": real_images,
                "mock_images": mock_images,
                "total_references_found": sum([img.get('reference_count', 0) for img in images])
            },
            "input": {
                "prompt_original": prompt
            },
            "output": {
                "analise_produto": analysis,
                "copies_geradas": copies,
                "imagens_geradas": images,
                "campanha_completa": campaign
            },
            "system_capabilities": system_status,
            "metadata": {
                "generated_at": "2024-12-25T00:00:00Z",
                "universal_system": True,
                "works_for": "ANY product/service/segment"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Erro na geração gratuita: {str(e)}")
        raise HTTPException(500, f"Erro no processamento gratuito: {str(e)}")

@app.get("/test")
async def test_system():
    """Endpoint de teste do sistema ativo"""
    
    if not main_system:
        return {"error": "Nenhum sistema disponível", "status": "offline"}
    
    try:
        test_prompt = "iPhone 15 Pro Max 256GB seminovo"
        
        logger.info("[TEST] Iniciando teste do sistema ativo...")
        
        # Teste baseado no sistema disponível
        if hasattr(main_system, 'get_free_status'):
            # Sistema gratuito
            status = main_system.get_free_status()
            
            # Teste rápido de análise
            if hasattr(main_system, 'analyze_with_openai'):
                analysis = await main_system.analyze_with_openai(test_prompt)
                analysis_working = bool(analysis.get("produto_identificado"))
            else:
                analysis_working = False
            
            return {
                "test_result": "success",
                "system": "FREE_SEARCH_AI",
                "prompt_tested": test_prompt,
                "system_status": status,
                "capabilities": {
                    "free_search": status.get("development_ready", False),
                    "analysis_working": analysis_working,
                    "universal": True,
                    "cost": "$0.00"
                },
                "recommendation": "Configure PEXELS_API_KEY + HUGGINGFACE_TOKEN para máximo desempenho"
            }
        
        else:
            # Sistema padrão
            analysis = await main_system.analyze_with_openai(test_prompt)
            
            return {
                "test_result": "success",
                "system": "STANDARD",
                "prompt_tested": test_prompt,
                "analysis_working": bool(analysis.get("produto_identificado")),
                "system_type": type(main_system).__name__
            }
        
    except Exception as e:
        logger.error(f"[TEST ERROR] {str(e)}")
        return {
            "test_result": "error",
            "error": str(e),
            "system": type(main_system).__name__ if main_system else "None"
        }

# ==================== FUNÇÕES AUXILIARES ====================

def create_free_campaign(analysis: dict, copies: list, images: list) -> dict:
    """Cria campanha baseada na análise gratuita"""
    
    produto = analysis.get('produto_identificado', 'produto')
    tipo_produto = analysis.get('tipo_produto', 'produto')
    
    # Orçamento baseado no tipo de produto
    budget_map = {
        "smartphone": 200,
        "notebook": 250,
        "alimento": 100,
        "servico": 150,
        "produto": 150
    }
    
    budget_daily = budget_map.get(tipo_produto, 150)
    
    # Contar referências encontradas
    total_references = sum([img.get('reference_count', 0) for img in images])
    
    return {
        "nome_campanha": f"Campanha {produto.split()[0]} - Busca Real",
        "objetivo": "CONVERSIONS",
        "orcamento": {
            "diario": budget_daily,
            "duracao": "7 dias",
            "total": budget_daily * 7,
            "custo_geracao": "$0.00"
        },
        "segmentacao": {
            "produto": produto,
            "tipo": tipo_produto,
            "publico": analysis.get("publico_alvo_sugerido", "Público geral"),
            "estrategia": analysis.get("estrategia_recomendada", "comercial")
        },
        "criativos": {
            "copies_disponiveis": len(copies),
            "imagens_disponiveis": len(images),
            "referencias_reais_encontradas": total_references,
            "qualidade": "desenvolvimento" if total_references > 0 else "mock"
        },
        "metricas_esperadas": {
            "ctr": "2.8% - 4.2%",
            "conversao": "30-80 leads",
            "cpm": "R$ 12 - 20"
        },
        "diferenciais": [
            "Baseado em produtos reais encontrados na internet",
            "Sistema universal (funciona para qualquer produto)",
            "Custo zero para desenvolvimento",
            f"Análise de {total_references} referências reais"
        ],
        "status": "pronta_para_lancamento",
        "sistema_usado": "free_search_ai_v2.3"
    }

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Executado quando o servidor inicia"""
    logger.info("\n" + "="*70)
    logger.info("[START] SISTEMA DE AUTOMAÇÃO v2.3 - BUSCA REAL + IA GRATUITA")
    logger.info("="*70)
    logger.info(f"[INFO] Servidor: http://localhost:8080")
    logger.info(f"[INFO] Docs: http://localhost:8080/docs")
    logger.info(f"[INFO] Teste: http://localhost:8080/test")
    logger.info(f"[INFO] Geração gratuita: http://localhost:8080/api/ai/generate-free")
    
    if main_system and hasattr(main_system, 'get_free_status'):
        # Sistema gratuito ativo
        status = main_system.get_free_status()
        
        logger.info(f"\n[SYSTEM] 🆓 Sistema Gratuito Ativo")
        logger.info(f"   Custo: {status['cost']}")
        logger.info(f"   Universal: Funciona para QUALQUER produto")
        
        logger.info(f"\n[APIS] Status das APIs gratuitas:")
        search_apis = status.get('search_apis', {})
        for api, info in search_apis.items():
            status_icon = "✅" if info.get('available') else "❌"
            logger.info(f"   {api}: {status_icon} ({info.get('cost', 'FREE')})")
        
        ai_apis = status.get('ai_apis', {})
        for api, info in ai_apis.items():
            status_icon = "✅" if info.get('available') else "❌"
            logger.info(f"   {api}: {status_icon} ({info.get('cost', 'FREE')})")
        
        # Recomendações
        if not status.get('development_ready'):
            logger.info(f"\n[SETUP] 🔧 Para ativar busca real, configure:")
            for rec in status.get('recommended_apis', []):
                logger.info(f"   • {rec}")
        else:
            logger.info(f"\n[READY] 🚀 Sistema pronto para desenvolvimento!")
            logger.info(f"   Busca real: ✅")
            logger.info(f"   IA gratuita: ✅")
            logger.info(f"   Custo total: $0.00")
    
    elif main_system:
        # Sistema padrão
        logger.info(f"\n[SYSTEM] Sistema Padrão Ativo: {type(main_system).__name__}")
        try:
            if hasattr(main_system, 'is_available'):
                standard_status = main_system.is_available()
                logger.info(f"   Status: {standard_status}")
        except Exception as e:
            logger.info(f"   Status: Erro ao verificar - {e}")
    
    else:
        logger.info(f"\n[ERROR] ❌ Nenhum sistema disponível")
        logger.info(f"   Verifique as configurações e dependências")
    
    logger.info("="*70 + "\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)