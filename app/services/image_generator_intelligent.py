# app/services/image_generator_intelligent.py
"""
Image Generator Inteligente v2.2
- Recebe prompts gerados pela IA (Groq)
- Adaptável para qualquer produto eletrônico
- Estratégias visuais baseadas nas estratégias de copy
"""

import os
import asyncio
import httpx
import base64
from typing import List, Dict, Optional
from dotenv import load_dotenv
from app.utils.logger import logger

load_dotenv()

class ImageGeneratorIntelligent:
    def __init__(self):
        """Inicializa o gerador inteligente que usa prompts da IA"""
        
        # APIs disponíveis
        self.stability_key = os.getenv("STABILITY_API_KEY")
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        
        # URLs das APIs
        self.stability_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        self.huggingface_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        
        # Estratégia
        if self.stability_key:
            self.primary_strategy = "stability"
            logger.info("[IMAGE] Estratégia: Stability AI com prompts IA")
        elif self.hf_token:
            self.primary_strategy = "huggingface"
            logger.info("[IMAGE] Estratégia: HuggingFace com prompts IA")
        else:
            self.primary_strategy = "mock"
            logger.info("[IMAGE] Estratégia: Mock inteligente")
        
        logger.info(f"[CONFIG] Image Generator Inteligente inicializado")
    
    async def generate_with_ai_prompts(self, product_data: Dict, ai_prompts: List[Dict]) -> List[Dict]:
        """
        Método principal - usa prompts gerados pela IA do Groq
        """
        logger.info(f"[IMAGE] Processando {len(ai_prompts)} prompts gerados por IA")
        
        images = []
        
        for i, prompt_data in enumerate(ai_prompts):
            logger.info(f"[IMAGE] Gerando imagem {i+1}: {prompt_data.get('style', 'Sem nome')}")
            logger.info(f"[AI-PROMPT] Estratégia: {prompt_data.get('strategy', 'N/A')}")
            logger.info(f"[AI-PROMPT] Prompt: {prompt_data.get('prompt', 'N/A')[:80]}...")
            
            # Tentar gerar imagem real
            image = None
            
            # Primeira tentativa: Stability AI
            if self.stability_key and not image:
                image = await self._generate_with_stability(prompt_data, i + 1)
            
            # Segunda tentativa: HuggingFace
            if self.hf_token and not image:
                image = await self._generate_with_huggingface(prompt_data, i + 1)
            
            # Fallback: Mock inteligente baseado na estratégia
            if not image:
                image = self._create_strategy_mock(product_data, prompt_data, i + 1)
            
            images.append(image)
        
        logger.info(f"[SUCCESS] {len(images)} imagens processadas com prompts IA")
        return images
    
    async def _generate_with_stability(self, prompt_data: Dict, image_id: int) -> Optional[Dict]:
        """Gera imagem com Stability AI usando prompt da IA"""
        try:
            logger.info(f"[STABILITY] Usando prompt IA para imagem {image_id}")
            
            # Usar o prompt gerado pela IA + otimizações
            base_prompt = prompt_data.get('prompt', '')
            enhanced_prompt = f"{base_prompt}, professional commercial photography, ultra high quality, 8k resolution, marketing photography"
            
            # Prompt negativo baseado na estratégia
            negative_prompt = self._get_negative_prompt_for_strategy(prompt_data.get('strategy', ''))
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.stability_url,
                    headers={
                        "Authorization": f"Bearer {self.stability_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "text_prompts": [
                            {"text": enhanced_prompt, "weight": 1.0},
                            {"text": negative_prompt, "weight": -0.6}
                        ],
                        "cfg_scale": 8,
                        "height": 1024,
                        "width": 1024,
                        "samples": 1,
                        "steps": 35,  # Mais steps para melhor qualidade
                        "style_preset": "photographic"
                    },
                    timeout=100
                )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('artifacts') and len(result['artifacts']) > 0:
                    image_b64 = result["artifacts"][0]["base64"]
                    
                    logger.info(f"[SUCCESS] Stability AI - Imagem {image_id} com prompt IA gerada")
                    
                    return {
                        'id': image_id,
                        'url': f"data:image/png;base64,{image_b64}",
                        'style': prompt_data.get('style', 'AI Generated'),
                        'strategy': prompt_data.get('strategy', 'N/A'),
                        'description': prompt_data.get('description', 'Imagem gerada por IA'),
                        'generated_by': 'stability_ai_with_groq',
                        'confidence': 0.96,
                        'quality': 'ai_prompt_professional',
                        'ai_prompt_used': enhanced_prompt[:100] + "...",
                        'original_strategy': prompt_data.get('strategy')
                    }
                else:
                    logger.info(f"[ERROR] Stability AI - Sem artifacts na resposta")
                    return None
            else:
                logger.info(f"[ERROR] Stability AI - Status {response.status_code}")
                return None
                
        except asyncio.TimeoutError:
            logger.info(f"[ERROR] Stability AI - Timeout na imagem {image_id}")
            return None
        except Exception as e:
            logger.info(f"[ERROR] Stability AI - Erro: {str(e)}")
            return None
    
    async def _generate_with_huggingface(self, prompt_data: Dict, image_id: int) -> Optional[Dict]:
        """Gera imagem com HuggingFace usando prompt da IA"""
        try:
            logger.info(f"[HUGGINGFACE] Usando prompt IA para imagem {image_id}")
            
            headers = {"Content-Type": "application/json"}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            # Otimizar prompt para HuggingFace
            base_prompt = prompt_data.get('prompt', '')
            hf_optimized = f"{base_prompt}, masterpiece, best quality, highly detailed, professional photography, commercial quality, 8k"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.huggingface_url,
                    headers=headers,
                    json={
                        "inputs": hf_optimized,
                        "parameters": {
                            "guidance_scale": 7.5,
                            "num_inference_steps": 30,
                            "width": 1024,
                            "height": 1024
                        }
                    },
                    timeout=100
                )
            
            if response.status_code == 200:
                image_bytes = response.content
                if len(image_bytes) > 5000:
                    image_b64 = base64.b64encode(image_bytes).decode()
                    
                    logger.info(f"[SUCCESS] HuggingFace - Imagem {image_id} com prompt IA gerada")
                    
                    return {
                        'id': image_id,
                        'url': f"data:image/jpeg;base64,{image_b64}",
                        'style': prompt_data.get('style', 'AI Generated'),
                        'strategy': prompt_data.get('strategy', 'N/A'),
                        'description': prompt_data.get('description', 'Imagem gerada por IA'),
                        'generated_by': 'huggingface_with_groq',
                        'confidence': 0.92,
                        'quality': 'ai_prompt_professional',
                        'ai_prompt_used': hf_optimized[:100] + "...",
                        'original_strategy': prompt_data.get('strategy')
                    }
                else:
                    logger.info(f"[ERROR] HuggingFace - Resposta muito pequena")
                    return None
            elif response.status_code == 503:
                logger.info(f"[INFO] HuggingFace - Modelo carregando")
                return None
            else:
                logger.info(f"[ERROR] HuggingFace - Status {response.status_code}")
                return None
                
        except asyncio.TimeoutError:
            logger.info(f"[ERROR] HuggingFace - Timeout na imagem {image_id}")
            return None
        except Exception as e:
            logger.info(f"[ERROR] HuggingFace - Erro: {str(e)}")
            return None
    
    def _create_strategy_mock(self, product_data: Dict, prompt_data: Dict, image_id: int) -> Dict:
        """Cria mock inteligente baseado na estratégia da campanha"""
        
        marca = product_data.get('marca', 'Produto')
        tipo_produto = product_data.get('tipo_produto', 'eletronico')
        strategy = prompt_data.get('strategy', 'PADRÃO')
        
        # Cores e estilos baseados na estratégia
        strategy_colors = {
            'URGÊNCIA': ('ff4444', 'ffffff'),          # Vermelho urgente
            'PREMIUM': ('1a1a1a', 'f5f5f5'),          # Preto premium
            'CUSTO_BENEFÍCIO': ('2ecc71', 'ffffff'),   # Verde economia
            'PROFISSIONAL': ('34495e', 'ffffff'),      # Azul corporativo
            'GAMER': ('9b59b6', '00ff00'),             # Roxo e verde neon
            'LIFESTYLE': ('3498db', 'ffffff')          # Azul lifestyle
        }
        
        # Cores da marca como fallback
        brand_colors = {
            'Apple': ('f5f5f7', '1d1d1f'),
            'Samsung': ('ffffff', '1428a0'), 
            'Xiaomi': ('ffffff', 'ff6900'),
            'Motorola': ('ffffff', '0066cc'),
            'Premium': ('f8f9fa', '2c3e50')
        }
        
        # Escolher cores: estratégia primeiro, marca como fallback
        if strategy in strategy_colors:
            cor_bg, cor_texto = strategy_colors[strategy]
        else:
            cor_bg, cor_texto = brand_colors.get(marca, brand_colors['Premium'])
        
        # Texto do placeholder baseado na estratégia
        strategy_texts = {
            'URGÊNCIA': f'{marca}+URGENTE+{image_id}',
            'PREMIUM': f'{marca}+PREMIUM+{image_id}',
            'CUSTO_BENEFÍCIO': f'{marca}+OFERTA+{image_id}',
            'PROFISSIONAL': f'{marca}+PRO+{image_id}',
            'GAMER': f'{marca}+GAMING+{image_id}',
            'LIFESTYLE': f'{marca}+LIFE+{image_id}'
        }
        
        text_overlay = strategy_texts.get(strategy, f'{marca}+{tipo_produto}+{image_id}')
        
        logger.info(f"[MOCK] Gerando mock inteligente: {strategy} -> {cor_bg}/{cor_texto}")
        
        return {
            'id': image_id,
            'url': f"https://via.placeholder.com/1024x1024/{cor_bg}/{cor_texto}?text={text_overlay}",
            'style': prompt_data.get('style', f'{strategy} Style'),
            'strategy': strategy,
            'description': prompt_data.get('description', f'Mock {strategy} para {tipo_produto}'),
            'generated_by': 'intelligent_mock',
            'confidence': 0.82,
            'quality': 'strategic_mock',
            'ai_prompt_used': f'Mock baseado na estratégia {strategy}',
            'original_strategy': strategy,
            'colors_used': f'#{cor_bg} / #{cor_texto}',
            'strategy_optimized': True
        }
    
    def _get_negative_prompt_for_strategy(self, strategy: str) -> str:
        """Retorna prompt negativo específico para cada estratégia"""
        
        base_negative = "blurry, low quality, distorted, amateur, bad lighting, pixelated, ugly, watermark"
        
        strategy_negatives = {
            'URGÊNCIA': f"{base_negative}, calm, peaceful, static, slow",
            'PREMIUM': f"{base_negative}, cheap, plastic, low-end, basic",
            'CUSTO_BENEFÍCIO': f"{base_negative}, expensive, luxury, exclusive",
            'PROFISSIONAL': f"{base_negative}, casual, messy, unprofessional, chaotic",
            'GAMER': f"{base_negative}, boring, office, corporate, plain",
            'LIFESTYLE': f"{base_negative}, technical, sterile, cold, industrial"
        }
        
        return strategy_negatives.get(strategy, base_negative)
    
    # ==================== FALLBACKS E COMPATIBILIDADE ====================
    
    async def generate_product_images(self, product_data: Dict, num_images: int = 3) -> List[Dict]:
        """
        Método de compatibilidade - gera prompts básicos se não receber prompts IA
        """
        logger.info(f"[COMPAT] Gerando {num_images} imagens sem prompts IA (modo compatibilidade)")
        
        # Gerar prompts básicos
        basic_prompts = self._generate_basic_prompts(product_data, num_images)
        
        # Usar o método principal
        return await self.generate_with_ai_prompts(product_data, basic_prompts)
    
    def _generate_basic_prompts(self, product_data: Dict, num_images: int) -> List[Dict]:
        """Gera prompts básicos quando não há prompts da IA"""
        
        marca = product_data.get('marca', 'Premium')
        tipo_produto = product_data.get('tipo_produto', 'eletronico')
        categoria_uso = product_data.get('categoria_uso', 'casual')
        
        basic_prompts = []
        
        styles = ['Professional', 'Lifestyle', 'Premium']
        strategies = ['PROFISSIONAL', 'LIFESTYLE', 'PREMIUM']
        
        for i in range(min(num_images, 3)):
            prompt = f"professional commercial photography of {marca} {tipo_produto}, clean composition, studio lighting, high quality"
            
            basic_prompts.append({
                'id': i + 1,
                'style': styles[i],
                'strategy': strategies[i],
                'prompt': prompt,
                'description': f'Imagem {styles[i].lower()} do {tipo_produto}'
            })
        
        return basic_prompts
    
    def get_status(self) -> Dict:
        """Retorna status do gerador inteligente"""
        return {
            "primary_strategy": self.primary_strategy,
            "availability": {
                "stability": bool(self.stability_key),
                "huggingface": bool(self.hf_token),
                "intelligent_mock": True
            },
            "features": {
                "ai_prompts": True,
                "strategy_based": True,
                "multi_product": True
            },
            "ready": True
        }
    
    def is_real_generation_available(self) -> bool:
        """Verifica se geração real está disponível"""
        return bool(self.stability_key or self.hf_token)

# Instância global
image_generator_intelligent = ImageGeneratorIntelligent()