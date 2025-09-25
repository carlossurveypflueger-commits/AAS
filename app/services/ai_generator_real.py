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
        
        # MODELOS ATUALIZADOS - Dezembro 2024
        self.available_models = [
            "llama-3.3-70b-versatile",  # Modelo principal
            "llama-3.1-8b-instant",     # Mais rápido
            "gemma2-9b-it",       # Alternativa
            ]
        
        self.primary_model = "llama-3.3-70b-versatile"  # MELHOR modelo disponível
        
        logger.info(f"[CONFIG] AI Generator iniciado - Modo: {self.strategy.upper()}")
        if self.strategy == "groq":
            logger.info(f"[GROQ] Usando modelo: {self.primary_model}")
    
    def is_available(self):
        return {
            "mode": self.strategy, 
            "groq": bool(self.groq_key),
            "model": self.primary_model if self.groq_key else "mock"
        }
    
    async def analyze_with_openai(self, prompt: str):
        if self.strategy == "groq" and self.groq_key:
            result = await self._groq_analysis(prompt)
            if result and result.get("produto_identificado"):
                logger.info("[OK] Análise Groq realizada com sucesso")
                return result
            else:
                logger.info("[FALLBACK] Groq analysis falhou, usando mock")
        
        return self._mock_analysis(prompt)
    
    async def generate_copies_with_openai(self, product_data: dict, num_copies: int = 3):
        if self.strategy == "groq" and self.groq_key:
            copies = await self._groq_copies(product_data, num_copies)
            if copies and len(copies) > 0:
                # Verificar se pelo menos uma copy foi gerada pelo Groq
                groq_copies = [c for c in copies if c.get("generated_by") == "groq_real"]
                if groq_copies:
                    logger.info(f"[OK] {len(groq_copies)} copies Groq geradas com sucesso")
                    return copies
        
        logger.info("[FALLBACK] Usando copies mock")
        return self._mock_copies(product_data, num_copies)
    
    async def generate_images_with_replicate(self, product_data: dict, num_images: int = 3):
        return self._mock_images(product_data, num_images)
    
    async def _groq_analysis(self, prompt: str):
        """Análise usando Groq com modelo atualizado"""
        try:
            logger.info(f"[GROQ] Analisando com {self.primary_model}")
            
            system_prompt = """Você é um especialista em análise de produtos para marketing digital no Brasil.
Analise produtos de tecnologia e retorne informações estruturadas em JSON válido."""

            user_prompt = f"""Analise este produto brasileiro: "{prompt}"

Retorne EXATAMENTE este formato JSON (sem markdown):
{{
    "produto_identificado": "nome completo e específico do produto",
    "marca": "marca identificada",
    "categoria": "novo/seminovo/usado",
    "caracteristicas_principais": ["característica técnica 1", "característica técnica 2", "característica técnica 3"],
    "publico_alvo_sugerido": "descrição detalhada do público-alvo brasileiro",
    "preco_estimado": "faixa de preço realista em reais",
    "pontos_de_venda": ["vantagem competitiva 1", "vantagem competitiva 2", "vantagem competitiva 3"]
}}"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.primary_model,  # MODELO ATUALIZADO
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 800
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
                    # Validar campos obrigatórios
                    required_fields = ["produto_identificado", "marca", "categoria"]
                    if all(field in analysis for field in required_fields):
                        return analysis
                    else:
                        logger.info("[WARNING] JSON válido mas campos faltando")
                        return None
                        
                except json.JSONDecodeError as e:
                    logger.info(f"[WARNING] JSON inválido do Groq: {e}")
                    return None
            else:
                logger.info(f"[ERROR] Groq API erro: {response.status_code}")
                return None
                
        except Exception as e:
            logger.info(f"[ERROR] Groq analysis falhou: {e}")
            return None
    
    async def _groq_copies(self, product_data: dict, num_copies: int):
        """Gera copies usando Groq com modelo atualizado"""
        copies = []
        strategies = [
            {"name": "URGÊNCIA", "desc": "Crie senso de urgência e escassez"},
            {"name": "BENEFÍCIOS", "desc": "Foque nas vantagens técnicas"},
            {"name": "PREMIUM", "desc": "Destaque exclusividade e qualidade"}
        ]
        
        for i, strategy in enumerate(strategies[:num_copies]):
            try:
                logger.info(f"[GROQ] Gerando copy {i+1}: {strategy['name']}")
                
                copy_prompt = f"""Crie uma copy publicitária brasileira para Facebook/Instagram sobre: {product_data.get('produto_identificado')}

Estratégia: {strategy['desc']}
Público-alvo: {product_data.get('publico_alvo_sugerido')}

REQUISITOS OBRIGATÓRIOS:
- Máximo 80 caracteres total
- Incluir 1-2 emojis brasileiros relevantes
- Call-to-action claro
- Linguagem brasileira natural e persuasiva
- Foco na estratégia {strategy['name']}

Retorne APENAS a copy final, sem aspas, explicações ou markdown."""

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.groq_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.primary_model,  # MODELO ATUALIZADO
                            "messages": [
                                {
                                    "role": "system", 
                                    "content": "Você é especialista em copywriting para redes sociais no Brasil. Seja conciso e persuasivo."
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
                    
                    # Limpar formatação indesejada
                    copy_text = copy_text.replace('```', '').replace('*', '').replace('"', '').strip()
                    
                    # Validar tamanho
                    if len(copy_text) <= 120:  # Limite razoável
                        copies.append({
                            'id': i + 1,
                            'titulo': f'Copy {strategy["name"]}',
                            'texto': copy_text,
                            'estrategia': strategy["name"],
                            'confidence': 0.92,
                            'generated_by': 'groq_real',
                            'ctr_estimado': f'{3.2 + (i * 0.4):.1f}%'
                        })
                        logger.info(f"[OK] Copy {i+1} gerada: {copy_text[:30]}...")
                    else:
                        logger.info(f"[WARNING] Copy {i+1} muito longa, usando fallback")
                        copies.append(self._create_mock_copy(product_data, i + 1, strategy["name"]))
                else:
                    logger.info(f"[ERROR] Copy {i+1} falhou: {response.status_code}")
                    copies.append(self._create_mock_copy(product_data, i + 1, strategy["name"]))
                
            except Exception as e:
                logger.info(f"[ERROR] Copy {i+1} erro: {e}")
                copies.append(self._create_mock_copy(product_data, i + 1, strategy["name"]))
                
        return copies
    
    def _create_mock_copy(self, product_data: dict, copy_id: int, strategy: str):
        """Cria uma copy mock individual"""
        produto = product_data.get('produto_identificado', 'produto')
        
        templates = {
            "URGÊNCIA": f"🔥 {produto} - Últimas unidades! Garanta já!",
            "BENEFÍCIOS": f"⚡ {produto} - Tecnologia premium que impressiona!",
            "PREMIUM": f"✨ {produto} - Exclusividade e qualidade superior!"
        }
        
        return {
            'id': copy_id,
            'titulo': f'Copy {strategy}',
            'texto': templates.get(strategy, f"📱 {produto} - Oportunidade única!"),
            'estrategia': strategy,
            'confidence': 0.78,
            'generated_by': 'mock_fallback'
        }
    
    # MÉTODOS MOCK (mantidos iguais)
    def _mock_analysis(self, prompt: str):
        """Análise mock inteligente"""
        prompt_lower = prompt.lower()
        
        # Detectar marca
        if "iphone" in prompt_lower:
            marca = "Apple"
            if "16 pro max" in prompt_lower:
                modelo = "iPhone 16 Pro Max"
                preco_base = 10000
            elif "16" in prompt_lower:
                modelo = "iPhone 16"
                preco_base = 7000
            elif "15" in prompt_lower:
                modelo = "iPhone 15"
                preco_base = 5500
            else:
                modelo = "iPhone"
                preco_base = 4000
        elif "samsung" in prompt_lower:
            marca = "Samsung"
            modelo = "Galaxy S24" if "s24" in prompt_lower else "Galaxy"
            preco_base = 3500
        elif "xiaomi" in prompt_lower:
            marca = "Xiaomi"
            modelo = "Redmi" if "redmi" in prompt_lower else "Xiaomi"
            preco_base = 2500
        else:
            marca = "Premium"
            modelo = "Smartphone Premium"
            preco_base = 2500
        
        # Detectar condição
        if "seminovo" in prompt_lower:
            condicao = "seminovo"
            fator_preco = 0.75
        elif "usado" in prompt_lower:
            condicao = "usado"
            fator_preco = 0.60
        else:
            condicao = "novo"
            fator_preco = 1.0
        
        preco_final = int(preco_base * fator_preco)
        
        return {
            "produto_identificado": prompt,
            "marca": marca,
            "categoria": condicao,
            "caracteristicas_principais": [
                "Tela premium de alta resolução",
                "Sistema de câmeras profissional", 
                "Processador de última geração"
            ],
            "publico_alvo_sugerido": f"Usuários de {marca}, profissionais e entusiastas de tecnologia, 25-50 anos, classe média-alta brasileira",
            "preco_estimado": f"R$ {preco_final - 500:,} - R$ {preco_final + 500:,}".replace(",", "."),
            "pontos_de_venda": [
                "Tecnologia de ponta garantida",
                "Melhor custo-benefício do mercado", 
                "Suporte técnico especializado no Brasil"
            ]
        }
    
    def _mock_copies(self, product_data: dict, num_copies: int):
        """Copies mock inteligentes"""
        produto = product_data.get('produto_identificado', 'produto')
        marca = product_data.get('marca', 'Premium')
        
        # Templates específicos por marca
        if "iPhone" in produto:
            templates = [
                f"🍎 {produto} - A revolução Apple chegou! Garanta já!",
                f"⚡ {produto} - Performance incomparável iOS!",
                f"✨ {produto} - Exclusividade Apple com desconto especial!"
            ]
        elif "Samsung" in marca:
            templates = [
                f"📱 {produto} - Inovação Samsung que transforma!",
                f"🚀 {produto} - Galaxy: tecnologia do futuro!",
                f"💫 {produto} - Design premium Samsung!"
            ]
        else:
            templates = [
                f"🔥 {produto} - Oferta imperdível! Últimas unidades!",
                f"⭐ {produto} - Tecnologia premium, preço justo!",
                f"💎 {produto} - Qualidade superior garantida!"
            ]
        
        return [
            {
                'id': i + 1,
                'titulo': f'Copy {["URGÊNCIA", "QUALIDADE", "PREMIUM"][i]}',
                'texto': templates[i] if i < len(templates) else templates[0],
                'estrategia': ["URGÊNCIA", "QUALIDADE", "PREMIUM"][i],
                'confidence': 0.85,
                'generated_by': f'enhanced_mock',
                'ctr_estimado': f'{3.2 + (i * 0.4):.1f}%'
            } for i in range(min(num_copies, 3))
        ]
    
    def _mock_images(self, product_data: dict, num_images: int):
        """Imagens mock personalizadas"""
        marca = product_data.get('marca', 'Produto')
        produto_nome = product_data.get('produto_identificado', 'produto')
        
        # Cores por marca
        cores = {
            'Apple': ('1d1d1f', 'f5f5f7'),      # Preto Apple e branco
            'Samsung': ('1428a0', 'ffffff'),    # Azul Samsung
            'Xiaomi': ('ff6900', 'ffffff'),     # Laranja Xiaomi  
            'Premium': ('2c3e50', 'ecf0f1')    # Azul escuro elegante
        }
        
        cor_bg, cor_texto = cores.get(marca, cores['Premium'])
        
        return [
            {
                'id': i + 1,
                'url': f"https://via.placeholder.com/1080x1080/{cor_bg}/{cor_texto}?text={marca}+{i+1}",
                'style': ['Profissional', 'Lifestyle', 'Premium'][i],
                'description': f"Mockup {['profissional', 'lifestyle', 'premium'][i]} para {produto_nome}",
                'generated_by': f'enhanced_mock',
                'confidence': 0.85
            } for i in range(min(num_images, 3))
        ]

# Instância global
logger.info("[CONFIG] Criando AI Generator com modelos Groq atualizados...")
ai_generator_real = AIGeneratorReal()
logger.info("[OK] AI Generator com Groq pronto para uso")