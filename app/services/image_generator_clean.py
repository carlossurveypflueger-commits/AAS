# app/services/image_generator_clean.py
"""
Gerador de imagens limpo e integrado
Primeira tentativa: Stability AI
Segunda tentativa: HuggingFace 
Fallback: Mock inteligente
"""

import os
import asyncio
import httpx
import base64
from typing import List, Dict, Optional
from dotenv import load_dotenv
from app.utils.logger import logger

load_dotenv()

class ImageGeneratorClean:
    def __init__(self):
        """Inicializa o gerador de imagens com fallbacks"""
        
        # APIs disponíveis
        self.stability_key = os.getenv("STABILITY_API_KEY")
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        
        # URLs das APIs
        self.stability_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        self.huggingface_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        
        # Determinar estratégia
        if self.stability_key:
            self.primary_strategy = "stability"
            logger.info("[IMAGE] Estratégia primária: Stability AI")
        elif self.hf_token:
            self.primary_strategy = "huggingface"
            logger.info("[IMAGE] Estratégia primária: HuggingFace")
        else:
            self.primary_strategy = "mock"
            logger.info("[IMAGE] Estratégia primária: Mock (sem APIs)")
        
        logger.info(f"[CONFIG] Image Generator Clean inicializado")
        logger.info(f"   Stability AI: {'✅' if self.stability_key else '❌'}")
        logger.info(f"   HuggingFace: {'✅' if self.hf_token else '❌'}")
    
    async def generate_product_images(self, product_data: Dict, num_images: int = 3) -> List[Dict]:
        """
        Método principal - tenta Stability, depois HuggingFace, depois Mock
        """
        logger.info(f"[IMAGE] Gerando {num_images} imagens para: {product_data.get('produto_identificado', 'produto')}")
        
        # Criar prompts para o produto
        prompts = self._create_product_prompts(product_data, num_images)
        images = []
        
        for i, prompt_data in enumerate(prompts):
            logger.info(f"[IMAGE] Processando imagem {i+1}: {prompt_data['style']}")
            
            # Tentar Stability AI primeiro
            image = None
            if self.stability_key and not image:
                image = await self._try_stability(prompt_data, i + 1)
            
            # Fallback para HuggingFace
            if self.hf_token and not image:
                image = await self._try_huggingface(prompt_data, i + 1)
            
            # Último fallback: Mock inteligente
            if not image:
                image = self._create_smart_mock(product_data, prompt_data, i + 1)
            
            images.append(image)
        
        logger.info(f"[SUCCESS] {len(images)} imagens geradas com sucesso")
        return images
    
    def _create_product_prompts(self, product_data: Dict, num_images: int) -> List[Dict]:
        """Cria prompts específicos para o produto"""
        
        produto = product_data.get('produto_identificado', 'smartphone')
        marca = product_data.get('marca', 'Premium')
        
        # Prompts específicos para diferentes estilos
        base_prompts = [
            {
                'style': 'Profissional',
                'prompt': f"professional product photography of {produto}, clean white background, studio lighting, commercial quality, high resolution, minimalist, centered composition",
                'description': f'Foto profissional do {produto} em fundo branco'
            },
            {
                'style': 'Lifestyle', 
                'prompt': f"lifestyle photograph of {produto}, modern workspace setup, natural lighting, premium desk environment, Instagram aesthetic, warm tones",
                'description': f'Foto lifestyle do {produto} em ambiente moderno'
            },
            {
                'style': 'Premium',
                'prompt': f"luxury {produto} product shot, elegant dark background with reflections, sophisticated lighting, premium materials, high-end commercial photography",
                'description': f'Foto premium do {produto} com reflexos elegantes'
            }
        ]
        
        return base_prompts[:num_images]
    
    async def _try_stability(self, prompt_data: Dict, image_id: int) -> Optional[Dict]:
        """Tenta gerar imagem com Stability AI"""
        try:
            logger.info(f"[STABILITY] Tentando gerar imagem {image_id}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.stability_url,
                    headers={
                        "Authorization": f"Bearer {self.stability_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "text_prompts": [{"text": prompt_data['prompt']}],
                        "cfg_scale": 7,
                        "height": 1024,
                        "width": 1024,
                        "samples": 1,
                        "steps": 20
                    },
                    timeout=60  # 60 segundos timeout
                )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('artifacts') and len(result['artifacts']) > 0:
                    image_b64 = result["artifacts"][0]["base64"]
                    
                    logger.info(f"[SUCCESS] Stability AI - Imagem {image_id} gerada ({len(image_b64)} chars)")
                    
                    return {
                        'id': image_id,
                        'url': f"data:image/png;base64,{image_b64}",
                        'style': prompt_data['style'],
                        'description': prompt_data['description'],
                        'generated_by': 'stability_ai',
                        'confidence': 0.95,
                        'prompt_used': prompt_data['prompt'][:50] + "..."
                    }
                else:
                    logger.info(f"[ERROR] Stability AI - Resposta sem artifacts")
                    return None
            else:
                logger.info(f"[ERROR] Stability AI - Status {response.status_code}: {response.text[:100]}")
                return None
                
        except asyncio.TimeoutError:
            logger.info(f"[ERROR] Stability AI - Timeout na imagem {image_id}")
            return None
        except Exception as e:
            logger.info(f"[ERROR] Stability AI - Erro: {str(e)}")
            return None
    
    async def _try_huggingface(self, prompt_data: Dict, image_id: int) -> Optional[Dict]:
        """Tenta gerar imagem com HuggingFace"""
        try:
            logger.info(f"[HUGGINGFACE] Tentando gerar imagem {image_id}...")
            
            headers = {"Content-Type": "application/json"}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.huggingface_url,
                    headers=headers,
                    json={"inputs": prompt_data['prompt']},
                    timeout=60
                )
            
            if response.status_code == 200:
                image_bytes = response.content
                if len(image_bytes) > 1000:  # Validar se não é uma mensagem de erro
                    image_b64 = base64.b64encode(image_bytes).decode()
                    
                    logger.info(f"[SUCCESS] HuggingFace - Imagem {image_id} gerada ({len(image_bytes)} bytes)")
                    
                    return {
                        'id': image_id,
                        'url': f"data:image/jpeg;base64,{image_b64}",
                        'style': prompt_data['style'],
                        'description': prompt_data['description'],
                        'generated_by': 'huggingface',
                        'confidence': 0.88,
                        'prompt_used': prompt_data['prompt'][:50] + "..."
                    }
                else:
                    logger.info(f"[ERROR] HuggingFace - Resposta muito pequena")
                    return None
            elif response.status_code == 503:
                logger.info(f"[INFO] HuggingFace - Modelo carregando (normal)")
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
    
    def _create_smart_mock(self, product_data: Dict, prompt_data: Dict, image_id: int) -> Dict:
        """Cria mock inteligente baseado no produto"""
        
        marca = product_data.get('marca', 'Premium')
        produto = product_data.get('produto_identificado', 'produto')
        
        # Cores personalizadas por marca
        brand_colors = {
            'Apple': ('1d1d1f', 'f5f5f7'),      # Preto Apple e branco
            'Samsung': ('1428a0', 'ffffff'),    # Azul Samsung
            'Xiaomi': ('ff6900', 'ffffff'),     # Laranja Xiaomi
            'Motorola': ('0066cc', 'ffffff'),   # Azul Motorola
            'LG': ('a50034', 'ffffff'),         # Vinho LG
            'Sony': ('000000', 'ffffff'),       # Preto Sony
            'Premium': ('2c3e50', 'ecf0f1')    # Azul escuro elegante
        }
        
        bg_color, text_color = brand_colors.get(marca, brand_colors['Premium'])
        
        # Texto personalizado por estilo
        style_texts = {
            'Profissional': f'{marca}+Studio',
            'Lifestyle': f'{marca}+Life', 
            'Premium': f'{marca}+Luxury'
        }
        
        text_overlay = style_texts.get(prompt_data['style'], f'{marca}+{image_id}')
        
        logger.info(f"[MOCK] Gerando mock inteligente para {marca} - {prompt_data['style']}")
        
        return {
            'id': image_id,
            'url': f"https://via.placeholder.com/1024x1024/{bg_color}/{text_color}?text={text_overlay}",
            'style': prompt_data['style'],
            'description': prompt_data['description'], 
            'generated_by': 'smart_mock',
            'confidence': 0.75,
            'prompt_used': 'Mock baseado em marca e estilo',
            'brand_colors': f'#{bg_color} / #{text_color}'
        }
    
    def get_status(self) -> Dict:
        """Retorna status dos geradores"""
        return {
            "primary_strategy": self.primary_strategy,
            "availability": {
                "stability": bool(self.stability_key),
                "huggingface": bool(self.hf_token),
                "mock": True  # Sempre disponível
            },
            "ready": True
        }
    
    def is_real_generation_available(self) -> bool:
        """Verifica se geração real (não-mock) está disponível"""
        return bool(self.stability_key or self.hf_token)

# Instância global
image_generator_clean = ImageGeneratorClean()