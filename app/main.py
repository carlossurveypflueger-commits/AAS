# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar configurações e logger
from app.core.config import settings
from app.utils.logger import logger

# Configuração da aplicação
app = FastAPI(
    title="Sistema de Automação de Anúncios",
    description="Sistema inteligente para criação automática de campanhas publicitárias",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== IMPORTS DAS IAS ====================
AI_STATUS = {}

try:
    from app.services.ai_generator_real import ai_generator_real
    AI_STATUS["ai_real"] = "active"
    logger.info("✅ AI Generator Real carregado")
except Exception as e:
    AI_STATUS["ai_real"] = f"error: {str(e)}"
    logger.error(f"❌ Erro ao carregar AI Generator Real: {e}")
    ai_generator_real = None

# ==================== ENDPOINTS PRINCIPAIS ====================

@app.get("/")
async def root():
    """Endpoint raiz com status do sistema"""
    api_status = settings.get_api_status()
    
    return {
        "message": "Sistema de Automação de Anúncios",
        "status": "online",
        "version": "2.0.0",
        "services": {
            "ai_real": AI_STATUS.get("ai_real", "inactive"),
            "openai": "configured" if api_status["openai"]["configured"] else "not_configured",
            "replicate": "configured" if api_status["replicate"]["configured"] else "not_configured"
        }
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    return {
        "status": "healthy",
        "ai_services": AI_STATUS,
        "api_keys": settings.get_api_status()
    }

# ==================== ENDPOINT PRINCIPAL DE GERAÇÃO ====================

@app.post("/api/ai/generate")
async def generate_campaign(request: dict):
    """
    Endpoint principal para gerar campanhas com IA
    Usa AI Generator Real se disponível, senão fallback para local
    """
    try:
        prompt = request.get("prompt", "")
        if not prompt:
            raise HTTPException(400, "Prompt é obrigatório")
        
        logger.info(f"📝 Nova requisição: {prompt[:50]}...")
        
        # Tentar usar AI Generator Real se disponível
        if ai_generator_real and AI_STATUS.get("ai_real") == "active":
            logger.info("🤖 Usando AI Generator Real")
            
            # 1. Análise do produto
            analysis = await ai_generator_real.analyze_with_openai(prompt)
            
            # 2. Geração de copies
            copies = await ai_generator_real.generate_copies_with_openai(analysis, num_copies=3)
            
            # 3. Geração de imagens
            images = await ai_generator_real.generate_images_with_replicate(analysis, num_images=3)
            
            # 4. Criar campanha completa
            campaign = create_complete_campaign(analysis, copies, images)
            
            return {
                "success": True,
                "mode": "ai_real",
                "services_used": ai_generator_real.is_available(),
                "prompt_original": prompt,
                "analise_produto": analysis,
                "copies_geradas": copies,
                "imagens_geradas": images,
                "campanha_completa": campaign
            }
        else:
            # Fallback para IA local
            logger.info("🔄 Usando IA Local (fallback)")
            return await generate_local_campaign(request)
            
    except Exception as e:
        logger.error(f"❌ Erro na geração: {str(e)}")
        raise HTTPException(500, f"Erro no processamento: {str(e)}")

@app.post("/api/ai/generate-local")
async def generate_local_campaign(request: dict):
    """
    Gerador local inteligente - funciona 100% offline
    """
    try:
        prompt = request.get("prompt", "")
        if not prompt:
            raise HTTPException(400, "Prompt é obrigatório")
        
        logger.info(f"🏠 Gerando campanha local para: {prompt[:50]}...")
        
        # Análise local
        analysis = analyze_product_local(prompt)
        
        # Gerar copies locais
        copies = generate_copies_local(analysis)
        
        # Gerar imagens placeholder
        images = generate_images_local(analysis)
        
        # Criar campanha
        campaign = create_complete_campaign(analysis, copies, images)
        
        return {
            "success": True,
            "mode": "local",
            "prompt_original": prompt,
            "analise_produto": analysis,
            "copies_geradas": copies,
            "imagens_geradas": images,
            "campanha_completa": campaign,
            "sistema": "IA_LOCAL_INTELIGENTE",
            "custo": "R$ 0,00"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na geração local: {str(e)}")
        raise HTTPException(500, f"Erro: {str(e)}")

# ==================== FUNÇÕES DA IA LOCAL ====================

def analyze_product_local(prompt: str) -> dict:
    """Análise local de produtos"""
    prompt_lower = prompt.lower()
    
    brand_info = detect_brand_and_model(prompt_lower)
    condition_info = detect_product_condition(prompt_lower)
    price_info = calculate_smart_price(brand_info, condition_info, prompt_lower)
    audience_info = determine_target_audience(brand_info, price_info)
    
    return {
        "produto_identificado": prompt,
        "marca": brand_info["brand"],
        "modelo_especifico": brand_info["model"],
        "categoria": condition_info["condition"],
        "caracteristicas_principais": brand_info["features"],
        "publico_alvo_sugerido": audience_info["description"],
        "segmentacao_demografica": audience_info["demographics"],
        "preco_estimado": price_info["range"],
        "preco_competitivo": price_info["competitive_position"],
        "pontos_de_venda": generate_selling_points(brand_info, condition_info),
        "diferenciais_competitivos": generate_competitive_advantages(brand_info, condition_info),
        "estrategia_recomendada": recommend_strategy(brand_info, price_info, audience_info)
    }

def detect_brand_and_model(prompt_lower: str) -> dict:
    """Detecta marca e modelo"""
    
    brand_patterns = {
        "apple": {
            "brand": "Apple",
            "models": {
                "iphone 15 pro max": {"model": "iPhone 15 Pro Max", "tier": "premium", "features": ["Tela ProMotion 6.7\"", "Câmera 48MP", "Chip A17 Pro"]},
                "iphone 15 pro": {"model": "iPhone 15 Pro", "tier": "premium", "features": ["Tela ProMotion 6.1\"", "Câmera 48MP", "Chip A17 Pro"]},
                "iphone 15": {"model": "iPhone 15", "tier": "standard", "features": ["Tela 6.1\"", "Câmera 48MP", "Chip A16"]},
                "iphone 14": {"model": "iPhone 14", "tier": "standard", "features": ["Tela 6.1\"", "Câmera 12MP", "Chip A15"]},
                "macbook": {"model": "MacBook", "tier": "premium", "features": ["Chip M-series", "Retina Display", "Battery life"]},
                "ipad": {"model": "iPad", "tier": "standard", "features": ["Tela Retina", "Apple Pencil", "Multitasking"]}
            }
        },
        "samsung": {
            "brand": "Samsung",
            "models": {
                "galaxy s24 ultra": {"model": "Galaxy S24 Ultra", "tier": "premium", "features": ["Tela 6.8\" AMOLED", "Câmera 200MP", "S Pen"]},
                "galaxy s24": {"model": "Galaxy S24", "tier": "standard", "features": ["Tela 6.2\" AMOLED", "Câmera 50MP", "5G"]},
                "galaxy s23": {"model": "Galaxy S23", "tier": "standard", "features": ["Tela 6.1\" AMOLED", "Câmera 50MP", "Snapdragon"]}
            }
        },
        "xiaomi": {
            "brand": "Xiaomi", 
            "models": {
                "xiaomi 14": {"model": "Xiaomi 14", "tier": "premium", "features": ["AMOLED", "Câmera Leica", "Fast Charging"]},
                "redmi": {"model": "Redmi", "tier": "budget", "features": ["Custo-benefício", "Bateria", "MIUI"]},
                "poco": {"model": "POCO", "tier": "budget", "features": ["Gaming", "Preço acessível", "120Hz"]}
            }
        }
    }
    
    detected_brand = None
    detected_model = None
    
    for brand_key, brand_data in brand_patterns.items():
        if brand_key in prompt_lower:
            detected_brand = brand_data
            
            for model_key, model_data in brand_data["models"].items():
                if all(word in prompt_lower for word in model_key.split()):
                    detected_model = model_data
                    break
            break
    
    if not detected_brand:
        return {
            "brand": "Premium",
            "model": "Produto Premium",
            "tier": "standard",
            "features": ["Tecnologia avançada", "Design moderno", "Performance"]
        }
    
    if not detected_model:
        detected_model = list(detected_brand["models"].values())[0]
    
    return {
        "brand": detected_brand["brand"],
        "model": detected_model["model"],
        "tier": detected_model["tier"],
        "features": detected_model["features"]
    }

def detect_product_condition(prompt_lower: str) -> dict:
    """Detecta condição do produto"""
    
    conditions = {
        "seminovo": {"condition": "seminovo", "price_factor": 0.75, "description": "estado impecável"},
        "usado": {"condition": "usado", "price_factor": 0.60, "description": "com sinais de uso"},
        "novo": {"condition": "novo", "price_factor": 1.0, "description": "lacrado de fábrica"},
        "outlet": {"condition": "outlet", "price_factor": 0.85, "description": "produto de vitrine"}
    }
    
    for pattern, info in conditions.items():
        if pattern in prompt_lower:
            return info
    
    return conditions["novo"]

def calculate_smart_price(brand_info: dict, condition_info: dict, prompt_lower: str) -> dict:
    """Calcula preço inteligente"""
    
    base_prices = {
        "Apple": {"premium": 6000, "standard": 4000},
        "Samsung": {"premium": 5000, "standard": 3000}, 
        "Xiaomi": {"premium": 3000, "budget": 1500},
        "Premium": {"standard": 2500}
    }
    
    brand = brand_info["brand"]
    tier = brand_info["tier"]
    
    base_price = base_prices.get(brand, {}).get(tier, 2500)
    
    # Ajuste por armazenamento
    if "1tb" in prompt_lower or "1000gb" in prompt_lower:
        base_price += 1000
    elif "512gb" in prompt_lower:
        base_price += 500
    elif "256gb" in prompt_lower:
        base_price += 250
    
    final_price = int(base_price * condition_info["price_factor"])
    
    return {
        "range": f"R$ {final_price - 300} - R$ {final_price + 300}",
        "competitive_position": "Preço competitivo" if tier == "standard" else "Premium"
    }

def determine_target_audience(brand_info: dict, price_info: dict) -> dict:
    """Determina público-alvo"""
    
    audiences = {
        "Apple": {
            "description": "Usuários Apple, profissionais criativos, early adopters",
            "demographics": {
                "idade": "25-50 anos",
                "renda": "Classe A e B",
                "interesses": ["Tecnologia", "Design", "Produtividade"],
                "comportamento": "Valorizam qualidade e status"
            }
        },
        "Samsung": {
            "description": "Profissionais, tech enthusiasts, corporativo",
            "demographics": {
                "idade": "28-55 anos", 
                "renda": "Classe B e C",
                "interesses": ["Inovação", "Fotografia", "Android"],
                "comportamento": "Buscam funcionalidade"
            }
        },
        "Xiaomi": {
            "description": "Jovens profissionais, gamers, custo-benefício",
            "demographics": {
                "idade": "18-35 anos",
                "renda": "Classe B, C e D",
                "interesses": ["Gaming", "Tecnologia", "Personalização"],
                "comportamento": "Pesquisam antes de comprar"
            }
        }
    }
    
    return audiences.get(brand_info["brand"], {
        "description": "Usuários de tecnologia",
        "demographics": {
            "idade": "20-45 anos",
            "renda": "Classe B e C",
            "interesses": ["Tecnologia", "Valor"],
            "comportamento": "Compram com pesquisa"
        }
    })

def generate_selling_points(brand_info: dict, condition_info: dict) -> list:
    """Gera pontos de venda"""
    
    base_points = brand_info["features"][:3]
    
    condition_points = {
        "novo": ["Lacrado", "Garantia integral", "Nota fiscal"],
        "seminovo": ["Estado impecável", "Garantia", "Preço imbatível"],
        "usado": ["Testado", "Custo-benefício", "Pronta entrega"],
        "outlet": ["Vitrine", "Desconto", "Garantia loja"]
    }
    
    return base_points + condition_points.get(condition_info["condition"], [])

def generate_competitive_advantages(brand_info: dict, condition_info: dict) -> list:
    """Gera vantagens competitivas"""
    
    return [
        f"Único {brand_info['model']} {condition_info['condition']} nesta faixa",
        "Procedência garantida", 
        "Suporte técnico incluído",
        "Parcelamento 12x sem juros",
        "Entrega expressa"
    ]

def recommend_strategy(brand_info: dict, price_info: dict, audience_info: dict) -> str:
    """Recomenda estratégia"""
    
    if brand_info["tier"] == "premium":
        return "Estratégia premium - exclusividade e qualidade"
    elif "competitivo" in price_info["competitive_position"]:
        return "Estratégia de valor - custo-benefício"
    else:
        return "Estratégia de acesso - democratização"

def generate_copies_local(analysis: dict) -> list:
    """Gera copies locais"""
    
    produto = analysis["produto_identificado"]
    marca = analysis["marca"]
    modelo = analysis["modelo_especifico"]
    preco = analysis["preco_estimado"]
    
    copies = []
    
    # Copy 1 - Estratégica
    if "premium" in analysis.get("estrategia_recomendada", "").lower():
        copy1 = f"✨ {modelo} - Exclusividade {marca} para os mais exigentes!"
    else:
        copy1 = f"🔥 {modelo} - Performance {marca} com preço justo!"
    
    # Copy 2 - Técnica
    features = ", ".join(analysis["caracteristicas_principais"][:2])
    copy2 = f"⚡ {modelo} com {features}. Tecnologia que impressiona!"
    
    # Copy 3 - Urgência
    copy3 = f"🏆 {modelo} por {preco}! Últimas unidades com frete grátis!"
    
    copies = [
        {
            "id": 1,
            "titulo": "Copy Estratégica",
            "texto": copy1,
            "estrategia": "POSICIONAMENTO", 
            "confidence": 0.85,
            "ctr_estimado": "4.2%",
            "generated_by": "local"
        },
        {
            "id": 2,
            "titulo": "Copy Técnica", 
            "texto": copy2,
            "estrategia": "BENEFÍCIOS",
            "confidence": 0.82,
            "ctr_estimado": "3.8%",
            "generated_by": "local"
        },
        {
            "id": 3,
            "titulo": "Copy Urgência",
            "texto": copy3, 
            "estrategia": "URGÊNCIA",
            "confidence": 0.80,
            "ctr_estimado": "4.5%",
            "generated_by": "local"
        }
    ]
    
    return copies

def generate_images_local(analysis: dict) -> list:
    """Gera placeholders de imagem"""
    
    marca = analysis["marca"]
    modelo = analysis.get("modelo_especifico", "Produto")
    
    brand_colors = {
        "Apple": ("000000", "ffffff"),
        "Samsung": ("1428a0", "ffffff"),
        "Xiaomi": ("ff6900", "ffffff"),
        "Premium": ("2c3e50", "ecf0f1")
    }
    
    bg_color, text_color = brand_colors.get(marca, ("333333", "ffffff"))
    
    return [
        {
            "id": 1,
            "url": f"https://via.placeholder.com/1080x1080/{bg_color}/{text_color}?text={marca}+{modelo}",
            "style": "Feed",
            "description": f"Imagem para feed {modelo}",
            "generated_by": "placeholder",
            "confidence": 0.70
        },
        {
            "id": 2,
            "url": f"https://via.placeholder.com/1080x1920/{bg_color}/{text_color}?text={marca}+Story",
            "style": "Story",
            "description": f"Story {modelo}",
            "generated_by": "placeholder",
            "confidence": 0.68
        },
        {
            "id": 3,
            "url": f"https://via.placeholder.com/1200x630/{bg_color}/{text_color}?text={marca}+Ad",
            "style": "Banner",
            "description": f"Banner {modelo}",
            "generated_by": "placeholder",
            "confidence": 0.65
        }
    ]

def create_complete_campaign(analysis: dict, copies: list, images: list) -> dict:
    """Cria campanha completa"""
    
    tier = analysis.get("categoria", "standard")
    if "premium" in analysis.get("estrategia_recomendada", "").lower():
        budget_daily = 300
    elif tier == "novo":
        budget_daily = 200
    else:
        budget_daily = 150
    
    return {
        "nome_campanha": f"Campanha {analysis['marca']} - {analysis.get('modelo_especifico', 'Premium')}",
        "objetivo": "CONVERSIONS",
        "orcamento": {
            "diario": budget_daily,
            "duracao": "7 dias",
            "total": budget_daily * 7
        },
        "segmentacao": analysis.get("segmentacao_demografica", {}),
        "copies_selecionadas": copies[:2],
        "imagens_selecionadas": images[:2],
        "metricas_esperadas": {
            "ctr": "3.5-4.5%",
            "cpc": "R$ 0.80-1.50",
            "conversoes": "50-150"
        }
    }

# ==================== ENDPOINTS DE TESTE ====================

@app.get("/test")
async def test_route():
    """Endpoint de teste"""
    return {
        "test": "funcionando",
        "server": "FastAPI",
        "port": 8080,
        "ai_status": AI_STATUS,
        "api_keys": settings.get_api_status()
    }

@app.post("/api/test/services")
async def test_services():
    """Testa disponibilidade dos serviços"""
    
    results = {
        "ai_generator_real": None,
        "openai": False,
        "replicate": False
    }
    
    # Testar AI Generator Real
    if ai_generator_real:
        results["ai_generator_real"] = ai_generator_real.is_available()
    
    # Verificar API keys
    api_status = settings.get_api_status()
    results["openai"] = api_status["openai"]["configured"]
    results["replicate"] = api_status["replicate"]["configured"]
    
    return {
        "timestamp": "2024-01-01",
        "services": results,
        "recommendation": "Configure API keys no arquivo .env" if not (results["openai"] or results["replicate"]) else "Pronto para usar!"
    }

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Executado quando o servidor inicia"""
    logger.info("\n" + "="*50)
    logger.info("🚀 SISTEMA DE AUTOMAÇÃO DE ANÚNCIOS v2.0")
    logger.info("="*50)
    logger.info(f"📡 Servidor: http://localhost:8080")
    logger.info(f"📚 Docs: http://localhost:8080/docs")
    
    # Status das APIs
    api_status = settings.get_api_status()
    logger.info("\n📊 Status das APIs:")
    logger.info(f"   OpenAI: {'✅' if api_status['openai']['configured'] else '❌'}")
    logger.info(f"   Replicate: {'✅' if api_status['replicate']['configured'] else '❌'}")
    logger.info(f"   AI Generator: {AI_STATUS.get('ai_real', 'inactive')}")
    logger.info("="*50 + "\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)