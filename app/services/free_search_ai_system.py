# app/services/free_search_ai_system.py
"""
Sistema 100% GRATUITO para desenvolvimento e testes
- Pexels API (gratuita) para busca de imagens
- Unsplash API (gratuita) como backup
- HuggingFace (gratuito) para geração de IA
- Groq (gratuito) para análise
- Funciona para QUALQUER produto
"""

import os
import asyncio
import httpx
import json
import base64
from typing import Dict, List, Optional
from app.utils.logger import logger
from urllib.parse import quote_plus

class FreeSearchAISystem:
    def __init__(self):
        """Sistema 100% gratuito para testes"""
        
        # APIs GRATUITAS de busca
        self.pexels_key = os.getenv("PEXELS_API_KEY")          # GRATUITO
        self.unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")   # GRATUITO  
        self.pixabay_key = os.getenv("PIXABAY_API_KEY")        # GRATUITO
        
        # APIs GRATUITAS de IA
        self.groq_key = os.getenv("GROQ_API_KEY")              # GRATUITO
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")         # GRATUITO
        
        # Estratégia de busca (priorizar gratuitas)
        if self.pexels_key:
            self.search_strategy = "pexels"
        elif self.unsplash_key:
            self.search_strategy = "unsplash"
        elif self.pixabay_key:
            self.search_strategy = "pixabay"
        else:
            self.search_strategy = "web_scraping"  # Último recurso
        
        # Estratégia de IA
        if self.hf_token:
            self.ai_strategy = "huggingface"
        else:
            self.ai_strategy = "mock_enhanced"
        
        logger.info(f"[FREE] 🆓 Sistema 100% GRATUITO inicializado")
        logger.info(f"[SEARCH] Estratégia: {self.search_strategy}")
        logger.info(f"[AI] Estratégia: {self.ai_strategy}")
        logger.info(f"[UNIVERSAL] ✅ Funciona para QUALQUER produto")
    
    async def generate_images_with_free_search(self, product_data: Dict, copies: List[Dict], num_images: int = 3) -> List[Dict]:
        """
        Método principal: Busca GRATUITA + IA GRATUITA
        """
        logger.info(f"[FREE] 🆓 Gerando {num_images} imagens com APIs gratuitas")
        
        # 1. BUSCAR imagens gratuitas do produto
        free_references = await self._search_free_product_images(product_data)
        
        # 2. ANALISAR referências gratuitamente  
        analysis = await self._analyze_free_references(free_references, product_data)
        
        # 3. GERAR prompts com Groq (gratuito)
        if self.groq_key:
            prompts = await self._create_prompts_with_groq(analysis, product_data, copies, num_images)
        else:
            prompts = self._create_smart_prompts_free(analysis, product_data, copies, num_images)
        
        # 4. GERAR imagens com HuggingFace (gratuito)
        images = []
        for i, prompt_data in enumerate(prompts):
            
            # Tentar HuggingFace gratuito
            if self.hf_token:
                image = await self._generate_with_huggingface_free(prompt_data, free_references, i + 1)
            else:
                image = None
            
            # Fallback para mock baseado em referências
            if not image:
                image = self._create_reference_based_mock(product_data, prompt_data, free_references, i + 1)
            
            images.append(image)
        
        logger.info(f"[SUCCESS] 🎉 {len(images)} imagens geradas gratuitamente")
        return images
    
    async def _search_free_product_images(self, product_data: Dict) -> List[Dict]:
    """
    Busca UNIVERSAL usando sistema inteligente
    """
    try:
        # Usar o sistema verdadeiramente universal
        from app.services.truly_universal_search import universal_search
        
        logger.info("[UNIVERSAL] Usando busca verdadeiramente universal")
        references = await universal_search.search_any_product(product_data)
        
        if references:
            logger.info(f"[UNIVERSAL SUCCESS] {len(references)} referências encontradas")
            return references
        else:
            logger.info("[UNIVERSAL] Nenhuma referência encontrada, usando fallback")
    
    except ImportError:
        logger.info("[ERROR] Sistema universal não encontrado, usando busca básica")
    except Exception as e:
        logger.info(f"[ERROR] Sistema universal falhou: {e}")
    
    # Fallback para busca básica
    return await self._search_basic_fallback(product_data)

async def _search_basic_fallback(self, product_data: Dict):
    """Fallback básico quando sistema universal falha"""
    
    produto = product_data.get('produto_identificado', '')
    tipo_produto = product_data.get('tipo_produto', '')
    
    # Queries simples e universais
    queries = []
    
    if produto:
        # Limpar produto para busca
        clean_produto = self._clean_product_for_search(produto)
        queries.append(clean_produto)
    
    if tipo_produto:
        queries.append(f"{tipo_produto} photography")
    
    # Termo genérico
    queries.append("product photography")
    
    all_refs = []
    
    for query in queries[:2]:
        logger.info(f"[FALLBACK] Buscando: {query}")
        
        if self.pexels_key:
            refs = await self._search_pexels_free(query)
            all_refs.extend(refs)
        
        if len(all_refs) >= 5:
            break
    
    return all_refs[:5]  # Máximo 5 para fallback

def _clean_product_for_search(self, produto: str) -> str:
    """Limpa produto para busca universal"""
    
    # Remover termos que atrapalham a busca
    noise_terms = [
        'novo', 'usado', 'seminovo', 'original', 'nacional',
        'gb', 'mb', 'tb', '256gb', '512gb', '1tb',
        'polegadas', '"', 'cm', 'mm', 'kg', 'gramas'
    ]
    
    clean = produto.lower()
    
    # Remover termos desnecessários
    for term in noise_terms:
        clean = clean.replace(term, ' ')
    
    # Limpar espaços extras
    clean = ' '.join(clean.split())
    
    # Pegar as primeiras 3 palavras importantes
    words = clean.split()[:3]
    
    return ' '.join(words) if words else produto

# E também atualizar o método _analyze_free_references para ser mais universal:

async def _analyze_free_references(self, references: List[Dict], product_data: Dict) -> Dict:
    """Análise universal das referências"""
    
    logger.info(f"[ANALYSIS] Analisando {len(references)} referências universais")
    
    if not references:
        return self._create_universal_fallback_analysis(product_data)
    
    # Análise baseada em dados reais das referências
    all_titles = [ref.get("title", "") for ref in references]
    all_search_terms = [ref.get("search_term", "") for ref in references]
    combined_text = " ".join(all_titles + all_search_terms).lower()
    
    # Análise universal (não específica por produto)
    analysis = {
        "product_name": product_data.get('produto_identificado'),
        "reference_count": len(references),
        "sources_analyzed": list(set([ref.get("source", "") for ref in references])),
        "search_terms_used": list(set([ref.get("search_term", "") for ref in references])),
        "average_relevance": sum([ref.get('relevance_score', 0) for ref in references]) / len(references),
        "visual_style": self._detect_universal_visual_style(combined_text),
        "typical_composition": self._detect_universal_composition(references),
        "common_background": self._detect_universal_background(combined_text),
        "lighting_pattern": self._detect_universal_lighting(combined_text),
        "quality_indicators": self._assess_universal_quality(references),
        "analysis_quality": "universal_intelligent",
        "sample_references": [ref.get("thumbnail") for ref in references[:3]]
    }
    
    return analysis

def _detect_universal_visual_style(self, text: str) -> str:
    """Detecta estilo visual de forma universal"""
    
    # Padrões universais
    if any(term in text for term in ['professional', 'studio', 'commercial']):
        return "professional commercial style"
    elif any(term in text for term in ['lifestyle', 'natural', 'candid']):
        return "lifestyle natural style"
    elif any(term in text for term in ['artistic', 'creative', 'abstract']):
        return "artistic creative style"
    elif any(term in text for term in ['minimal', 'clean', 'simple']):
        return "minimalist clean style"
    else:
        return "standard photography style"

def _detect_universal_composition(self, references: List[Dict]) -> str:
    """Detecta composição típica universal"""
    
    # Analisar aspect ratios
    landscape_count = 0
    portrait_count = 0
    square_count = 0
    
    for ref in references:
        width = ref.get('width', 1)
        height = ref.get('height', 1)
        
        ratio = width / height if height > 0 else 1
        
        if ratio > 1.3:
            landscape_count += 1
        elif ratio < 0.8:
            portrait_count += 1
        else:
            square_count += 1
    
    total = len(references)
    if total == 0:
        return "balanced composition"
    
    if landscape_count / total > 0.6:
        return "landscape orientation preferred"
    elif portrait_count / total > 0.6:
        return "portrait orientation common"
    else:
        return "mixed orientation styles"

def _detect_universal_background(self, text: str) -> str:
    """Detecta fundo típico universal"""
    
    if any(term in text for term in ['white', 'clean', 'minimal']):
        return "clean light background"
    elif any(term in text for term in ['dark', 'black', 'dramatic']):
        return "dark dramatic background"
    elif any(term in text for term in ['natural', 'outdoor', 'environment']):
        return "natural environment background"
    elif any(term in text for term in ['lifestyle', 'home', 'room']):
        return "lifestyle context background"
    else:
        return "varied background styles"

def _detect_universal_lighting(self, text: str) -> str:
    """Detecta padrão de iluminação universal"""
    
    if any(term in text for term in ['studio', 'professional']):
        return "professional studio lighting"
    elif any(term in text for term in ['natural', 'sunlight', 'daylight']):
        return "natural daylight preferred"
    elif any(term in text for term in ['dramatic', 'moody', 'shadow']):
        return "dramatic moody lighting"
    elif any(term in text for term in ['soft', 'gentle', 'warm']):
        return "soft warm lighting"
    else:
        return "standard lighting setup"

def _assess_universal_quality(self, references: List[Dict]) -> List[str]:
    """Avalia qualidade universal das referências"""
    
    indicators = []
    
    if not references:
        return ["no references available"]
    
    # Avaliar resolução
    high_res_count = len([r for r in references if r.get('width', 0) > 800])
    if high_res_count > 0:
        indicators.append(f"{high_res_count}/{len(references)} high resolution")
    
    # Avaliar diversidade de sources
    sources = set([r.get('source', '') for r in references])
    if len(sources) > 1:
        indicators.append(f"diverse sources: {', '.join(sources)}")
    
    # Avaliar relevância média
    avg_relevance = sum([r.get('relevance_score', 0) for r in references]) / len(references)
    if avg_relevance >= 2:
        indicators.append("high relevance matches")
    elif avg_relevance >= 1:
        indicators.append("moderate relevance matches")
    else:
        indicators.append("basic relevance matches")
    
    # Avaliar se há licenças gratuitas
    free_license_count = len([r for r in references if r.get('free_license')])
    if free_license_count == len(references):
        indicators.append("all free licensed")
    
    return indicators

def _create_universal_fallback_analysis(self, product_data: Dict) -> Dict:
    """Análise fallback universal quando não há referências"""
    
    return {
        "product_name": product_data.get('produto_identificado'),
        "reference_count": 0,
        "sources_analyzed": [],
        "search_terms_used": [],
        "average_relevance": 0,
        "visual_style": "standard commercial photography",
        "typical_composition": "centered product placement",
        "common_background": "neutral background",
        "lighting_pattern": "professional lighting",
        "quality_indicators": ["no references - using intelligent defaults"],
        "analysis_quality": "universal_fallback",
        "sample_references": []
    }
    
    def _create_universal_queries(self, produto: str, tipo_produto: str) -> List[str]:
        """Cria queries universais para qualquer produto"""
        
        queries = []
        
        # Query 1: Produto específico
        if produto:
            # Limpar o produto para busca
            clean_produto = produto.replace('GB', '').replace('256', '').replace('512', '').replace('seminovo', '').replace('usado', '').replace('novo', '').strip()
            queries.append(clean_produto)
        
        # Query 2: Tipo genérico (para contexto)
        if tipo_produto:
            type_translations = {
                'smartphone': 'mobile phone',
                'notebook': 'laptop computer',
                'smart_tv': 'television',
                'fone': 'headphones',
                'smartwatch': 'smart watch',
                'caixa_som': 'speaker',
                'eletronico': 'electronics'
            }
            
            english_type = type_translations.get(tipo_produto, tipo_produto)
            queries.append(english_type)
        
        # Query 3: Contexto profissional
        if produto:
            queries.append(f"{produto.split()[0]} professional")
        
        return queries
    
    async def _search_pexels_free(self, query: str) -> List[Dict]:
        """Pexels - 200 imagens/hora GRATUITO"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.pexels.com/v1/search",
                    headers={
                        "Authorization": self.pexels_key
                    },
                    params={
                        "query": query,
                        "per_page": 15,
                        "orientation": "landscape"
                    },
                    timeout=15
                )
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                
                refs = []
                for photo in photos:
                    refs.append({
                        "url": photo["src"]["large"],
                        "thumbnail": photo["src"]["medium"],
                        "title": photo.get("alt", query),
                        "width": photo["width"],
                        "height": photo["height"],
                        "source": "pexels_free",
                        "photographer": photo.get("photographer", ""),
                        "free_license": True
                    })
                
                logger.info(f"[PEXELS] 🆓 {len(refs)} imagens gratuitas")
                return refs
        
        except Exception as e:
            logger.info(f"[ERROR] Pexels: {e}")
        
        return []
    
    async def _search_unsplash_free(self, query: str) -> List[Dict]:
        """Unsplash - 50 requests/hora GRATUITO"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.unsplash.com/search/photos",
                    headers={
                        "Authorization": f"Client-ID {self.unsplash_key}"
                    },
                    params={
                        "query": query,
                        "per_page": 15,
                        "orientation": "landscape"
                    },
                    timeout=15
                )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                refs = []
                for photo in results:
                    refs.append({
                        "url": photo["urls"]["regular"],
                        "thumbnail": photo["urls"]["small"],
                        "title": photo.get("alt_description", query),
                        "width": photo["width"],
                        "height": photo["height"],
                        "source": "unsplash_free",
                        "photographer": photo["user"]["name"],
                        "free_license": True
                    })
                
                logger.info(f"[UNSPLASH] 🆓 {len(refs)} imagens gratuitas")
                return refs
        
        except Exception as e:
            logger.info(f"[ERROR] Unsplash: {e}")
        
        return []
    
    async def _search_pixabay_free(self, query: str) -> List[Dict]:
        """Pixabay - GRATUITO ilimitado"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://pixabay.com/api/",
                    params={
                        "key": self.pixabay_key,
                        "q": query,
                        "image_type": "photo",
                        "per_page": 15,
                        "safesearch": "true",
                        "min_width": 300
                    },
                    timeout=15
                )
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])
                
                refs = []
                for hit in hits:
                    refs.append({
                        "url": hit["largeImageURL"],
                        "thumbnail": hit["webformatURL"],
                        "title": hit.get("tags", query),
                        "width": hit["imageWidth"],
                        "height": hit["imageHeight"],
                        "source": "pixabay_free",
                        "photographer": hit.get("user", ""),
                        "free_license": True
                    })
                
                logger.info(f"[PIXABAY] 🆓 {len(refs)} imagens gratuitas")
                return refs
        
        except Exception as e:
            logger.info(f"[ERROR] Pixabay: {e}")
        
        return []
    
    async def _search_web_scraping_free(self, query: str) -> List[Dict]:
        """Web scraping como último recurso (cuidado com rate limits)"""
        # Para desenvolvimento, retornar mock references
        logger.info(f"[WEB] 🔍 Simulando busca web para: {query}")
        
        return [
            {
                "url": f"https://via.placeholder.com/800x600/f8f9fa/2c3e50?text={quote_plus(query)}+Real+Ref+{i}",
                "thumbnail": f"https://via.placeholder.com/300x200/f8f9fa/2c3e50?text=Ref+{i}",
                "title": f"{query} - Referência web {i}",
                "width": 800,
                "height": 600,
                "source": "web_simulation",
                "free_license": True
            } for i in range(1, 4)
        ]
    
    def _filter_free_references(self, references: List[Dict], product_data: Dict) -> List[Dict]:
        """Filtra melhores referências gratuitas"""
        
        # Filtrar por qualidade mínima
        quality_refs = [
            ref for ref in references
            if ref.get("width", 0) >= 200 and ref.get("height", 0) >= 200
        ]
        
        # Rankear por relevância
        produto_words = product_data.get('produto_identificado', '').lower().split()
        
        def relevance_score(ref):
            title = ref.get("title", "").lower()
            score = 0
            
            # Pontos por palavra-chave
            for word in produto_words:
                if word in title and len(word) > 2:  # Evitar palavras pequenas
                    score += 2
            
            # Bonus por resolução
            if ref.get("width", 0) > 500:
                score += 1
            
            # Bonus por source confiável
            if ref.get("source") in ["pexels_free", "unsplash_free"]:
                score += 1
            
            return score
        
        ranked = sorted(quality_refs, key=relevance_score, reverse=True)
        
        return ranked[:6]  # Top 6 melhores
    
    async def _analyze_free_references(self, references: List[Dict], product_data: Dict) -> Dict:
        """Análise gratuita das referências"""
        
        logger.info(f"[ANALYSIS] 🔍 Analisando {len(references)} referências gratuitas")
        
        if not references:
            return {
                "product_name": product_data.get('produto_identificado'),
                "reference_count": 0,
                "visual_style": "standard commercial",
                "typical_composition": "centered product",
                "common_background": "clean background",
                "lighting_pattern": "professional lighting",
                "analysis_quality": "basic"
            }
        
        # Análise baseada em títulos e metadados
        all_titles = [ref.get("title", "") for ref in references]
        combined_text = " ".join(all_titles).lower()
        
        analysis = {
            "product_name": product_data.get('produto_identificado'),
            "reference_count": len(references),
            "sources_used": list(set([ref.get("source", "") for ref in references])),
            "visual_style": self._analyze_visual_style_free(combined_text),
            "typical_composition": self._analyze_composition_free(references),
            "common_background": self._analyze_background_free(combined_text),
            "lighting_pattern": self._analyze_lighting_free(combined_text),
            "color_themes": self._analyze_colors_free(combined_text),
            "analysis_quality": "reference_based",
            "sample_references": [ref.get("thumbnail") for ref in references[:3]]
        }
        
        return analysis
    
    def _analyze_visual_style_free(self, text: str) -> str:
        """Analisa estilo visual dos títulos"""
        
        if "professional" in text or "business" in text:
            return "professional commercial style"
        elif "modern" in text or "contemporary" in text:
            return "modern minimalist style"
        elif "lifestyle" in text or "home" in text:
            return "lifestyle contextual style"
        else:
            return "clean product photography style"
    
    def _analyze_composition_free(self, references: List[Dict]) -> str:
        """Analisa composição típica"""
        
        landscape_count = 0
        for ref in references:
            if ref.get("width", 1) > ref.get("height", 1):
                landscape_count += 1
        
        if landscape_count > len(references) / 2:
            return "landscape orientation preferred"
        else:
            return "balanced composition"
    
    def _analyze_background_free(self, text: str) -> str:
        """Analisa fundos comuns"""
        
        if "white" in text or "clean" in text:
            return "clean white background"
        elif "dark" in text or "black" in text:
            return "dark professional background"
        elif "wood" in text or "table" in text:
            return "natural surface background"
        else:
            return "neutral background"
    
    def _analyze_lighting_free(self, text: str) -> str:
        """Analisa padrões de iluminação"""
        
        if "studio" in text:
            return "studio lighting setup"
        elif "natural" in text or "sunlight" in text:
            return "natural lighting preferred"
        else:
            return "professional lighting"
    
    def _analyze_colors_free(self, text: str) -> List[str]:
        """Analisa temas de cor"""
        
        colors = []
        color_words = {
            "white": "clean whites",
            "black": "elegant blacks", 
            "blue": "blue tones",
            "red": "vibrant reds",
            "wood": "natural browns"
        }
        
        for word, desc in color_words.items():
            if word in text:
                colors.append(desc)
        
        return colors or ["neutral palette"]
    
    async def _create_prompts_with_groq(self, analysis: Dict, product_data: Dict, copies: List[Dict], num_images: int) -> List[Dict]:
        """Cria prompts usando Groq GRATUITO"""
        
        try:
            logger.info("[GROQ] 🆓 Gerando prompts com IA gratuita")
            
            strategies = [copy.get('estrategia', 'COMERCIAL') for copy in copies[:num_images]]
            
            system_prompt = f"""Você é especialista em fotografia comercial baseada em referências reais.
Crie prompts para geração de imagem baseados na análise de {analysis['reference_count']} referências reais."""
            
            user_prompt = f"""Produto: {product_data.get('produto_identificado')}
Análise das referências reais:
- Estilo visual: {analysis.get('visual_style')}
- Composição: {analysis.get('typical_composition')}
- Fundo: {analysis.get('common_background')}
- Iluminação: {analysis.get('lighting_pattern')}
- Cores: {analysis.get('color_themes')}

Estratégias das copies: {strategies}

Crie {num_images} prompts em inglês otimizados para HuggingFace, baseados nas referências reais:

JSON:
{{
    "prompts": [
        {{
            "id": 1,
            "strategy": "estratégia",
            "prompt": "prompt em inglês baseado nas referências",
            "style": "estilo baseado na análise"
        }}
    ]
}}"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                
                try:
                    data = json.loads(content)
                    if "prompts" in data:
                        logger.info(f"[SUCCESS] 🤖 {len(data['prompts'])} prompts Groq gerados")
                        return data["prompts"]
                except:
                    pass
        
        except Exception as e:
            logger.info(f"[ERROR] Groq prompts: {e}")
        
        # Fallback
        return self._create_smart_prompts_free(analysis, product_data, copies, num_images)
    
    def _create_smart_prompts_free(self, analysis: Dict, product_data: Dict, copies: List[Dict], num_images: int) -> List[Dict]:
        """Cria prompts inteligentes sem IA"""
        
        produto = product_data.get('produto_identificado')
        visual_style = analysis.get('visual_style', 'commercial')
        background = analysis.get('common_background', 'clean')
        lighting = analysis.get('lighting_pattern', 'professional')
        
        prompts = []
        
        for i in range(num_images):
            strategy = copies[i].get('estrategia', 'COMERCIAL') if i < len(copies) else 'COMERCIAL'
            
            # Base do prompt baseada na análise
            base_prompt = f"professional photography of {produto}, {visual_style}, {background}, {lighting}"
            
            # Modificar por estratégia
            if strategy == "URGÊNCIA":
                enhanced_prompt = f"{base_prompt}, dynamic composition, vibrant energy"
                style = "Dynamic Energy"
            elif strategy == "PREMIUM":
                enhanced_prompt = f"{base_prompt}, luxury aesthetic, sophisticated composition"
                style = "Premium Luxury"
            elif strategy == "GAMER":
                enhanced_prompt = f"{base_prompt}, modern tech environment, RGB accents"
                style = "Gaming Tech"
            else:
                enhanced_prompt = f"{base_prompt}, commercial quality, marketing ready"
                style = "Commercial Standard"
            
            prompts.append({
                'id': i + 1,
                'strategy': strategy,
                'prompt': enhanced_prompt,
                'style': style,
                'reference_based': True
            })
        
        return prompts
    
    async def _generate_with_huggingface_free(self, prompt_data: Dict, references: List[Dict], image_id: int) -> Optional[Dict]:
        """Gera com HuggingFace GRATUITO"""
        
        try:
            logger.info(f"[HF] 🆓 Gerando imagem gratuita {image_id}")
            
            prompt = prompt_data.get('prompt')
            enhanced = f"{prompt}, professional commercial photography, high quality, detailed, masterpiece"
            
            headers = {"Content-Type": "application/json"}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            # Usar modelo gratuito Stable Diffusion
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
                    headers=headers,
                    json={
                        "inputs": enhanced[:500],  # Limitar tamanho
                        "parameters": {
                            "guidance_scale": 7.5,
                            "num_inference_steps": 20
                        }
                    },
                    timeout=60
                )
            
            if response.status_code == 200:
                image_bytes = response.content
                if len(image_bytes) > 2000:  # Verificar se é imagem válida
                    image_b64 = base64.b64encode(image_bytes).decode()
                    
                    logger.info(f"[SUCCESS] 🎨 HuggingFace gratuito - imagem {image_id}")
                    
                    return {
                        'id': image_id,
                        'url': f"data:image/jpeg;base64,{image_b64}",
                        'style': prompt_data.get('style', 'Free AI Generated'),
                        'strategy': prompt_data.get('strategy'),
                        'description': f'Gerado gratuitamente com {len(references)} referências',
                        'generated_by': 'huggingface_free',
                        'confidence': 0.88,
                        'quality': 'free_ai_generated',
                        'reference_count': len(references),
                        'cost': '$0.00',
                        'prompt_used': enhanced[:100] + "..."
                    }
            
            elif response.status_code == 503:
                logger.info("[INFO] HuggingFace modelo carregando...")
            
        except Exception as e:
            logger.info(f"[ERROR] HuggingFace free: {e}")
        
        return None
    
    def _create_reference_based_mock(self, product_data: Dict, prompt_data: Dict, references: List[Dict], image_id: int) -> Dict:
        """Mock baseado em referências gratuitas"""
        
        produto = product_data.get('produto_identificado', 'produto')
        strategy = prompt_data.get('strategy', 'COMERCIAL')
        ref_count = len(references)
        
        # Cores baseadas na análise das referências
        if ref_count > 0:
            # Simular análise de cor baseada no source
            sources = [ref.get('source', '') for ref in references]
            if 'pexels' in str(sources):
                bg_color, text_color = "e8f4fd", "2c3e50"  # Azul claro Pexels
            elif 'unsplash' in str(sources):
                bg_color, text_color = "f8f9fa", "495057"  # Cinza claro Unsplash
            else:
                bg_color, text_color = "ffffff", "333333"  # Branco clean
        else:
            # Cores por estratégia
            strategy_colors = {
                'URGÊNCIA': ('ff4444', 'ffffff'),
                'PREMIUM': ('1a1a1a', 'f5f5f5'),
                'GAMER': ('6f42c1', '00ff41'),
                'COMERCIAL': ('2c3e50', 'ffffff')
            }
            bg_color, text_color = strategy_colors.get(strategy, ('f8f9fa', '2c3e50'))
        
        # Texto informativo
        product_clean = produto.replace(' ', '+')
        text_overlay = f"{product_clean}+FREE+{ref_count}REF"
        
        return {
            'id': image_id,
            'url': f"https://via.placeholder.com/1024x1024/{bg_color}/{text_color}?text={text_overlay}&font-size=24",
            'style': f'Free Reference-based {strategy}',
            'strategy': strategy,
            'description': f'Mock gratuito baseado em {ref_count} referências reais',
            'generated_by': 'free_reference_mock',
            'confidence': 0.80 + (ref_count * 0.03),
            'quality': 'free_reference_informed',
            'reference_count': ref_count,
            'cost': '$0.00',
            'sources_analyzed': list(set([ref.get('source', 'unknown') for ref in references])),
            'note': f'Sistema 100% gratuito - baseado em {ref_count} referências reais'
        }
    
    def get_free_status(self) -> Dict:
        """Status do sistema 100% gratuito"""
        return {
            "cost": "$0.00",
            "search_apis": {
                "pexels": {"available": bool(self.pexels_key), "limit": "200/hour", "cost": "FREE"},
                "unsplash": {"available": bool(self.unsplash_key), "limit": "50/hour", "cost": "FREE"},
                "pixabay": {"available": bool(self.pixabay_key), "limit": "unlimited", "cost": "FREE"}
            },
            "ai_apis": {
                "groq": {"available": bool(self.groq_key), "limit": "generous", "cost": "FREE"},
                "huggingface": {"available": bool(self.hf_token), "limit": "1000/day", "cost": "FREE"}
            },
            "features": {
                "universal_search": True,
                "reference_analysis": True,
                "ai_prompt_generation": bool(self.groq_key),
                "ai_image_generation": bool(self.hf_token),
                "works_for_any_product": True
            },
            "development_ready": True,
            "production_ready": self.groq_key and (self.pexels_key or self.unsplash_key),
            "recommended_apis": [
                "PEXELS_API_KEY (pexels.com/api)",
                "GROQ_API_KEY (console.groq.com)", 
                "HUGGINGFACE_TOKEN (huggingface.co/settings/tokens)"
            ]
        }
    
    def is_free_generation_available(self) -> bool:
        """Verifica se geração gratuita real está disponível"""
        return bool((self.pexels_key or self.unsplash_key or self.pixabay_key) and self.hf_token)

# Instância global
free_search_ai = FreeSearchAISystem()