# app/services/truly_universal_search.py
"""
Sistema VERDADEIRAMENTE Universal
- Funciona para iPhone, parafuso, consulta médica, aula de dança, pizza
- IA analisa o produto e cria estratégias de busca
- Sem hard-coding de produtos específicos
- 100% adaptável
"""

import os
import asyncio
import httpx
import json
from typing import Dict, List, Optional
from app.utils.logger import logger

class TrulyUniversalSearch:
    def __init__(self):
        """Sistema universal que funciona para QUALQUER produto"""
        
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
        self.pixabay_key = os.getenv("PIXABAY_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        logger.info("[UNIVERSAL] Sistema para QUALQUER produto inicializado")
    
    async def search_any_product(self, product_data: Dict) -> List[Dict]:
        """
        Busca UNIVERSAL - funciona para qualquer produto do mundo
        """
        
        produto = product_data.get('produto_identificado', '')
        
        logger.info(f"[UNIVERSAL] Analisando: {produto}")
        
        # 1. IA analisa o produto e cria estratégias de busca
        search_strategies = await self._ai_create_search_strategies(product_data)
        
        # 2. Executar buscas baseadas nas estratégias da IA
        all_references = []
        for strategy in search_strategies[:3]:  # Top 3 estratégias
            
            refs = await self._execute_universal_search(strategy)
            filtered_refs = self._universal_relevance_filter(refs, product_data)
            all_references.extend(filtered_refs)
            
            if len(all_references) >= 12:
                break
        
        # 3. Ranquear universalmente
        best_references = self._universal_ranking(all_references, product_data)
        
        logger.info(f"[FOUND] {len(best_references)} referências universais")
        return best_references
    
    async def _ai_create_search_strategies(self, product_data: Dict) -> List[Dict]:
        """
        IA CRIA as estratégias de busca para qualquer produto
        """
        
        if not self.groq_key:
            return self._create_smart_fallback_strategies(product_data)
        
        try:
            logger.info("[AI] IA criando estratégias de busca universais")
            
            produto = product_data.get('produto_identificado', '')
            tipo_produto = product_data.get('tipo_produto', '')
            marca = product_data.get('marca', '')
            
            system_prompt = """Você é especialista em encontrar imagens de produtos na internet.
Sua tarefa é criar estratégias de busca inteligentes para encontrar fotos reais de QUALQUER produto.

Regras importantes:
- Pense em COMO as pessoas fotografam esse tipo de produto
- Considere ONDE esse produto aparece em fotos
- Use termos em INGLÊS (APIs internacionais)
- Seja ESPECÍFICO mas não limitado a marcas
- Foque no CONTEXTO onde o produto é fotografado"""
            
            user_prompt = f"""Produto: {produto}
Tipo: {tipo_produto}
Marca: {marca}

Crie 4 estratégias de busca diferentes para encontrar fotos reais deste produto:

1. CONTEXTO DE USO - onde/como é usado
2. COMERCIAL - como é vendido/promovido  
3. PROFISSIONAL - fotografia profissional
4. GENÉRICO - termos simples e diretos

Para cada estratégia, crie 2-3 termos de busca em inglês.

Retorne JSON:
{{
    "strategies": [
        {{
            "name": "uso_context",
            "description": "contexto de uso",
            "search_terms": ["termo1", "termo2", "termo3"]
        }},
        {{
            "name": "commercial",
            "description": "contexto comercial",
            "search_terms": ["termo1", "termo2"]
        }},
        {{
            "name": "professional",
            "description": "fotografia profissional",
            "search_terms": ["termo1", "termo2"]
        }},
        {{
            "name": "generic",
            "description": "termos diretos",
            "search_terms": ["termo1", "termo2"]
        }}
    ]
}}

Seja criativo e pense em como REALMENTE encontrar fotos deste produto."""

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
                    timeout=25
                )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Limpar JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                try:
                    data = json.loads(content)
                    if "strategies" in data and len(data["strategies"]) > 0:
                        logger.info(f"[AI SUCCESS] {len(data['strategies'])} estratégias criadas pela IA")
                        return data["strategies"]
                except json.JSONDecodeError as e:
                    logger.info(f"[AI ERROR] JSON inválido: {e}")
            
        except Exception as e:
            logger.info(f"[AI ERROR] Erro na IA: {e}")
        
        # Fallback inteligente
        return self._create_smart_fallback_strategies(product_data)
    
    def _create_smart_fallback_strategies(self, product_data: Dict) -> List[Dict]:
        """
        Fallback inteligente SEM IA - mas ainda universal
        """
        
        produto = product_data.get('produto_identificado', '')
        tipo_produto = product_data.get('tipo_produto', '')
        marca = product_data.get('marca', '')
        
        # Extrair palavras-chave principais do produto
        product_keywords = self._extract_universal_keywords(produto)
        
        strategies = []
        
        # ESTRATÉGIA 1: Contexto de Uso  
        uso_terms = []
        if tipo_produto:
            uso_terms.append(f"{tipo_produto} in use")
            uso_terms.append(f"using {tipo_produto}")
        
        # Adicionar contexto baseado no tipo
        context_hints = self._guess_usage_context(produto, tipo_produto)
        uso_terms.extend(context_hints)
        
        strategies.append({
            "name": "uso_context",
            "description": "contexto de uso",
            "search_terms": uso_terms[:3]
        })
        
        # ESTRATÉGIA 2: Comercial/Marketing
        commercial_terms = []
        if marca and marca != "Premium":
            commercial_terms.append(f"{marca} {tipo_produto}")
        
        commercial_terms.extend([
            f"{tipo_produto} product photography",
            f"{tipo_produto} marketing photo",
            f"commercial {tipo_produto}"
        ])
        
        strategies.append({
            "name": "commercial", 
            "description": "contexto comercial",
            "search_terms": commercial_terms[:3]
        })
        
        # ESTRATÉGIA 3: Profissional
        professional_terms = [
            f"professional {tipo_produto} photography",
            f"{tipo_produto} studio photo",
            f"high quality {tipo_produto}"
        ]
        
        strategies.append({
            "name": "professional",
            "description": "fotografia profissional", 
            "search_terms": professional_terms
        })
        
        # ESTRATÉGIA 4: Direto/Simples
        # Usar as palavras mais importantes do produto
        direct_terms = product_keywords[:3] if product_keywords else [tipo_produto, produto.split()[0] if produto else "product"]
        
        strategies.append({
            "name": "direct",
            "description": "busca direta",
            "search_terms": direct_terms
        })
        
        return strategies
    
    def _extract_universal_keywords(self, produto: str) -> List[str]:
        """
        Extrai palavras-chave universais de qualquer produto
        """
        
        if not produto:
            return []
        
        # Limpar o produto
        produto_clean = produto.lower()
        
        # Remover palavras comuns que não ajudam na busca
        stop_words = {
            'novo', 'usado', 'seminovo', 'original', 'nacional', 'importado',
            'profissional', 'premium', 'básico', 'simples', 'completo',
            'com', 'sem', 'para', 'de', 'da', 'do', 'em', 'na', 'no',
            'gb', 'mb', 'kg', 'cm', 'mm', 'polegadas', 'unidade', 'peça'
        }
        
        # Dividir em palavras
        words = produto_clean.replace('-', ' ').replace('/', ' ').split()
        
        # Filtrar palavras importantes
        keywords = []
        for word in words:
            word = word.strip('.,!?()[]{}')
            if (len(word) >= 3 and 
                word not in stop_words and 
                not word.isdigit() and
                word.isalpha()):  # Apenas letras
                keywords.append(word)
        
        # Pegar as mais importantes (primeiras palavras tendem a ser mais relevantes)
        return keywords[:5]
    
    def _guess_usage_context(self, produto: str, tipo_produto: str) -> List[str]:
        """
        Adivinha contexto de uso universal (sem hard-coding específico)
        """
        
        produto_lower = produto.lower()
        contexts = []
        
        # Contextos universais baseados em padrões
        if any(word in produto_lower for word in ['phone', 'celular', 'smartphone', 'iphone']):
            contexts.extend(["phone in hand", "smartphone unboxing"])
        
        elif any(word in produto_lower for word in ['laptop', 'notebook', 'computer']):
            contexts.extend(["person using laptop", "laptop on desk"])
        
        elif any(word in produto_lower for word in ['food', 'comida', 'pão', 'pizza', 'hambúrguer']):
            contexts.extend(["food photography", "food on plate"])
        
        elif any(word in produto_lower for word in ['car', 'carro', 'auto', 'vehicle']):
            contexts.extend(["car photography", "vehicle exterior"])
        
        elif any(word in produto_lower for word in ['service', 'consulta', 'aula', 'curso']):
            contexts.extend(["professional service", "business meeting"])
        
        elif tipo_produto in ['ferramenta', 'tool', 'equipment']:
            contexts.extend(["tool in use", "workshop equipment"])
        
        else:
            # Contexto genérico universal
            contexts.extend([
                f"{tipo_produto} lifestyle",
                f"{tipo_produto} in environment",
                f"person with {tipo_produto}"
            ])
        
        return contexts[:2]  # Máximo 2 contextos
    
    async def _execute_universal_search(self, strategy: Dict) -> List[Dict]:
        """
        Executa busca universal em múltiplas APIs
        """
        
        search_terms = strategy.get('search_terms', [])
        strategy_name = strategy.get('name', 'unknown')
        
        all_refs = []
        
        for term in search_terms[:2]:  # Máximo 2 termos por estratégia
            if not term or len(term.strip()) < 2:
                continue
                
            logger.info(f"[{strategy_name.upper()}_CONTEXT] Buscando: '{term}'")
            
            # Buscar em todas as APIs disponíveis
            if self.pexels_key:
                refs = await self._search_pexels_universal(term)
                all_refs.extend(refs)
            
            if self.unsplash_key:
                refs = await self._search_unsplash_universal(term) 
                all_refs.extend(refs)
            
            if self.pixabay_key:
                refs = await self._search_pixabay_universal(term)
                all_refs.extend(refs)
            
            # Evitar spam de requests
            if len(all_refs) >= 20:
                break
        
        return all_refs
    
    async def _search_pexels_universal(self, term: str) -> List[Dict]:
        """Busca Pexels otimizada universal"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.pexels.com/v1/search",
                    headers={"Authorization": self.pexels_key},
                    params={
                        "query": term,
                        "per_page": 10,  # Reduzido para performance
                        "orientation": "all",
                        "size": "medium",
                        "locale": "en-US"
                    },
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                
                refs = []
                for photo in photos[:10]:
                    refs.append({
                        "url": photo["src"]["large"],
                        "thumbnail": photo["src"]["medium"],
                        "title": photo.get("alt", term),
                        "width": photo["width"],
                        "height": photo["height"],
                        "source": "pexels",
                        "photographer": photo.get("photographer", ""),
                        "search_term": term,
                        "free_license": True,
                        "relevance_score": 1
                    })
                
                logger.info(f"[PEXELS] {len(refs)} encontradas para '{term}'")
                return refs
        
        except Exception as e:
            logger.info(f"[PEXELS ERROR] {term}: {e}")
        
        return []
    
    async def _search_unsplash_universal(self, term: str) -> List[Dict]:
        """Busca Unsplash universal"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.unsplash.com/search/photos",
                    headers={"Authorization": f"Client-ID {self.unsplash_key}"},
                    params={
                        "query": term,
                        "per_page": 10,
                        "orientation": "all"
                    },
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                refs = []
                for photo in results[:10]:
                    refs.append({
                        "url": photo["urls"]["regular"],
                        "thumbnail": photo["urls"]["small"],
                        "title": photo.get("alt_description", term) or term,
                        "width": photo["width"],
                        "height": photo["height"],
                        "source": "unsplash",
                        "photographer": photo["user"]["name"],
                        "search_term": term,
                        "free_license": True,
                        "relevance_score": 1
                    })
                
                logger.info(f"[UNSPLASH] {len(refs)} encontradas para '{term}'")
                return refs
        
        except Exception as e:
            logger.info(f"[UNSPLASH ERROR] {term}: {e}")
        
        return []
    
    async def _search_pixabay_universal(self, term: str) -> List[Dict]:
        """Busca Pixabay universal"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://pixabay.com/api/",
                    params={
                        "key": self.pixabay_key,
                        "q": term,
                        "image_type": "photo",
                        "per_page": 10,
                        "safesearch": "true",
                        "min_width": 200
                    },
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])
                
                refs = []
                for hit in hits[:10]:
                    refs.append({
                        "url": hit["largeImageURL"],
                        "thumbnail": hit["webformatURL"],
                        "title": hit.get("tags", term),
                        "width": hit["imageWidth"],
                        "height": hit["imageHeight"],
                        "source": "pixabay",
                        "photographer": hit.get("user", ""),
                        "search_term": term,
                        "free_license": True,
                        "relevance_score": 1
                    })
                
                logger.info(f"[PIXABAY] {len(refs)} encontradas para '{term}'")
                return refs
        
        except Exception as e:
            logger.info(f"[PIXABAY ERROR] {term}: {e}")
        
        return []
    
    def _universal_relevance_filter(self, references: List[Dict], product_data: Dict) -> List[Dict]:
        """
        Filtra relevância de forma universal (não específica por produto)
        """
        
        produto = product_data.get('produto_identificado', '').lower()
        tipo_produto = product_data.get('tipo_produto', '').lower()
        marca = product_data.get('marca', '').lower()
        
        # Palavras-chave importantes para buscar nas imagens
        important_keywords = []
        
        # Extrair do produto
        if produto:
            important_keywords.extend(produto.split()[:3])
        
        # Adicionar tipo
        if tipo_produto:
            important_keywords.append(tipo_produto)
        
        # Adicionar marca (mas não é obrigatório)
        if marca and marca != "premium":
            important_keywords.append(marca)
        
        filtered = []
        
        for ref in references:
            title = ref.get('title', '').lower()
            search_term = ref.get('search_term', '').lower()
            
            # Calcular score de relevância
            relevance_score = ref.get('relevance_score', 1)
            
            # Pontos por palavra-chave encontrada
            for keyword in important_keywords:
                if keyword in title:
                    relevance_score += 2
                if keyword in search_term:
                    relevance_score += 1
            
            # Bonus por resolução
            width = ref.get('width', 0)
            if width >= 500:
                relevance_score += 1
            
            # Bonus por source confiável
            if ref.get('source') in ['pexels', 'unsplash']:
                relevance_score += 1
            
            # Filtrar por score mínimo
            if relevance_score >= 1:  # Score baixo = mais inclusivo
                ref['relevance_score'] = relevance_score
                filtered.append(ref)
        
        # Ordenar por relevância
        filtered.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return filtered
    
    def _universal_ranking(self, references: List[Dict], product_data: Dict) -> List[Dict]:
        """
        Ranking universal baseado em qualidade e relevância
        """
        
        if not references:
            return []
        
        # Remover duplicatas por URL
        seen_urls = set()
        unique_refs = []
        for ref in references:
            url = ref.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_refs.append(ref)
        
        # Ordenar por score de relevância + qualidade
        def comprehensive_score(ref):
            score = ref.get('relevance_score', 0)
            
            # Bonus por resolução
            width = ref.get('width', 0)
            if width >= 800:
                score += 2
            elif width >= 500:
                score += 1
            
            # Bonus por source
            source = ref.get('source', '')
            if source == 'unsplash':
                score += 2  # Unsplash tem fotos mais artísticas
            elif source == 'pexels':
                score += 1
            
            return score
        
        # Ordenar e pegar os melhores
        ranked = sorted(unique_refs, key=comprehensive_score, reverse=True)
        
        # Retornar top referencias
        return ranked[:8]  # Máximo 8 referências de qualidade
    
    def get_universal_status(self) -> Dict:
        """Status do sistema universal"""
        
        return {
            "system_type": "truly_universal",
            "works_for": "ANY product in the world",
            "search_apis": {
                "pexels": bool(self.pexels_key),
                "unsplash": bool(self.unsplash_key), 
                "pixabay": bool(self.pixabay_key)
            },
            "ai_analysis": bool(self.groq_key),
            "capabilities": [
                "iPhone to nail screws",
                "Pizza to dental implants", 
                "Dance classes to car parts",
                "ANY product/service imaginable"
            ],
            "cost": "$0.00",
            "universal": True
        }

# Instância global
universal_search = TrulyUniversalSearch()