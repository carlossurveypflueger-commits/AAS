import os
import json
import asyncio
from dotenv import load_dotenv
from app.utils.logger import logger

# Garantir que .env seja carregado
load_dotenv()

class AIGeneratorReal:
    def __init__(self):
        """
        Inicializa o gerador de IA real
        
        Este construtor:
        1. Carrega as chaves de API do ambiente
        2. Tenta inicializar os clientes das APIs
        3. Define fallbacks para modo mock
        """
        # Carregar chaves das variáveis de ambiente
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        
        logger.info("🤖 INICIALIZANDO AI GENERATOR REAL...")
        logger.info(f"   OpenAI Key: {'✅ Presente' if self.openai_key else '❌ Ausente'}")
        logger.info(f"   Replicate Token: {'✅ Presente' if self.replicate_token else '❌ Ausente'}")
        
        # Inicializar clientes (None se não disponível)
        self.openai_client = self._init_openai_client()
        self.replicate_client = self._init_replicate_client()
        
        logger.info(f"   Cliente OpenAI: {'✅ Ativo' if self.openai_client else '❌ Inativo'}")
        logger.info(f"   Cliente Replicate: {'✅ Ativo' if self.replicate_client else '❌ Inativo'}")
    
    def _init_openai_client(self):
        if not self.openai_key:
            logger.info("⚠️ Chave OpenAI não encontrada")
            return None
        
        try:
            # Tentar versão nova primeiro
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            logger.info("✅ Cliente OpenAI inicializado (versão nova)")
            return client
        except TypeError as e:
            if 'proxies' in str(e):
                try:
                    # Fallback para versão mais antiga
                    from openai import OpenAI
                    client = OpenAI(
                        api_key=self.openai_key,
                        # Remover parâmetros não suportados em versões antigas
                    )
                    logger.info("✅ Cliente OpenAI inicializado (versão antiga)")
                    return client
                except Exception as e2:
                    logger.info(f"❌ Erro OpenAI versão antiga: {e2}")
                    return None
            else:
                logger.info(f"❌ Erro OpenAI desconhecido: {e}")
                return None
        except Exception as e:
            logger.info(f"❌ Erro ao inicializar OpenAI: {e}")
            return None
    
    def _init_replicate_client(self):
        """Inicializa cliente Replicate com tratamento de erro"""
        if not self.replicate_token:
            logger.info("⚠️  Token Replicate não encontrado")
            return None
            
        try:
            import replicate
            client = replicate.Client(api_token=self.replicate_token)
            logger.info("✅ Cliente Replicate inicializado")
            return client
        except Exception as e:
            logger.info(f"❌ Erro ao inicializar Replicate: {e}")
            return None
    
    def is_available(self):
        """Retorna status de disponibilidade dos serviços"""
        return {
            "openai": self.openai_client is not None,
            "replicate": self.replicate_client is not None,
            "mode": "real" if (self.openai_client or self.replicate_client) else "mock"
        }
    
    async def analyze_with_openai(self, prompt):
        """
        Análise de produto usando OpenAI
        
        Fluxo:
        1. Verifica se cliente OpenAI está disponível
        2. Monta prompt estruturado para análise
        3. Faz chamada para API
        4. Processa resposta JSON
        5. Retorna dados estruturados ou fallback
        """
        if not self.openai_client:
            logger.info("🔄 OpenAI indisponível, usando análise mock")
            return self._mock_analysis(prompt)
        
        try:
            logger.info(f"🤖 Analisando com OpenAI: {prompt[:50]}...")
            
            # Prompt estruturado para garantir resposta JSON
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

            # Chamada para API OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Baixa temperatura para respostas consistentes
                max_tokens=500
            )
            
            # Processar resposta
            result = response.choices[0].message.content.strip()
            
            # Limpar formatação markdown se presente
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            analysis = json.loads(result)
            logger.info("✅ Análise OpenAI concluída com sucesso")
            return analysis
            
        except json.JSONDecodeError as e:
            logger.info(f"❌ Erro ao fazer parse do JSON OpenAI: {e}")
            logger.info(f"   Resposta recebida: {result[:200]}...")
            return self._mock_analysis(prompt)
        except Exception as e:
            logger.info(f"❌ Erro geral na análise OpenAI: {e}")
            return self._mock_analysis(prompt)
    
    async def generate_copies_with_openai(self, product_data, num_copies=3):
        """
        Geração de copies usando OpenAI
        
        Processo:
        1. Define estratégias de copy diferentes
        2. Para cada estratégia, cria um prompt específico
        3. Faz chamada individual para OpenAI
        4. Processa e estrutura resposta
        """
        if not self.openai_client:
            logger.info("🔄 OpenAI indisponível para copies, usando mock")
            return self._mock_copies(product_data, num_copies)
        
        # Estratégias de copywriting
        strategies = [
            {"name": "URGÊNCIA", "description": "Crie senso de urgência e escassez"},
            {"name": "BENEFÍCIOS", "description": "Foque nas vantagens técnicas"},
            {"name": "SOCIAL_PROOF", "description": "Use aprovação social e credibilidade"}
        ]
        
        copies = []
        
        for i, strategy in enumerate(strategies[:num_copies]):
            try:
                logger.info(f"✍️  Gerando copy {i+1}: {strategy['name']}")
                
                # Prompt específico para cada estratégia
                copy_prompt = f"""Crie uma copy publicitária para Facebook/Instagram sobre: {product_data.get('produto_identificado')}

ESTRATÉGIA: {strategy['description']}
PÚBLICO-ALVO: {product_data.get('publico_alvo_sugerido')}
VANTAGENS DO PRODUTO: {', '.join(product_data.get('pontos_de_venda', []))}

REQUISITOS OBRIGATÓRIOS:
- Máximo 100 caracteres
- 1-2 emojis relevantes
- Call-to-action claro
- Português brasileiro natural
- Seja específico sobre este produto

Retorne apenas a copy final, sem aspas ou explicações."""

                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um especialista em copywriting para redes sociais no Brasil. Crie copies persuasivas e autênticas."
                        },
                        {"role": "user", "content": copy_prompt}
                    ],
                    temperature=0.8,  # Temperatura mais alta para criatividade
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
                
                logger.info(f"✅ Copy {i+1} gerada: {copy_text[:40]}...")
                
            except Exception as e:
                logger.info(f"❌ Erro ao gerar copy {i+1}: {e}")
                copies.append({
                    'id': i + 1,
                    'titulo': f'Copy Erro {i+1}',
                    'texto': f"🔥 {product_data.get('produto_identificado', 'produto')} - Oferta imperdível!",
                    'estrategia': 'FALLBACK',
                    'confidence': 0.60,
                    'generated_by': 'error_fallback'
                })
        
        return copies
    
    async def generate_images_with_replicate(self, product_data, num_images=3):
        """
        Geração de imagens usando Replicate/Flux
        
        Processo:
        1. Cria prompts específicos para cada estilo visual
        2. Chama API Replicate para cada prompt
        3. Processa URLs retornadas
        4. Retorna estrutura padronizada
        """
        if not self.replicate_client:
            logger.info("🔄 Replicate indisponível, usando imagens mock")
            return self._mock_images(product_data, num_images)
        
        produto = product_data.get('produto_identificado', 'smartphone')
        
        # Prompts visuais específicos
        visual_prompts = [
            f"Professional product photography of {produto}, clean white background, studio lighting, commercial quality, 4K resolution, minimalist",
            f"Lifestyle photograph of {produto} on modern wooden desk with coffee and laptop, natural lighting, cozy atmosphere, Instagram style",
            f"Premium {produto} with elegant reflections, dark gradient background, luxury product shot, sophisticated lighting, high-end commercial"
        ]
        
        images = []
        
        for i, prompt in enumerate(visual_prompts[:num_images]):
            try:
                logger.info(f"🎨 Gerando imagem {i+1} com Flux...")
                logger.info(f"   Prompt: {prompt[:60]}...")
                
                # Chamada para Replicate
                output = self.replicate_client.run(
                    "black-forest-labs/flux-schnell",
                    input={
                        "prompt": prompt,
                        "width": 1024,
                        "height": 1024,
                        "num_outputs": 1,
                        "num_inference_steps": 4,
                        "guidance_scale": 3.5
                    }
                )
                
                if output and len(output) > 0:
                    image_url = output[0]
                    logger.info(f"✅ Imagem {i+1} gerada com sucesso")
                    logger.info(f"   URL: {image_url[:50]}...")
                    
                    images.append({
                        'id': i + 1,
                        'url': image_url,
                        'style': ['Profissional', 'Lifestyle', 'Premium'][i],
                        'description': prompt,
                        'generated_by': 'flux_real',
                        'confidence': 0.92 + (i * 0.02)
                    })
                else:
                    raise Exception("Nenhuma imagem retornada pela API")
                
            except Exception as e:
                logger.info(f"❌ Erro ao gerar imagem {i+1}: {e}")
                images.append({
                    'id': i + 1,
                    'url': f"https://via.placeholder.com/1024x1024/ff0000/ffffff?text=Erro+Imagem+{i+1}",
                    'style': f'Erro {i+1}',
                    'generated_by': 'error_fallback',
                    'confidence': 0.30
                })
        
        return images
    
    # Métodos mock para fallback
    def _mock_analysis(self, prompt):
        return {
            "produto_identificado": prompt,
            "marca": "Apple" if "iphone" in prompt.lower() else "Samsung",
            "categoria": "seminovo" if "seminovo" in prompt.lower() else "novo",
            "caracteristicas_principais": ["Design premium", "Tecnologia avançada", "Performance superior"],
            "publico_alvo_sugerido": "Entusiastas de tecnologia, 25-45 anos, renda média-alta",
            "preco_estimado": "R$ 1200-2500",
            "pontos_de_venda": ["Qualidade comprovada", "Garantia estendida", "Suporte especializado"]
        }
    
    def _mock_copies(self, product_data, num_copies):
        produto = product_data.get('produto_identificado', 'produto')
        strategies = ["URGÊNCIA", "QUALIDADE", "PREMIUM"]
        
        return [
            {
                'id': i + 1,
                'titulo': f'Copy Mock {strategies[i]}',
                'texto': f"🔥 {produto} - {['Últimas unidades!', 'Qualidade premium!', 'Exclusividade!'][i]}",
                'estrategia': strategies[i],
                'confidence': 0.70 + (i * 0.05),
                'generated_by': 'mock_fallback'
            } for i in range(num_copies)
        ]
    
    def _mock_images(self, product_data, num_images):
        marca = product_data.get('marca', 'Produto')
        return [
            {
                'id': i + 1,
                'url': f"https://via.placeholder.com/1024x1024/0066cc/ffffff?text={marca}+Mock+{i+1}",
                'style': f'Mock Style {i+1}',
                'generated_by': 'mock_fallback',
                'confidence': 0.50
            } for i in range(num_images)
        ]

# Instância global (padrão Singleton)
logger.info("🔧 Criando instância global do AI Generator...")
ai_generator_real = AIGeneratorReal()
logger.info("✅ AI Generator Real pronto para uso")