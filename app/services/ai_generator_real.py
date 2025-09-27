# app/services/ai_generator_real.py
"""
AI Generator Unificado v2.2
- A mesma IA (Groq) gera análise, copies E prompts de imagem
- Adaptável para qualquer produto (celulares, eletrônicos, etc)
- Prompts de imagem baseados na estratégia da campanha
"""

import os
import json
import httpx
import asyncio
from dotenv import load_dotenv
from app.utils.logger import logger

load_dotenv()

class AIGeneratorReal:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.strategy = "groq" if self.groq_key else "mock"
        
        # MODELOS GROQ ATUALIZADOS
        self.primary_model = "llama-3.3-70b-versatile"
        
        # IMPORTAR IMAGE GENERATOR
        try:
            from app.services.image_generator_intelligent import image_generator_intelligent
            self.image_gen = image_generator_intelligent
            logger.info("[CONFIG] Image Generator Inteligente carregado")
        except ImportError as e:
            logger.info(f"[ERROR] Erro ao carregar Image Generator: {e}")
            self.image_gen = None
        
        logger.info(f"[CONFIG] AI Generator Unificado - Modo: {self.strategy.upper()}")
        if self.strategy == "groq":
            logger.info(f"[GROQ] Modelo: {self.primary_model}")
    
    def is_available(self):
        image_status = self.image_gen.get_status() if self.image_gen else {"ready": False}
        
        return {
            "mode": self.strategy,
            "groq": bool(self.groq_key),
            "model": self.primary_model if self.groq_key else "mock",
            "images": image_status,
            "unified_ai": True,  # IA gera tanto copies quanto prompts de imagem
            "real_images_available": self.image_gen.is_real_generation_available() if self.image_gen else False
        }
    
    async def analyze_with_openai(self, prompt: str):
        """Análise expandida para qualquer produto eletrônico"""
        if self.strategy == "groq" and self.groq_key:
            result = await self._groq_analysis_expanded(prompt)
            if result and result.get("produto_identificado"):
                logger.info("[OK] Análise Groq expandida realizada com sucesso")
                return result
            else:
                logger.info("[FALLBACK] Groq analysis falhou, usando mock")
        
        return self._mock_analysis_expanded(prompt)
    
    async def generate_copies_with_openai(self, product_data: dict, num_copies: int = 3):
        """Geração de copies com estratégias definidas"""
        if self.strategy == "groq" and self.groq_key:
            copies = await self._groq_copies_with_strategies(product_data, num_copies)
            if copies and len(copies) > 0:
                groq_copies = [c for c in copies if c.get("generated_by") == "groq_real"]
                if groq_copies:
                    logger.info(f"[OK] {len(groq_copies)} copies Groq com estratégias geradas")
                    return copies
        
        logger.info("[FALLBACK] Usando copies mock")
        return self._mock_copies_with_strategies(product_data, num_copies)
    
    async def generate_images_with_replicate(self, product_data: dict, copies: list, num_images: int = 3):
        """
        NOVO: Gera prompts de imagem baseados nas estratégias dos copies
        """
        if not self.image_gen:
            logger.info("[ERROR] Image Generator não disponível, usando mock")
            return self._mock_images(product_data, num_images)
        
        try:
            logger.info(f"[IMAGE] Iniciando geração inteligente de {num_images} imagens")
            
            # 1. Gerar prompts de imagem com IA baseados nas estratégias dos copies
            image_prompts = await self._generate_image_prompts_with_ai(product_data, copies, num_images)
            
            # 2. Usar o Image Generator com os prompts inteligentes
            images = await self.image_gen.generate_with_ai_prompts(product_data, image_prompts)
            
            # Estatísticas
            real_images = [img for img in images if img['generated_by'] in ['stability_ai', 'huggingface']]
            mock_images = [img for img in images if img['generated_by'] in ['intelligent_mock']]
            
            logger.info(f"[RESULT] {len(real_images)} imagens reais, {len(mock_images)} mocks")
            
            return images
            
        except Exception as e:
            logger.info(f"[ERROR] Erro na geração inteligente: {e}")
            return self._mock_images(product_data, num_images)
    
    # ==================== NOVOS MÉTODOS EXPANDIDOS ====================
    
    async def _groq_analysis_expanded(self, prompt: str):
        """Análise expandida para qualquer produto eletrônico"""
        try:
            logger.info(f"[GROQ] Analisando produto expandido com {self.primary_model}")
            
            system_prompt = """Você é um especialista em análise de produtos eletrônicos para marketing digital no Brasil.
Analise qualquer tipo de produto eletrônico: smartphones, notebooks, tablets, fones, smart TVs, videogames, 
smartwatches, caixas de som, carregadores, acessórios, etc.

Retorne informações estruturadas e precisas em JSON."""

            user_prompt = f"""Analise este produto eletrônico brasileiro: "{prompt}"

Identifique automaticamente:
- Tipo de produto (smartphone, notebook, tablet, TV, etc)
- Marca e modelo específico
- Categoria de uso (profissional, gamer, casual, premium)
- Condição (novo, seminovo, usado)
- Faixa de preço real do mercado brasileiro

Retorne EXATAMENTE este formato JSON (sem markdown):
{{
    "produto_identificado": "nome completo e específico do produto",
    "tipo_produto": "smartphone/notebook/tablet/tv/fone/smartwatch/acessorio/etc",
    "marca": "marca identificada",
    "modelo_especifico": "modelo exato se identificado",
    "categoria": "novo/seminovo/usado",
    "categoria_uso": "profissional/gamer/casual/premium/entrada",
    "caracteristicas_principais": ["característica técnica 1", "característica técnica 2", "característica técnica 3"],
    "publico_alvo_sugerido": "descrição detalhada do público-alvo brasileiro específico",
    "preco_estimado": "faixa de preço realista em reais baseada no mercado atual",
    "pontos_de_venda": ["vantagem competitiva 1", "vantagem competitiva 2", "vantagem competitiva 3"],
    "estrategia_recomendada": "urgencia/premium/custo_beneficio/profissional/gamer"
}}"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.primary_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    },
                    timeout=30
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
                    # Validar campos obrigatórios expandidos
                    required_fields = ["produto_identificado", "tipo_produto", "marca", "categoria"]
                    if all(field in analysis for field in required_fields):
                        return analysis
                    else:
                        logger.info("[WARNING] JSON válido mas campos obrigatórios faltando")
                        return None
                        
                except json.JSONDecodeError as e:
                    logger.info(f"[WARNING] JSON inválido do Groq: {e}")
                    return None
            else:
                logger.info(f"[ERROR] Groq API erro: {response.status_code}")
                return None
                
        except Exception as e:
            logger.info(f"[ERROR] Groq analysis expandida falhou: {e}")
            return None
    
    async def _groq_copies_with_strategies(self, product_data: dict, num_copies: int):
        """Gera copies com estratégias bem definidas"""
        copies = []
        
        # Estratégias baseadas no produto e público
        estrategia_recomendada = product_data.get('estrategia_recomendada', 'custo_beneficio')
        tipo_produto = product_data.get('tipo_produto', 'eletronico')
        categoria_uso = product_data.get('categoria_uso', 'casual')
        
        # Definir estratégias baseadas na análise
        strategies = self._get_strategies_for_product(estrategia_recomendada, tipo_produto, categoria_uso, num_copies)
        
        for i, strategy in enumerate(strategies):
            try:
                logger.info(f"[GROQ] Gerando copy {i+1}: {strategy['name']}")
                
                copy_prompt = f"""Crie uma copy publicitária brasileira para Facebook/Instagram sobre: {product_data.get('produto_identificado')}

CONTEXTO DO PRODUTO:
- Tipo: {product_data.get('tipo_produto')}
- Marca: {product_data.get('marca')}
- Categoria: {product_data.get('categoria_uso')} / {product_data.get('categoria')}
- Público-alvo: {product_data.get('publico_alvo_sugerido')}
- Preço estimado: {product_data.get('preco_estimado')}

ESTRATÉGIA: {strategy['desc']}
OBJETIVO: {strategy['objective']}

REQUISITOS OBRIGATÓRIOS:
- Máximo 85 caracteres total
- Incluir 1-2 emojis brasileiros relevantes ao produto
- Call-to-action claro e específico
- Linguagem brasileira natural e persuasiva
- Foco total na estratégia {strategy['name']}
- Adaptar ao tipo de produto ({tipo_produto})

Retorne APENAS a copy final, sem aspas, explicações ou markdown."""

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.groq_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.primary_model,
                            "messages": [
                                {
                                    "role": "system", 
                                    "content": f"Você é especialista em copywriting para produtos eletrônicos no Brasil. Crie copies específicas para {tipo_produto} com foco em {categoria_uso}."
                                },
                                {"role": "user", "content": copy_prompt}
                            ],
                            "temperature": 0.8,
                            "max_tokens": 150
                        },
                        timeout=25
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    copy_text = result["choices"][0]["message"]["content"].strip()
                    
                    copy_text = copy_text.replace('```', '').replace('*', '').replace('"', '').strip()
                    
                    if len(copy_text) <= 120:
                        copies.append({
                            'id': i + 1,
                            'titulo': f'Copy {strategy["name"]}',
                            'texto': copy_text,
                            'estrategia': strategy["name"],
                            'tipo_campanha': strategy["campaign_type"],
                            'confidence': 0.92,
                            'generated_by': 'groq_real',
                            'ctr_estimado': f'{3.2 + (i * 0.4):.1f}%'
                        })
                        logger.info(f"[OK] Copy {i+1} gerada: {copy_text[:40]}...")
                    else:
                        logger.info(f"[WARNING] Copy {i+1} muito longa, usando fallback")
                        copies.append(self._create_mock_copy_strategic(product_data, i + 1, strategy))
                else:
                    logger.info(f"[ERROR] Copy {i+1} falhou: {response.status_code}")
                    copies.append(self._create_mock_copy_strategic(product_data, i + 1, strategy))
                
            except Exception as e:
                logger.info(f"[ERROR] Copy {i+1} erro: {e}")
                copies.append(self._create_mock_copy_strategic(product_data, i + 1, strategy))
                
        return copies
    
    async def _generate_image_prompts_with_ai(self, product_data: dict, copies: list, num_images: int):
        """
        NOVIDADE: IA gera prompts de imagem baseados nas estratégias dos copies
        """
        if not self.groq_key:
            return self._generate_basic_image_prompts(product_data, copies, num_images)
        
        try:
            logger.info(f"[GROQ] Gerando {num_images} prompts de imagem com IA")
            
            # Extrair estratégias dos copies
            strategies = [copy.get('estrategia', 'PADRÃO') for copy in copies[:num_images]]
            campaign_types = [copy.get('tipo_campanha', 'standard') for copy in copies[:num_images]]
            
            system_prompt = """Você é um especialista em fotografia comercial e marketing visual para produtos eletrônicos.
Crie prompts detalhados para geração de imagens que complementem perfeitamente as estratégias de copy.

Foque em: iluminação profissional, composição comercial, apelo visual específico para cada estratégia."""
            
            user_prompt = f"""Crie prompts de imagem para: {product_data.get('produto_identificado')}

CONTEXTO:
- Produto: {product_data.get('tipo_produto')} {product_data.get('marca')}
- Categoria uso: {product_data.get('categoria_uso')}
- Estratégias das copies: {strategies}
- Tipos de campanha: {campaign_types}

CRIE {num_images} PROMPTS DE IMAGEM diferentes, cada um alinhado com uma estratégia:

Para cada prompt, considere:
- URGÊNCIA: ambiente dinâmico, cores vibrantes, movimento
- PREMIUM: fundo escuro elegante, iluminação sofisticada, materiais luxuosos
- CUSTO-BENEFÍCIO: ambiente acessível, iluminação natural, setup prático
- PROFISSIONAL: escritório moderno, setup corporativo, ambiente clean
- GAMER: RGB, setup gaming, cores neon, ambiente tech

Retorne EXATAMENTE este formato JSON:
{{
    "image_prompts": [
        {{
            "id": 1,
            "style": "Nome do estilo baseado na estratégia",
            "strategy": "estratégia correspondente",
            "prompt": "prompt detalhado em inglês para Stability AI",
            "description": "descrição em português do que a imagem deve transmitir"
        }}
    ]
}}

SEM MARKDOWN, APENAS JSON PURO."""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.primary_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1500
                    },
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Limpar markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                try:
                    prompts_data = json.loads(content)
                    if "image_prompts" in prompts_data:
                        logger.info(f"[SUCCESS] {len(prompts_data['image_prompts'])} prompts de imagem gerados por IA")
                        return prompts_data["image_prompts"]
                    else:
                        logger.info("[WARNING] Formato inesperado na resposta")
                        return self._generate_basic_image_prompts(product_data, copies, num_images)
                        
                except json.JSONDecodeError as e:
                    logger.info(f"[WARNING] JSON inválido nos prompts: {e}")
                    return self._generate_basic_image_prompts(product_data, copies, num_images)
            else:
                logger.info(f"[ERROR] Erro na geração de prompts: {response.status_code}")
                return self._generate_basic_image_prompts(product_data, copies, num_images)
                
        except Exception as e:
            logger.info(f"[ERROR] Erro na geração de prompts com IA: {e}")
            return self._generate_basic_image_prompts(product_data, copies, num_images)
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _get_strategies_for_product(self, estrategia_recomendada: str, tipo_produto: str, categoria_uso: str, num_copies: int):
        """Define estratégias baseadas no tipo de produto"""
        
        # Estratégias base
        all_strategies = {
            "URGÊNCIA": {
                "name": "URGÊNCIA",
                "desc": "Criar senso de urgência e escassez",
                "objective": "Conversão rápida",
                "campaign_type": "conversion"
            },
            "PREMIUM": {
                "name": "PREMIUM", 
                "desc": "Destacar exclusividade e qualidade superior",
                "objective": "Posicionamento alto",
                "campaign_type": "branding"
            },
            "CUSTO_BENEFÍCIO": {
                "name": "CUSTO_BENEFÍCIO",
                "desc": "Enfatizar valor e economia",
                "objective": "Acessibilidade",
                "campaign_type": "value"
            },
            "PROFISSIONAL": {
                "name": "PROFISSIONAL",
                "desc": "Focar em produtividade e performance",
                "objective": "B2B e profissionais",
                "campaign_type": "professional"
            },
            "GAMER": {
                "name": "GAMER",
                "desc": "Destacar performance para games",
                "objective": "Público gamer",
                "campaign_type": "gaming"
            },
            "LIFESTYLE": {
                "name": "LIFESTYLE",
                "desc": "Mostrar como melhora o dia a dia",
                "objective": "Aspiracional",
                "campaign_type": "lifestyle"
            }
        }
        
        # Selecionar estratégias baseadas no produto
        if categoria_uso == "gamer" or "gamer" in tipo_produto:
            selected = ["GAMER", "PREMIUM", "URGÊNCIA"]
        elif categoria_uso == "profissional" or tipo_produto in ["notebook", "tablet"]:
            selected = ["PROFISSIONAL", "PREMIUM", "CUSTO_BENEFÍCIO"]
        elif estrategia_recomendada == "premium":
            selected = ["PREMIUM", "LIFESTYLE", "PROFISSIONAL"]
        elif estrategia_recomendada == "urgencia":
            selected = ["URGÊNCIA", "CUSTO_BENEFÍCIO", "LIFESTYLE"]
        else:
            selected = ["CUSTO_BENEFÍCIO", "URGÊNCIA", "PREMIUM"]
        
        return [all_strategies[s] for s in selected[:num_copies]]
    
    def _generate_basic_image_prompts(self, product_data: dict, copies: list, num_images: int):
        """Fallback para prompts básicos quando IA falha"""
        
        tipo_produto = product_data.get('tipo_produto', 'eletronico')
        marca = product_data.get('marca', 'Premium')
        categoria_uso = product_data.get('categoria_uso', 'casual')
        
        base_prompts = []
        
        for i in range(num_images):
            strategy = copies[i].get('estrategia', 'PADRÃO') if i < len(copies) else 'PADRÃO'
            
            if strategy == "URGÊNCIA":
                prompt = f"dynamic commercial photography of {marca} {tipo_produto}, vibrant red and orange lighting, energetic composition, sale environment, urgent atmosphere, professional quality"
                style = "Dinâmico Urgente"
            elif strategy == "PREMIUM":
                prompt = f"luxury product photography of {marca} {tipo_produto}, dark elegant background, sophisticated lighting, premium materials, commercial quality, high-end aesthetic"
                style = "Premium Luxo"
            elif strategy == "GAMER":
                prompt = f"gaming setup photography with {marca} {tipo_produto}, RGB lighting, neon colors, modern gaming environment, tech aesthetic, professional quality"
                style = "Gaming RGB"
            elif strategy == "PROFISSIONAL":
                prompt = f"professional office photography of {marca} {tipo_produto}, clean modern workspace, natural lighting, corporate environment, productivity focus, commercial quality"
                style = "Profissional Clean"
            else:
                prompt = f"clean product photography of {marca} {tipo_produto}, white background, studio lighting, commercial quality, minimalist composition"
                style = "Clean Padrão"
            
            base_prompts.append({
                "id": i + 1,
                "style": style,
                "strategy": strategy,
                "prompt": prompt,
                "description": f"Imagem {style.lower()} para {tipo_produto}"
            })
        
        return base_prompts
    
    def _create_mock_copy_strategic(self, product_data: dict, copy_id: int, strategy: dict):
        """Cria copy mock baseada na estratégia"""
        produto = product_data.get('produto_identificado', 'produto')
        tipo_produto = product_data.get('tipo_produto', 'produto')
        
        templates = {
            "URGÊNCIA": f"🔥 {produto} - Últimas unidades! Aproveite!",
            "PREMIUM": f"✨ {produto} - Exclusividade e qualidade premium!",
            "CUSTO_BENEFÍCIO": f"💰 {produto} - Melhor preço do mercado!",
            "PROFISSIONAL": f"⚡ {produto} - Performance profissional!",
            "GAMER": f"🎮 {produto} - Power gaming absoluto!",
            "LIFESTYLE": f"📱 {produto} - Transforme seu dia a dia!"
        }
        
        return {
            'id': copy_id,
            'titulo': f'Copy {strategy["name"]}',
            'texto': templates.get(strategy["name"], f"📱 {produto} - Oportunidade única!"),
            'estrategia': strategy["name"],
            'tipo_campanha': strategy["campaign_type"],
            'confidence': 0.78,
            'generated_by': 'strategic_mock'
        }
    
    # ==================== MÉTODOS MOCK EXPANDIDOS ====================
    
    def _mock_analysis_expanded(self, prompt: str):
        """Mock analysis expandida para qualquer produto eletrônico"""
        prompt_lower = prompt.lower()
        
        # Detectar tipo de produto
        if any(term in prompt_lower for term in ['iphone', 'galaxy', 'xiaomi', 'motorola', 'smartphone', 'celular']):
            tipo_produto = "smartphone"
        elif any(term in prompt_lower for term in ['notebook', 'laptop', 'macbook']):
            tipo_produto = "notebook"
        elif any(term in prompt_lower for term in ['tablet', 'ipad']):
            tipo_produto = "tablet"
        elif any(term in prompt_lower for term in ['tv', 'smart tv', 'televisão']):
            tipo_produto = "smart_tv"
        elif any(term in prompt_lower for term in ['fone', 'headphone', 'earphone', 'airpods']):
            tipo_produto = "fone"
        elif any(term in prompt_lower for term in ['smartwatch', 'watch', 'relógio']):
            tipo_produto = "smartwatch"
        elif any(term in prompt_lower for term in ['caixa de som', 'speaker', 'jbl']):
            tipo_produto = "caixa_som"
        else:
            tipo_produto = "eletronico"
        
        # Detectar marca
        if any(term in prompt_lower for term in ['iphone', 'apple', 'macbook', 'ipad']):
            marca = "Apple"
            preco_base = 5000 if tipo_produto == "smartphone" else 7000
        elif any(term in prompt_lower for term in ['samsung', 'galaxy']):
            marca = "Samsung"
            preco_base = 3500 if tipo_produto == "smartphone" else 4000
        elif any(term in prompt_lower for term in ['xiaomi', 'redmi']):
            marca = "Xiaomi"
            preco_base = 2000
        elif any(term in prompt_lower for term in ['motorola', 'moto']):
            marca = "Motorola"
            preco_base = 1500
        else:
            marca = "Premium"
            preco_base = 2500
        
        # Detectar categoria de uso
        if any(term in prompt_lower for term in ['gamer', 'gaming', 'game']):
            categoria_uso = "gamer"
            estrategia = "gamer"
        elif any(term in prompt_lower for term in ['pro', 'profissional', 'trabalho']):
            categoria_uso = "profissional" 
            estrategia = "profissional"
        elif marca in ["Apple", "Samsung"] and "pro" in prompt_lower:
            categoria_uso = "premium"
            estrategia = "premium"
        else:
            categoria_uso = "casual"
            estrategia = "custo_beneficio"
        
        # Detectar condição
        if "seminovo" in prompt_lower:
            categoria = "seminovo"
            fator_preco = 0.75
        elif "usado" in prompt_lower:
            categoria = "usado"
            fator_preco = 0.60
        else:
            categoria = "novo"
            fator_preco = 1.0
        
        preco_final = int(preco_base * fator_preco)
        
        return {
            "produto_identificado": prompt,
            "tipo_produto": tipo_produto,
            "marca": marca,
            "modelo_especifico": f"{marca} {tipo_produto.title()}",
            "categoria": categoria,
            "categoria_uso": categoria_uso,
            "caracteristicas_principais": self._get_features_for_product(tipo_produto, marca),
            "publico_alvo_sugerido": self._get_target_audience(tipo_produto, categoria_uso, marca),
            "preco_estimado": f"R$ {preco_final - 500:,} - R$ {preco_final + 500:,}".replace(",", "."),
            "pontos_de_venda": self._get_selling_points(tipo_produto, categoria_uso),
            "estrategia_recomendada": estrategia
        }
    
    def _get_features_for_product(self, tipo_produto: str, marca: str):
        """Features específicas por tipo de produto"""
        features_map = {
            "smartphone": ["Câmera avançada", "Performance rápida", "Bateria duradoura"],
            "notebook": ["Processador potente", "Tela de qualidade", "Portabilidade"],
            "tablet": ["Tela touchscreen", "Portabilidade", "Multimídia"],
            "smart_tv": ["4K Ultra HD", "Smart OS", "Conectividade"],
            "fone": ["Qualidade sonora", "Conforto", "Cancelamento ruído"],
            "smartwatch": ["Monitor saúde", "GPS", "Resistência água"],
            "caixa_som": ["Som potente", "Bluetooth", "Portabilidade"]
        }
        return features_map.get(tipo_produto, ["Tecnologia avançada", "Design moderno", "Qualidade premium"])
    
    def _get_target_audience(self, tipo_produto: str, categoria_uso: str, marca: str):
        """Público-alvo específico por produto e categoria"""
        if categoria_uso == "gamer":
            return "Gamers, entusiastas de tecnologia, jovens 18-35 anos"
        elif categoria_uso == "profissional":
            return "Profissionais, empresários, trabalho remoto, 25-50 anos"
        elif marca == "Apple":
            return "Usuários Apple, criativos, early adopters, classe A-B"
        elif tipo_produto == "smartphone":
            return "Usuários de smartphone, conectados, 20-45 anos"
        else:
            return "Consumidores de eletrônicos, tech enthusiasts, 25-45 anos"
    
    def _get_selling_points(self, tipo_produto: str, categoria_uso: str):
        """Pontos de venda específicos por produto"""
        points_map = {
            "smartphone": ["Conectividade 5G", "Câmeras profissionais", "Bateria inteligente"],
            "notebook": ["Produtividade máxima", "Design portátil", "Performance superior"],
            "tablet": ["Versatilidade total", "Tela premium", "Mobilidade"],
            "smart_tv": ["Experiência 4K", "Apps integrados", "Som surround"],
            "fone": ["Som cristalino", "Conforto prolongado", "Tecnologia bluetooth"],
            "smartwatch": ["Saúde 24h", "Estilo moderno", "Autonomia"],
            "caixa_som": ["Som potente", "Design compacto", "Bateria longa"]
        }
        
        base_points = points_map.get(tipo_produto, ["Tecnologia avançada", "Qualidade garantida", "Melhor preço"])
        
        if categoria_uso == "gamer":
            return ["Performance gaming", "RGB personalizado", "Zero lag"]
        elif categoria_uso == "profissional":
            return ["Produtividade", "Confiabilidade", "Suporte técnico"]
        else:
            return base_points
    
    def _mock_copies_with_strategies(self, product_data: dict, num_copies: int):
        """Mock copies com estratégias específicas"""
        produto = product_data.get('produto_identificado', 'produto')
        tipo_produto = product_data.get('tipo_produto', 'eletronico')
        marca = product_data.get('marca', 'Premium')
        categoria_uso = product_data.get('categoria_uso', 'casual')
        
        strategies = self._get_strategies_for_product(
            product_data.get('estrategia_recomendada', 'custo_beneficio'), 
            tipo_produto, 
            categoria_uso, 
            num_copies
        )
        
        copies = []
        for i, strategy in enumerate(strategies):
            copy_text = self._create_mock_copy_strategic(product_data, i + 1, strategy)
            copies.append({
                'id': i + 1,
                'titulo': f'Copy {strategy["name"]}',
                'texto': copy_text['texto'],
                'estrategia': strategy["name"],
                'tipo_campanha': strategy["campaign_type"],
                'confidence': 0.85,
                'generated_by': 'strategic_mock',
                'ctr_estimado': f'{3.2 + (i * 0.4):.1f}%'
            })
        
        return copies
    
    def _mock_images(self, product_data: dict, num_images: int):
        """Mock images com base no produto"""
        marca = product_data.get('marca', 'Produto')
        tipo_produto = product_data.get('tipo_produto', 'eletronico')
        categoria_uso = product_data.get('categoria_uso', 'casual')
        
        # Cores por marca
        cores = {
            'Apple': ('f5f5f7', '1d1d1f'),
            'Samsung': ('ffffff', '1428a0'),
            'Xiaomi': ('ffffff', 'ff6900'),
            'Motorola': ('ffffff', '0066cc'),
            'Premium': ('f8f9fa', '2c3e50')
        }
        
        cor_bg, cor_texto = cores.get(marca, cores['Premium'])
        
        # Estilos baseados no tipo de produto
        if categoria_uso == "gamer":
            styles = ['Gaming+RGB', 'Neon+Setup', 'Pro+Gamer']
        elif categoria_uso == "profissional":
            styles = ['Office+Pro', 'Business+Clean', 'Corporate']
        else:
            styles = ['Studio+Pro', 'Lifestyle', 'Premium']
        
        return [
            {
                'id': i + 1,
                'url': f"https://via.placeholder.com/1024x1024/{cor_bg}/{cor_texto}?text={marca}+{styles[i] if i < len(styles) else styles[0]}",
                'style': styles[i] if i < len(styles) else styles[0],
                'description': f"Mock {styles[i] if i < len(styles) else styles[0]} para {tipo_produto}",
                'generated_by': 'intelligent_mock',
                'confidence': 0.75,
                'strategy': f"MOCK_{i+1}",
                'brand_optimized': True
            } for i in range(min(num_images, 3))
        ]

# Instância global
logger.info("[CONFIG] Criando AI Generator Unificado...")
ai_generator_real = AIGeneratorReal()
logger.info("[OK] AI Generator Unificado pronto - IA gera copies E prompts de imagem")