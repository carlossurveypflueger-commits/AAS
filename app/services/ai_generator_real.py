import os
import json
import asyncio
from dotenv import load_dotenv
from app.utils.logger import logger

# Garantir que .env seja carregado
load_dotenv()

class AIGeneratorReal:
    def __init__(self):
        """Inicializa o gerador de IA com modo mock inteligente"""
        
        # Verificar se deve forçar modo mock
        self.force_mock = os.getenv("FORCE_MOCK_MODE", "false").lower() == "true"
        
        logger.info("[CONFIG] INICIALIZANDO AI GENERATOR REAL...")
        
        if self.force_mock:
            logger.info("[MOCK] Modo mock forçado via .env - APIs desabilitadas")
            self.openai_client = None
            self.replicate_client = None
            self.openai_key = None
            self.replicate_token = None
        else:
            # Modo normal - tentar inicializar APIs
            self.openai_key = os.getenv("OPENAI_API_KEY")
            self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
            
            logger.info(f"   OpenAI Key: [OK] Presente" if self.openai_key else "   OpenAI Key: [WARNING] Ausente")
            logger.info(f"   Replicate Token: [OK] Presente" if self.replicate_token else "   Replicate Token: [WARNING] Ausente")
            
            # Inicializar clientes
            self.openai_client = self._init_openai_client()
            self.replicate_client = self._init_replicate_client()
            
            logger.info(f"   Cliente OpenAI: [OK] Ativo" if self.openai_client else "   Cliente OpenAI: [MOCK] Usando fallback")
            logger.info(f"   Cliente Replicate: [OK] Ativo" if self.replicate_client else "   Cliente Replicate: [MOCK] Usando fallback")
        
        # Status final
        mode = "mock" if (self.force_mock or not self.openai_client) else "hybrid"
        logger.info(f"[STATUS] Sistema em modo: {mode.upper()}")
    
    def _init_openai_client(self):
        """Inicializa cliente OpenAI assíncrono"""
        if not self.openai_key:
            return None
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.openai_key)
            logger.info("[OK] Cliente OpenAI Assíncrono inicializado")
            return client
        except Exception as e:
            logger.info(f"[ERROR] Erro ao inicializar OpenAI: {e}")
            return None
    
    def _init_replicate_client(self):
        """Inicializa cliente Replicate"""
        if not self.replicate_token:
            return None
            
        try:
            import replicate
            os.environ["REPLICATE_API_TOKEN"] = self.replicate_token
            logger.info("[OK] Replicate configurado")
            return True
        except Exception as e:
            logger.info(f"[ERROR] Erro ao configurar Replicate: {e}")
            return None
    
    def is_available(self):
        """Retorna status de disponibilidade dos serviços"""
        return {
            "openai": self.openai_client is not None,
            "replicate": self.replicate_client is not None,
            "mode": "mock" if self.force_mock else ("real" if (self.openai_client or self.replicate_client) else "mock"),
            "force_mock": self.force_mock
        }
    
    async def analyze_with_openai(self, prompt):
        """Análise inteligente - usa API se disponível, senão mock"""
        
        # Se modo mock forçado ou sem cliente, usar mock
        if self.force_mock or not self.openai_client:
            logger.info("[MOCK] Usando análise inteligente local")
            return self._enhanced_mock_analysis(prompt)
        
        # Tentar usar OpenAI
        try:
            logger.info(f"[AI] Tentando análise com OpenAI: {prompt[:50]}...")
            
            system_prompt = """Você é um especialista em análise de produtos para marketing digital.
Sua tarefa é analisar produtos e retornar informações estruturadas em JSON.
Seja preciso e use dados realistas baseados no mercado brasileiro."""

            user_prompt = f"""Analise este produto: "{prompt}"

Retorne EXATAMENTE este formato JSON:
{{
    "produto_identificado": "nome completo e específico",
    "marca": "marca identificada", 
    "categoria": "novo/seminovo/usado",
    "caracteristicas_principais": ["característica 1", "característica 2", "característica 3"],
    "publico_alvo_sugerido": "descrição detalhada do público-alvo",
    "preco_estimado": "faixa de preço em reais",
    "pontos_de_venda": ["vantagem 1", "vantagem 2", "vantagem 3"]
}}

IMPORTANTE: Responda APENAS com o JSON, sem texto adicional."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Limpar markdown
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(result)
            logger.info("[OK] Análise OpenAI concluída com sucesso")
            return analysis
            
        except Exception as e:
            logger.info(f"[FALLBACK] OpenAI falhou, usando mock: {e}")
            return self._enhanced_mock_analysis(prompt)
    
    async def generate_copies_with_openai(self, product_data, num_copies=3):
        """Geração de copies - usa API se disponível, senão mock aprimorado"""
        
        if self.force_mock or not self.openai_client:
            logger.info("[MOCK] Usando geração de copies inteligente local")
            return self._enhanced_mock_copies(product_data, num_copies)
        
        # Tentar OpenAI
        try:
            strategies = [
                {"name": "URGENCIA", "description": "Crie senso de urgência e escassez"},
                {"name": "BENEFICIOS", "description": "Foque nas vantagens técnicas"},
                {"name": "SOCIAL_PROOF", "description": "Use aprovação social e credibilidade"}
            ]
            
            copies = []
            
            for i, strategy in enumerate(strategies[:num_copies]):
                logger.info(f"[COPY] Tentando gerar copy {i+1} com OpenAI: {strategy['name']}")
                
                copy_prompt = f"""Crie uma copy publicitária para Facebook/Instagram sobre: {product_data.get('produto_identificado')}

ESTRATÉGIA: {strategy['description']}
PÚBLICO-ALVO: {product_data.get('publico_alvo_sugerido')}
VANTAGENS: {', '.join(product_data.get('pontos_de_venda', []))}

REQUISITOS:
- Máximo 100 caracteres
- 1-2 emojis relevantes  
- Call-to-action claro
- Português brasileiro natural

Retorne apenas a copy final, sem aspas."""

                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Você é especialista em copywriting para redes sociais no Brasil."},
                        {"role": "user", "content": copy_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=80
                )
                
                copy_text = response.choices[0].message.content.strip().strip('"\'')
                
                copies.append({
                    'id': i + 1,
                    'titulo': f'Copy {strategy["name"]}',
                    'texto': copy_text,
                    'estrategia': strategy["name"],
                    'confidence': 0.90 + (i * 0.02),
                    'generated_by': 'openai_real',
                    'ctr_estimado': f'{2.5 + (i * 0.3):.1f}%'
                })
                
                logger.info(f"[OK] Copy {i+1} gerada com OpenAI")
            
            return copies
                
        except Exception as e:
            logger.info(f"[FALLBACK] OpenAI falhou para copies, usando mock: {e}")
            return self._enhanced_mock_copies(product_data, num_copies)
    
    async def generate_images_with_replicate(self, product_data, num_images=3):
        """Geração de imagens - sempre usa mock por enquanto"""
        logger.info("[MOCK] Usando geração de imagens mock (mais estável)")
        return self._enhanced_mock_images(product_data, num_images)
    
    # MÉTODOS MOCK APRIMORADOS
    def _enhanced_mock_analysis(self, prompt):
        """Análise mock muito mais inteligente"""
        prompt_lower = prompt.lower()
        
        # Detectar marca
        if "iphone" in prompt_lower:
            marca = "Apple"
            if "15 pro max" in prompt_lower:
                modelo = "iPhone 15 Pro Max"
                preco_base = 8000
            elif "15 pro" in prompt_lower:
                modelo = "iPhone 15 Pro"  
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
            preco_base = 2000
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
        
        # Detectar armazenamento
        if "1tb" in prompt_lower or "1000gb" in prompt_lower:
            preco_base += 1000
        elif "512gb" in prompt_lower:
            preco_base += 500
        elif "256gb" in prompt_lower:
            preco_base += 250
        
        preco_final = int(preco_base * fator_preco)
        
        return {
            "produto_identificado": prompt,
            "marca": marca,
            "categoria": condicao,
            "caracteristicas_principais": [
                f"Tela premium de alta resolução",
                f"Câmera profissional avançada", 
                f"Performance excepcional"
            ],
            "publico_alvo_sugerido": f"Usuários de {marca}, profissionais e entusiastas de tecnologia, 25-50 anos, classe média-alta",
            "preco_estimado": f"R$ {preco_final - 500} - R$ {preco_final + 500}",
            "pontos_de_venda": [
                "Qualidade comprovada e garantida",
                "Melhor custo-benefício do mercado",
                "Suporte técnico especializado"
            ]
        }
    
    def _enhanced_mock_copies(self, product_data, num_copies):
        """Copies mock muito mais inteligentes"""
        produto = product_data.get('produto_identificado', 'produto')
        marca = product_data.get('marca', 'Premium')
        
        # Templates inteligentes baseados na marca
        if "iPhone" in produto:
            templates = [
                f"🔥 {produto} - Tecnologia Apple que impressiona! Garanta já o seu!",
                f"⚡ {produto} - Performance incomparável para quem exige o melhor!",
                f"✨ {produto} - Exclusividade Apple com preço especial. Últimas unidades!"
            ]
        elif "Samsung" in marca:
            templates = [
                f"📱 {produto} - Inovação Samsung que transforma seu dia!",
                f"🚀 {produto} - Design premium e tecnologia de ponta!",
                f"💫 {produto} - Samsung Galaxy: o futuro em suas mãos!"
            ]
        else:
            templates = [
                f"🔥 {produto} - Oferta imperdível! Aproveite enquanto durarem!",
                f"⭐ {produto} - Tecnologia premium com preço justo!",
                f"💎 {produto} - Qualidade superior, resultado garantido!"
            ]
        
        return [
            {
                'id': i + 1,
                'titulo': f'Copy {["URGÊNCIA", "QUALIDADE", "PREMIUM"][i]}',
                'texto': templates[i] if i < len(templates) else templates[0],
                'estrategia': ["URGÊNCIA", "QUALIDADE", "PREMIUM"][i],
                'confidence': 0.85 + (i * 0.03),
                'generated_by': 'enhanced_mock',
                'ctr_estimado': f'{3.2 + (i * 0.4):.1f}%'
            } for i in range(min(num_copies, 3))
        ]
    
    def _enhanced_mock_images(self, product_data, num_images):
        """Imagens mock personalizadas"""
        marca = product_data.get('marca', 'Produto')
        produto = product_data.get('produto_identificado', 'produto')
        
        # Cores por marca
        cores = {
            'Apple': ('000000', 'ffffff'),      # Preto e branco
            'Samsung': ('1428a0', 'ffffff'),    # Azul Samsung
            'Xiaomi': ('ff6900', 'ffffff'),     # Laranja Xiaomi
            'Premium': ('2c3e50', 'ecf0f1')    # Azul escuro
        }
        
        cor_bg, cor_texto = cores.get(marca, cores['Premium'])
        
        return [
            {
                'id': i + 1,
                'url': f"https://via.placeholder.com/1080x1080/{cor_bg}/{cor_texto}?text={marca.replace(' ', '+')}+{i+1}",
                'style': ['Profissional', 'Lifestyle', 'Premium'][i],
                'description': f"Imagem {['profissional', 'lifestyle', 'premium'][i]} para {produto}",
                'generated_by': 'enhanced_mock',
                'confidence': 0.85 + (i * 0.03)
            } for i in range(min(num_images, 3))
        ]

# Instância global
logger.info("[CONFIG] Criando instância global do AI Generator...")
ai_generator_real = AIGeneratorReal()
logger.info("[OK] AI Generator Real pronto para uso")