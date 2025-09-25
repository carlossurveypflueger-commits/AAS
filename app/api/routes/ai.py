from fastapi import APIRouter, HTTPException
from app.services.ai_generator import ai_generator
from app.schemas.ai import ProductAnalysisRequest, AIGenerationResponse
import time

router = APIRouter()

@router.get("/status")
async def ai_status():
    """Verifica status das IAs disponíveis"""
    availability = ai_generator.is_available()
    return {
        "ai_services": availability,
        "total_available": sum(availability.values()),
        "recommended": "claude" if availability["claude"] else "openai" if availability["openai"] else "mock"
    }

@router.post("/analyze-prompt")
async def analyze_product_prompt(request: ProductAnalysisRequest):
    """Analisa um prompt e retorna dados do produto"""
    try:
        start_time = time.time()
        
        # Analisa o produto
        analysis = await ai_generator.analyze_product_prompt(request.prompt)
        
        generation_time = time.time() - start_time
        
        return {
            "success": True,
            "analysis": analysis,
            "generation_time": round(generation_time, 2),
            "ai_used": "claude" if ai_generator.claude_client else "openai" if ai_generator.openai_client else "mock"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@router.post("/generate-copies")
async def generate_copies(request: ProductAnalysisRequest):
    """Gera copies baseado em análise de produto"""
    try:
        start_time = time.time()
        
        # Primeiro analisa o produto
        product_data = await ai_generator.analyze_product_prompt(request.prompt)
        
        # Depois gera as copies
        copies = await ai_generator.generate_copy_variations(product_data, num_variations=3)
        
        generation_time = time.time() - start_time
        
        return {
            "success": True,
            "product_analysis": product_data,
            "copies": copies,
            "generation_time": round(generation_time, 2),
            "ai_used": "claude + openai" if ai_generator.claude_client and ai_generator.openai_client else 
                      "claude" if ai_generator.claude_client else 
                      "openai" if ai_generator.openai_client else "mock"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na geração: {str(e)}")

@router.get("/test")
async def test_ai():
    """Testa o sistema de IA com um exemplo"""
    test_prompt = "iPhone 15 Pro Max 256GB seminovo"
    
    try:
        result = await generate_copies(ProductAnalysisRequest(prompt=test_prompt))
        return result
    except Exception as e:
        return {"error": str(e), "message": "Teste com dados mock"}