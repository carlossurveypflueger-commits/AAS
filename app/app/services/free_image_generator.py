# app/services/free_image_generator.py
"""
Gerador de imagens usando APIs gratuitas
"""

import os
import asyncio
import httpx
import base64
from typing import List, Dict
from dotenv import load_dotenv
from app.utils.logger import logger

load_dotenv()

class FreeImageGenerator:
    def __init__(self):
        """Inicializa geradores de imagem gratuitos"""
        
        # Stability AI (gratuito com limites)
        self.stability_key = os.getenv("STABILITY_API_KEY")
        
        # HuggingFace (gratuito)
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        
        # Replicate (alguns modelos gratuitos)
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        
        logger.info("[CONFIG] Inicializando geradores de imagem gratuitos")
        logger.info(f"   Stability AI: {'Configurado' if self.stability_key else 'Não configurado'}")
        logger.info(f"   HuggingFace: {'Configurado' if self.hf_token else 'Não configurado'}")
        logger.info(f"   Replicate: {'Configurado' if self.replicate_token else 'Não configurado'}")
        
        # Determinar melhor estratégia
        if self.stability_key:
            self.strategy = "stability"
        elif self.hf_token:
            self.strategy = "huggingface"
        elif self.replicate_token:
            self.strategy = "replicate"
        else:
            self.strategy = "mock"
        
        logger.info(f"[STRATEGY] Estratégia de imagem: {self.strategy.upper()}")
    
    async def generate_product_images(self, product_data: Dict, num_images: int = 3) -> List[Dict]:
        """Gera imagens reais do produto"""
        
        if self.strategy == "stability":
            return await self._generate_with_stability(product_data, num_images)
        elif self.strategy == "huggingface":
            return await self._generate_with_huggingface(product_data, num_images)
        elif self.strategy == "replicate":
            return await self._generate_with_replicate(product_data, num_images)
        else:
            return self._generate_mock_images(product_data, num_images)
    
    async def _generate_with_stability(self, product_data: Dict, num_images: int) -> List[Dict]:
        """Gera imagens usando Stability AI (Stable Diffusion)"""
        images = []
        produto = product_data.get('produto_identificado', 'smartphone')
        
        # Prompts específicos para diferentes estilos
        prompts = [
            f"professional product photography of {produto}, clean white background, studio lighting, commercial quality, high resolution, minimalist",
            f"lifestyle photograph of {produto}, modern workspace, natural lighting, premium setup, Instagram style, professional",
            f"premium {produto} with elegant reflections, dark gradient background, luxury product shot, sophisticated lighting"
        ]
        
        for i, prompt in enumerate(prompts[:num_images]):
            try:
                logger.info(f"[STABILITY] Gerando imagem {i+1}...")
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                        headers={
                            "Authorization": f"Bearer {self.stability_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "text_prompts": [{"text": prompt}],
                            "cfg_scale": 7,
                            "height": 1024,
                            "width": 1024,
                            "samples": 1,
                            "steps": 20
                        },
                        timeout=60
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    image_b64 = result["artifacts"][0]["base64"]
                    
                    images.append({
                        'id': i + 1,
                        'url': f"data:image/png;base64,{image_b64}",
                        'style': ['Profissional', 'Lifestyle', 'Premium'][i],
                        'description': prompt,
                        'generated_by': 'stability_ai',
                        'confidence': 0.92
                    })
                    
                    logger.info(f"[OK] Imagem {i+1} gerada com Stability AI")
                else:
                    logger.info(f"[ERROR] Stability AI erro {response.status_code}")
                    images.append(self._create_fallback_image(product_data, i + 1))
                
            except Exception as e:
                logger.info(f"[ERROR] Stability AI falhou: {e}")
                images.append(self._create_fallback_image(product_data, i + 1))
        
        return images
    
    async def _generate_with_huggingface(self, product_data: Dict, num_images: int) -> List[Dict]:
        """Gera imagens usando HuggingFace (gratuito)"""
        images = []
        produto = product_data.get('produto_identificado', 'smartphone')
        
        # Modelo Stable Diffusion gratuito
        model_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        
        prompts = [
            f"professional product photo of {produto}, white background, studio lighting",
            f"lifestyle photo of {produto}, modern desk, natural light",
            f"premium {produto} with reflections, dark background"
        ]
        
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        for i, prompt in enumerate(prompts[:num_images]):
            try:
                logger.info(f"[HF] Gerando imagem {i+1} com HuggingFace...")
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        model_url,
                        headers=headers,
                        json={"inputs": prompt},
                        timeout=60
                    )
                
                if response.status_code == 200:
                    image_bytes = response.content
                    image_b64 = base64.b64encode(image_bytes).decode()
                    
                    images.append({
                        'id': i + 1,
                        'url': f"data:image/jpeg;base64,{image_b64}",
                        'style': ['Profissional', 'Lifestyle', 'Premium'][i],
                        'description': prompt,
                        'generated_by': 'huggingface_free',
                        'confidence': 0.88
                    })
                    
                    logger.info(f"[OK] Imagem {i+1} gerada com HuggingFace")
                elif response.status_code == 503:
                    logger.info(f"[INFO] HuggingFace modelo carregando, usando fallback")
                    images.append(self._create_fallback_image(product_data, i + 1))
                else:
                    logger.info(f"[ERROR] HuggingFace erro {response.status_code}")
                    images.append(self._create_fallback_image(product_data, i + 1))
                
            except Exception as e:
                logger.info(f"[ERROR] HuggingFace falhou: {e}")
                images.append(self._create_fallback_image(product_data, i + 1))
        
        return images
    
    async def _generate_with_replicate(self, product_data: Dict, num_images: int) -> List[Dict]:
        """Gera imagens usando Replicate"""
        images = []
        produto = product_data.get('produto_identificado', 'smartphone')
        
        try:
            import replicate
            
            prompts = [
                f"professional product photography of {produto}, clean white background, commercial quality",
                f"lifestyle photograph of {produto}, modern setup, natural lighting",
                f"premium {produto} with elegant lighting, luxury product shot"
            ]
            
            for i, prompt in enumerate(prompts[:num_images]):
                try:
                    logger.info(f"[REPLICATE] Gerando imagem {i+1}...")
                    
                    # Usar modelo Stable Diffusion gratuito
                    output = replicate.run(
                        "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
                        input={
                            "prompt": prompt,
                            "width": 1024,
                            "height": 1024,
                            "num_inference_steps": 20,
                            "guidance_scale": 7.5
                        }
                    )
                    
                    if output and len(output) > 0:
                        image_url = output[0] if isinstance(output, list) else output
                        
                        images.append({
                            'id': i + 1,
                            'url': image_url,
                            'style': ['Profissional', 'Lifestyle', 'Premium'][i],
                            'description': prompt,
                            'generated_by': 'replicate',
                            'confidence': 0.90
                        })
                        
                        logger.info(f"[OK] Imagem {i+1} gerada com Replicate")
                    else:
                        raise Exception("Nenhuma imagem retornada")
                
                except Exception as e:
                    logger.info(f"[ERROR] Replicate erro: {e}")
                    images.append(self._create_fallback_image(product_data, i + 1))
            
        except ImportError:
            logger.info("[ERROR] Biblioteca replicate não instalada")
            return self._generate_mock_images(product_data, num_images)
        
        return images
    
    def _create_fallback_image(self, product_data: Dict, image_id: int) -> Dict:
        """Cria imagem fallback individual"""
        marca = product_data.get('marca', 'Produto')
        
        return {
            'id': image_id,
            'url': f"https://via.placeholder.com/1024x1024/0066cc/ffffff?text={marca}+Erro+{image_id}",
            'style': f'Fallback {image_id}',
            'description': f'Fallback para erro na geração',
            'generated_by': 'fallback',
            'confidence': 0.30
        }
    
    def _generate_mock_images(self, product_data: Dict, num_images: int) -> List[Dict]:
        """Imagens mock como último recurso"""
        marca = product_data.get('marca', 'Produto')
        produto = product_data.get('produto_identificado', 'produto')
        
        # Cores por marca
        cores = {
            'Apple': ('1d1d1f', 'f5f5f7'),
            'Samsung': ('1428a0', 'ffffff'),
            'Xiaomi': ('ff6900', 'ffffff'),
            'Premium': ('2c3e50', 'ecf0f1')
        }
        
        cor_bg, cor_texto = cores.get(marca, cores['Premium'])
        
        return [
            {
                'id': i + 1,
                'url': f"https://via.placeholder.com/1024x1024/{cor_bg}/{cor_texto}?text={marca}+{i+1}",
                'style': ['Profissional', 'Lifestyle', 'Premium'][i],
                'description': f"Mockup {['profissional', 'lifestyle', 'premium'][i]} para {produto}",
                'generated_by': 'enhanced_mock',
                'confidence': 0.75
            } for i in range(min(num_images, 3))
        ]
    
    def is_available(self) -> Dict:
        """Status dos geradores de imagem"""
        return {
            "strategy": self.strategy,
            "stability": bool(self.stability_key),
            "huggingface": bool(self.hf_token),
            "replicate": bool(self.replicate_token)
        }

# Instância global
free_image_generator = FreeImageGenerator()