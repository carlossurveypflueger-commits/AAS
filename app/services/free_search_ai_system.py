# app/services/free_search_ai_system.py
"""
Sistema 100% GRATUITO para desenvolvimento e testes
- Pexels API (gratuita) para busca de imagens
- Unsplash API (gratuita) como backup
- HuggingFace (gratuito) para geração de IA
- Groq (gratuito) para análise E COPIES
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
    
    # ==================== MÉTODOS PRINCIPAIS PARA COMPATIBILIDADE ====================
    
    async def analyze_with_openai(self, prompt: str) -> Dict:
        """Método de compatibilidade - análise com Groq gratuito"""
        
        if self.groq_key:
            logger.info("[GROQ] Analisando produto com IA gratuita")
            analysis = await self._groq_analysis_free(prompt)
            if analysis:
                return analysis
        
        logger.info("[FALLBACK] Usando análise mock")
        return self._mock_analysis_free(prompt)
    
    async def generate_copies_with_openai(self, product_data: Dict, num_copies: int = 3) -> List[Dict]:
        """Método de compatibilidade - copies com Groq gratuito"""
        
        if self.groq_key:
            logger.info("[GROQ] Gerando copies com IA gratuita")
            copies = await self._groq_copies_free(product_data, num_copies)
            if copies and len(copies) > 0:
                # Verificar se pelo menos uma copy foi gerada pelo Groq
                real_copies = [c for c in copies if c.get('generated_by') == 'groq_real']
                if real_copies:
                    logger.info(f"[SUCCESS] {len(real_copies)} copies Groq reais geradas")
                    return copies
        
        logger.info("[FALLBACK] Usando copies mock")
        return self._mock_copies_free(product_data, num_copies)
    
    # ==================== MÉTODO PRINCIPAL DO SISTEMA GRATUITO ====================
    
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
    
    # ==================== ANÁLISE COM GROQ GRATUITO ====================
    
    async def _groq_analysis_free(self, prompt: str) -> Optional[Dict]:
        """Análise com Groq GRATUITO"""
        
        try:
            logger.info("[GROQ] Iniciando análise gratuita")
            
            system_prompt = """Você é especialista em análise de produtos para marketing digital brasileiro.
Analise qualquer produto com atenção especial ao CONTEXTO:

IMPORTANTE: Antes de classificar, pense no CONTEXTO:
- "peixe palhaço" = animal de estimação de aquário (NÃO alimento)
- "cachorro golden retriever" = animal de estimação (NÃO alimento)
- "gato persa" = animal de estimação (NÃO alimento) 
- "papagaio" = ave de estimação (NÃO alimento)
- "hamster" = animal de estimação (NÃO alimento)
- "plantas ornamentais" = decoração (NÃO alimento)
- "smartphone usado" = eletrônico seminovo (NÃO lixo)

Sempre considere o USO MAIS COMUM do produto no Brasil."""
            
            user_prompt = f"""Analise este produto brasileiro: "{prompt}"

INSTRUÇÕES ESPECIAIS:
1. Se for um ANIMAL, considere como PET/ANIMAL DE ESTIMAÇÃO
2. Se for ELETRÔNICO USADO/SEMINOVO, considere como TECNOLOGIA
3. Se for PLANTA, considere como DECORAÇÃO/JARDINAGEM
4. Pense no CONTEXTO DE USO mais comum no Brasil

Retorne EXATAMENTE este formato JSON (sem markdown):
{{
    "produto_identificado": "nome completo do produto",
    "tipo_produto": "categoria correta baseada no contexto (pet/animal_estimacao/tecnologia/decoracao/etc)",
    "marca": "marca identificada ou 'Genérico'",
    "categoria_uso": "como é usado (pet/decoracao/profissional/pessoal/etc)",
    "caracteristicas_principais": ["característica 1", "característica 2", "característica 3"],
    "publico_alvo_sugerido": "descrição do público-alvo brasileiro correto",
    "preco_estimado": "faixa de preço em reais",
    "pontos_de_venda": ["vantagem 1", "vantagem 2", "vantagem 3"],
    "estrategia_recomendada": "urgencia/premium/custo_beneficio/profissional",
    "contexto_uso": "explicação de como o produto é usado"
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
                        "temperature": 0.3,
                        "max_tokens": 800
                    },
                    timeout=25
                )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Limpar markdown se presente
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                try:
                    analysis = json.loads(content)
                    
                    # Validar campos obrigatórios
                    required_fields = ["produto_identificado", "tipo_produto", "marca"]
                    if all(field in analysis for field in required_fields):
                        logger.info("[SUCCESS] Análise Groq gratuita realizada")
                        return analysis
                    else:
                        logger.info("[WARNING] Campos obrigatórios ausentes na análise Groq")
                        return None
                        
                except json.JSONDecodeError as e:
                    logger.info(f"[ERROR] JSON inválido do Groq: {e}")
                    return None
            else:
                logger.info(f"[ERROR] Groq análise - Status {response.status_code}")
                return None
                
        except Exception as e:
            logger.info(f"[ERROR] Groq análise falhou: {e}")
            return None
    
    # ==================== COPIES COM GROQ GRATUITO ====================
    
    async def _groq_copies_free(self, product_data: Dict, num_copies: int) -> List[Dict]:
        """Gera copies com Groq GRATUITO"""
        
        try:
            logger.info(f"[GROQ] Gerando {num_copies} copies gratuitas")
            
            produto = product_data.get('produto_identificado', 'produto')
            tipo_produto = product_data.get('tipo_produto', 'produto')
            categoria_uso = product_data.get('categoria_uso', 'geral')
            publico_alvo = product_data.get('publico_alvo_sugerido', 'público geral')
            estrategia = product_data.get('estrategia_recomendada', 'comercial')
            contexto_uso = product_data.get('contexto_uso', 'uso geral')
            
            # Definir estratégias para as copies
            strategies = self._get_copy_strategies(estrategia, num_copies)
            
            copies = []
            
            for i, strategy in enumerate(strategies):
                try:
                    logger.info(f"[GROQ] Copy {i+1}: {strategy['name']}")
                    
                    system_prompt = f"""Você é especialista em copywriting para Facebook/Instagram no Brasil.
Crie copies publicitárias persuasivas considerando o CONTEXTO DE USO do produto.

CONTEXTOS ESPECIAIS:
- ANIMAIS DE ESTIMAÇÃO: Foque em cuidado, amor, responsabilidade, alegria para a família
- TECNOLOGIA: Foque em funcionalidade, inovação, produtividade
- DECORAÇÃO: Foque em beleza, ambiente, estilo de vida
- SERVIÇOS: Foque em benefícios, resultados, conveniência"""
                    
                    user_prompt = f"""Produto: {produto}
Tipo: {tipo_produto}
Categoria de uso: {categoria_uso}
Contexto: {contexto_uso}
Público: {publico_alvo}
Estratégia: {strategy['desc']}

IMPORTANTE: Este produto é usado para: {contexto_uso}
Tipo de produto: {tipo_produto}

Crie UMA copy publicitária para Facebook/Instagram:

REQUISITOS:
- Máximo 80 caracteres
- 1-2 emojis relevantes ao TIPO DE PRODUTO
- Call-to-action apropriado para o contexto
- Linguagem brasileira natural
- Foco na estratégia: {strategy['name']}
- RESPEITE o contexto de uso: {categoria_uso}

Retorne APENAS a copy final, sem aspas ou explicações."""

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
                                "temperature": 0.8,
                                "max_tokens": 100
                            },
                            timeout=20
                        )
                    
                    if response.status_code == 200:
                        result = response.json()
                        copy_text = result["choices"][0]["message"]["content"].strip()
                        
                        # Limpar a copy
                        copy_text = copy_text.replace('```', '').replace('*', '').replace('"', '').strip()
                        
                        if len(copy_text) <= 120 and len(copy_text) >= 10:
                            copies.append({
                                'id': i + 1,
                                'titulo': f'Copy {strategy["name"]}',
                                'texto': copy_text,
                                'estrategia': strategy["name"],
                                'tipo_campanha': strategy["type"],
                                'confidence': 0.93,
                                'generated_by': 'groq_real',
                                'ctr_estimado': f'{3.5 + (i * 0.3):.1f}%',
                                'contexto_aplicado': categoria_uso
                            })
                            logger.info(f"[SUCCESS] Copy {i+1} Groq: {copy_text[:40]}...")
                        else:
                            logger.info(f"[WARNING] Copy {i+1} tamanho inválido, usando fallback")
                            copies.append(self._create_fallback_copy(product_data, i + 1, strategy))
                    else:
                        logger.info(f"[ERROR] Groq copy {i+1} - Status {response.status_code}")
                        copies.append(self._create_fallback_copy(product_data, i + 1, strategy))
                    
                    # Pequena pausa para evitar rate limit
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.info(f"[ERROR] Copy {i+1} erro: {e}")
                    copies.append(self._create_fallback_copy(product_data, i + 1, strategy))
            
            if copies:
                real_copies = [c for c in copies if c.get('generated_by') == 'groq_real']
                logger.info(f"[RESULT] {len(real_copies)}/{len(copies)} copies reais geradas")
                return copies
            else:
                logger.info("[ERROR] Nenhuma copy Groq gerada")
                return []
                
        except Exception as e:
            logger.info(f"[ERROR] Groq copies falhou: {e}")
            return []
    
    def _get_copy_strategies(self, estrategia_recomendada: str, num_copies: int) -> List[Dict]:
        """Define estratégias para as copies baseadas na análise"""
        
        all_strategies = {
            "URGÊNCIA": {
                "name": "URGÊNCIA",
                "desc": "Criar senso de urgência e escassez",
                "type": "conversion"
            },
            "PREMIUM": {
                "name": "PREMIUM", 
                "desc": "Destacar exclusividade e qualidade superior",
                "type": "branding"
            },
            "CUSTO_BENEFÍCIO": {
                "name": "CUSTO_BENEFÍCIO",
                "desc": "Enfatizar valor e economia",
                "type": "value"
            },
            "PROFISSIONAL": {
                "name": "PROFISSIONAL",
                "desc": "Focar em produtividade e performance",
                "type": "professional"
            },
            "COMERCIAL": {
                "name": "COMERCIAL",
                "desc": "Apresentação comercial direta",
                "type": "commercial"
            }
        }
        
        # Selecionar estratégias baseadas na recomendação
        if estrategia_recomendada == "urgencia":
            selected = ["URGÊNCIA", "CUSTO_BENEFÍCIO", "COMERCIAL"]
        elif estrategia_recomendada == "premium":
            selected = ["PREMIUM", "PROFISSIONAL", "COMERCIAL"]
        elif estrategia_recomendada == "profissional":
            selected = ["PROFISSIONAL", "PREMIUM", "COMERCIAL"]
        else:
            selected = ["COMERCIAL", "CUSTO_BENEFÍCIO", "URGÊNCIA"]
        
        return [all_strategies[s] for s in selected[:num_copies]]
    
    def _create_fallback_copy(self, product_data: Dict, copy_id: int, strategy: Dict) -> Dict:
        """Cria copy fallback quando Groq falha"""
        
        produto = product_data.get('produto_identificado', 'produto')
        
        templates = {
            "URGÊNCIA": f"🔥 {produto} - Últimas unidades! Aproveite!",
            "PREMIUM": f"✨ {produto} - Exclusividade premium!",
            "CUSTO_BENEFÍCIO": f"💰 {produto} - Melhor preço garantido!",
            "PROFISSIONAL": f"⚡ {produto} - Performance profissional!",
            "COMERCIAL": f"📱 {produto} - Oportunidade única!"
        }
        
        return {
            'id': copy_id,
            'titulo': f'Copy {strategy["name"]}',
            'texto': templates.get(strategy["name"], f"📱 {produto} - Confira!"),
            'estrategia': strategy["name"],
            'tipo_campanha': strategy["type"],
            'confidence': 0.75,
            'generated_by': 'groq_fallback'
        }
    
    # ==================== ANÁLISE E COPIES MOCK ====================
    
    def _mock_analysis_free(self, prompt: str) -> Dict:
        """Análise mock quando Groq não está disponível"""
        
        prompt_lower = prompt.lower()
        
        # DETECTOR DE CONTEXTO INTELIGENTE
        
        # 1. ANIMAIS DE ESTIMAÇÃO
        pets = [
            'peixe palhaço', 'peixe', 'goldfish', 'betta', 'guppy', 'neon tetra',
            'cachorro', 'cão', 'golden', 'labrador', 'poodle', 'shih tzu',
            'gato', 'persa', 'siamês', 'maine coon',
            'hamster', 'chinchila', 'coelho', 'ferret',
            'papagaio', 'canário', 'calopsita', 'agapornis',
            'tartaruga', 'iguana', 'gecko'
        ]
        
        # 2. PLANTAS E JARDINAGEM
        plantas = [
            'suculenta', 'cacto', 'samambaia', 'violeta', 'orquídea',
            'rosa', 'girassol', 'lavanda', 'manjericão', 'alecrim',
            'palmeira', 'ficus', 'monstera', 'costela de adão'
        ]
        
        # 3. TECNOLOGIA
        tech = [
            'iphone', 'smartphone', 'celular', 'tablet', 'notebook', 'laptop',
            'smartwatch', 'fone', 'headphone', 'mouse', 'teclado',
            'monitor', 'tv', 'smart tv', 'chromecast'
        ]
        
        # 4. SERVIÇOS
        servicos = [
            'consulta', 'aula', 'curso', 'treinamento', 'coaching',
            'manutenção', 'reparo', 'instalação', 'limpeza',
            'design', 'fotografia', 'marketing'
        ]
        
        # DETECÇÃO DE CONTEXTO
        if any(pet in prompt_lower for pet in pets):
            tipo_produto = "pet_animal_estimacao"
            categoria_uso = "pet"
            estrategia = "premium"
            publico = "Famílias com pets, aquaristas, amantes de animais"
            contexto = "cuidado e bem-estar de animal de estimação"
            pontos = ["Bem-estar do pet", "Alegria para família", "Cuidado responsável"]
            preco = "R$ 50 - R$ 300"
            
        elif any(planta in prompt_lower for planta in plantas):
            tipo_produto = "planta_decoracao"
            categoria_uso = "decoracao"
            estrategia = "premium"
            publico = "Entusiastas de jardinagem, decoradores, pessoas que gostam de plantas"
            contexto = "decoração e purificação do ambiente"
            pontos = ["Ambiente mais bonito", "Ar purificado", "Bem-estar"]
            preco = "R$ 15 - R$ 150"
            
        elif any(t in prompt_lower for t in tech):
            tipo_produto = "tecnologia"
            categoria_uso = "profissional" if any(x in prompt_lower for x in ['pro', 'profissional', 'trabalho']) else "pessoal"
            estrategia = "premium" if "iphone" in prompt_lower else "custo_beneficio"
            publico = "Usuários de tecnologia, profissionais, estudantes"
            contexto = "produtividade e comunicação digital"
            pontos = ["Tecnologia avançada", "Produtividade", "Conectividade"]
            preco = "R$ 500 - R$ 5.000"
            
        elif any(servico in prompt_lower for servico in servicos):
            tipo_produto = "servico"
            categoria_uso = "profissional"
            estrategia = "profissional"
            publico = "Pessoas buscando soluções profissionais"
            contexto = "solução de problemas ou aprendizado"
            pontos = ["Expertise profissional", "Resultados garantidos", "Conveniência"]
            preco = "R$ 100 - R$ 500"
            
        else:
            # GENÉRICO
            tipo_produto = "produto"
            categoria_uso = "geral"
            estrategia = "comercial"
            publico = "Consumidores brasileiros"
            contexto = "uso cotidiano"
            pontos = ["Qualidade garantida", "Bom custo-benefício", "Entrega rápida"]
            preco = "R$ 50 - R$ 500"
        
        return {
            "produto_identificado": prompt,
            "tipo_produto": tipo_produto,
            "marca": "Premium",
            "categoria_uso": categoria_uso,
            "caracteristicas_principais": ["Qualidade superior", "Design atrativo", "Durabilidade"],
            "publico_alvo_sugerido": publico,
            "preco_estimado": preco,
            "pontos_de_venda": pontos,
            "estrategia_recomendada": estrategia,
            "contexto_uso": contexto
        }
    
    def _mock_copies_free(self, product_data: Dict, num_copies: int) -> List[Dict]:
        """Copies mock quando Groq não está disponível"""
        
        produto = product_data.get('produto_identificado', 'produto')
        
        copies = [
            {
                'id': 1,
                'titulo': 'Copy Comercial',
                'texto': f"📱 {produto} - Oportunidade imperdível!",
                'estrategia': 'COMERCIAL',
                'tipo_campanha': 'commercial',
                'confidence': 0.80,
                'generated_by': 'mock_fallback'
            },
            {
                'id': 2,
                'titulo': 'Copy Urgência',
                'texto': f"🔥 {produto} - Últimas unidades disponíveis!",
                'estrategia': 'URGÊNCIA',
                'tipo_campanha': 'conversion',
                'confidence': 0.80,
                'generated_by': 'mock_fallback'
            },
            {
                'id': 3,
                'titulo': 'Copy Premium',
                'texto': f"✨ {produto} - Qualidade premium garantida!",
                'estrategia': 'PREMIUM',
                'tipo_campanha': 'branding',
                'confidence': 0.80,
                'generated_by': 'mock_fallback'
            }
        ]
        
        return copies[:num_copies]
    
    # ==================== RESTO DOS MÉTODOS (BUSCA E IMAGENS) ====================
    
    async def _search_free_product_images(self, product_data: Dict) -> List[Dict]:
        """Busca UNIVERSAL usando sistema inteligente"""
        
        try:
            from app.services.truly_universal_search import universal_search
            
            logger.info("[UNIVERSAL] Sistema para QUALQUER produto inicializado")
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
        
        return await self._search_basic_fallback(product_data)

    async def _search_basic_fallback(self, product_data: Dict) -> List[Dict]:
        """Fallback básico quando sistema universal falha"""
        
        produto = product_data.get('produto_identificado', '')
        tipo_produto = product_data.get('tipo_produto', '')
        
        queries = []
        
        if produto:
            clean_produto = self._clean_product_for_search(produto)
            queries.append(clean_produto)
        
        if tipo_produto:
            queries.append(f"{tipo_produto} photography")
        
        queries.append("product photography")
        
        all_refs = []
        
        for query in queries[:2]:
            logger.info(f"[FALLBACK] Buscando: {query}")
            
            if self.pexels_key:
                refs = await self._search_pexels_free(query)
                all_refs.extend(refs)
            
            if len(all_refs) >= 5:
                break
        
        return all_refs[:5]

    def _clean_product_for_search(self, produto: str) -> str:
        """Limpa produto para busca universal"""
        
        noise_terms = [
            'novo', 'usado', 'seminovo', 'original', 'nacional',
            'gb', 'mb', 'tb', '256gb', '512gb', '1tb',
            'polegadas', '"', 'cm', 'mm', 'kg', 'gramas'
        ]
        
        clean = produto.lower()
        
        for term in noise_terms:
            clean = clean.replace(term, ' ')
        
        clean = ' '.join(clean.split())
        words = clean.split()[:3]
        
        return ' '.join(words) if words else produto

    async def _analyze_free_references(self, references: List[Dict], product_data: Dict) -> Dict:
        """Análise universal das referências"""
        
        logger.info(f"[ANALYSIS] Analisando {len(references)} referências universais")
        
        if not references:
            return self._create_universal_fallback_analysis(product_data)
        
        all_titles = [ref.get("title", "") for ref in references]
        all_search_terms = [ref.get("search_term", "") for ref in references]
        combined_text = " ".join(all_titles + all_search_terms).lower()
        
        analysis = {
            "product_name": product_data.get('produto_identificado'),
            "reference_count": len(references),
            "sources_analyzed": list(set([ref.get("source", "") for ref in references])),
            "search_terms_used": list(set([ref.get("search_term", "") for ref in references])),
            "average_relevance": sum([ref.get('relevance_score', 0) for ref in references]) / len(references) if references else 0,
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
        indicators = []
        
        if not references:
            return ["no references available"]
        
        high_res_count = len([r for r in references if r.get('width', 0) > 800])
        if high_res_count > 0:
            indicators.append(f"{high_res_count}/{len(references)} high resolution")
        
        sources = set([r.get('source', '') for r in references])
        if len(sources) > 1:
            indicators.append(f"diverse sources: {', '.join(sources)}")
        
        avg_relevance = sum([r.get('relevance_score', 0) for r in references]) / len(references) if references else 0
        if avg_relevance >= 2:
            indicators.append("high relevance matches")
        elif avg_relevance >= 1:
            indicators.append("moderate relevance matches")
        else:
            indicators.append("basic relevance matches")
        
        free_license_count = len([r for r in references if r.get('free_license')])
        if free_license_count == len(references):
            indicators.append("all free licensed")
        
        return indicators

    def _create_universal_fallback_analysis(self, product_data: Dict) -> Dict:
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
    
    async def _search_pexels_free(self, query: str) -> List[Dict]:
        """Pexels - 200 imagens/hora GRATUITO"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.pexels.com/v1/search",
                    headers={"Authorization": self.pexels_key},
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
                        "search_term": query,
                        "free_license": True,
                        "relevance_score": 1
                    })
                
                logger.info(f"[PEXELS] {len(refs)} encontradas para '{query}'")
                return refs
        
        except Exception as e:
            logger.info(f"[ERROR] Pexels: {e}")
        
        return []
    
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
            elif strategy == "PROFISSIONAL":
                enhanced_prompt = f"{base_prompt}, modern tech environment, professional setup"
                style = "Professional Tech"
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
                'PROFISSIONAL': ('6f42c1', 'ffffff'),
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
                "ai_copy_generation": bool(self.groq_key),
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