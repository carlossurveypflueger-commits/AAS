from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class ProductAnalysisRequest(BaseModel):
    prompt: str
    user_preferences: Optional[Dict[str, Any]] = {}

class ProductAnalysis(BaseModel):
    produto_identificado: str
    marca: str
    categoria: str
    caracteristicas_principais: List[str]
    publico_alvo_sugerido: str
    tom_de_comunicacao: str
    preco_estimado: str
    pontos_de_venda: List[str]
    keywords_sugeridas: List[str]

class CopyVariation(BaseModel):
    id: int
    copy: str
    strategy: str
    confidence: float
    estimated_ctr: float

class AIGenerationResponse(BaseModel):
    product_analysis: ProductAnalysis
    copy_variations: List[CopyVariation]
    generation_time: float
    ai_used: str