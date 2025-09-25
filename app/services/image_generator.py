import asyncio
import requests
import base64
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import io
import os

class ImageGenerator:
    def __init__(self):
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        print("Image Generator inicializado")
    
    def is_available(self) -> bool:
        """Verifica se a geração de imagens está disponível"""
        return bool(self.replicate_token)
    
    async def generate_product_mockups(self, product_data: Dict, num_images: int = 3) -> List[Dict]:
        """Gera mockups de produto usando diferentes estilos"""
        
        produto = product_data.get('produto_identificado', 'smartphone')
        marca = product_data.get('marca', 'Generic')
        categoria = product_data.get('categoria', 'novo')
        
        # Estilos diferentes para os mockups
        styles = [
            {
                "name": "Minimalista",
                "description": f"Foto profissional de {produto} em fundo branco limpo, iluminação de estúdio, alta qualidade, minimalista",
                "mood": "clean_minimal"
            },
            {
                "name": "Lifestyle",
                "description": f"Foto lifestyle de {produto} em mesa de madeira moderna com café e notebook, ambiente aconchegante",
                "mood": "lifestyle_cozy"
            },
            {
                "name": "Premium",
                "description": f"Foto premium de {produto} com reflexos elegantes, fundo gradiente escuro, luxuoso e sofisticado",
                "mood": "luxury_premium"
            }
        ]
        
        images = []
        
        for i, style in enumerate(styles[:num_images]):
            if self.replicate_token:
                # Tentar gerar com Replicate (IA real)
                image_data = await self._generate_with_replicate(style["description"])
            else:
                # Gerar placeholder personalizado
                image_data = await self._generate_placeholder(produto, marca, style["name"])
            
            images.append({
                'id': i + 1,
                'url': image_data['url'],
                'style': style["name"],
                'description': style["description"],
                'mood': style["mood"],
                'generated_by': image_data['method'],
                'confidence': 0.85 + (i * 0.03),
                'download_ready': image_data.get('download_ready', True)
            })
        
        return images
    
    async def _generate_with_replicate(self, prompt: str) -> Dict:
        """Gera imagem usando Replicate/Flux (IA real)"""
        try:
            import replicate
            
            # Usar Flux para gerar imagem realista de produto
            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input={
                    "prompt": f"Professional product photography, {prompt}, commercial quality, high resolution, 4K",
                    "width": 1024,
                    "height": 1024,
                    "num_outputs": 1,
                    "num_inference_steps": 4
                }
            )
            
            if output and len(output) > 0:
                return {
                    'url': output[0],
                    'method': 'replicate_flux',
                    'download_ready': True
                }
            else:
                return await self._generate_placeholder("Produto", "Premium", "AI")
                
        except Exception as e:
            print(f"Erro ao gerar com Replicate: {e}")
            return await self._generate_placeholder("Produto", "Premium", "Fallback")
    
    async def _generate_placeholder(self, produto: str, marca: str, style: str) -> Dict:
        """Gera placeholder visual personalizado"""
        try:
            # Criar imagem placeholder com informações do produto
            width, height = 1024, 1024
            
            # Cores baseadas na marca
            colors = {
                'Apple': ('#1d1d1f', '#f5f5f7', '#007aff'),
                'Samsung': ('#1428a0', '#ffffff', '#ff6900'),
                'Xiaomi': ('#ff6900', '#ffffff', '#34495e'),
                'Motorola': ('#0066cc', '#ffffff', '#e74c3c')
            }
            
            bg_color, text_color, accent_color = colors.get(marca, ('#2c3e50', '#ffffff', '#3498db'))
            
            # Criar imagem
            img = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Tentar carregar fonte (fallback para fonte padrão)
            try:
                font_large = ImageFont.truetype("arial.ttf", 60)
                font_medium = ImageFont.truetype("arial.ttf", 40)
                font_small = ImageFont.truetype("arial.ttf", 30)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Desenhar elementos do mockup
            # Título
            draw.text((width//2, 200), marca, fill=text_color, font=font_large, anchor="mm")
            
            # Produto (texto quebrado se muito longo)
            produto_lines = self._wrap_text(produto, font_medium, width - 100)
            y_offset = 300
            for line in produto_lines:
                draw.text((width//2, y_offset), line, fill=text_color, font=font_medium, anchor="mm")
                y_offset += 50
            
            # Estilo
            draw.text((width//2, y_offset + 50), f"Estilo: {style}", fill=accent_color, font=font_small, anchor="mm")
            
            # Retângulo decorativo (simula produto)
            rect_width, rect_height = 300, 400
            rect_x = (width - rect_width) // 2
            rect_y = y_offset + 120
            draw.rounded_rectangle(
                [rect_x, rect_y, rect_x + rect_width, rect_y + rect_height],
                radius=20,
                fill=accent_color,
                outline=text_color,
                width=3
            )
            
            # Texto no "produto"
            draw.text((width//2, rect_y + rect_height//2), "PREVIEW", fill=bg_color, font=font_medium, anchor="mm")
            
            # Converter para base64 para usar como data URL
            buffer = io.BytesIO()
            img.save(buffer, format='PNG', quality=95)
            img_data = buffer.getvalue()
            img_b64 = base64.b64encode(img_data).decode()
            
            return {
                'url': f"data:image/png;base64,{img_b64}",
                'method': 'placeholder_generated',
                'download_ready': True
            }
            
        except Exception as e:
            print(f"Erro ao gerar placeholder: {e}")
            # Fallback simples
            return {
                'url': f"https://via.placeholder.com/1024x1024/2c3e50/ffffff?text={produto.replace(' ', '+')}",
                'method': 'placeholder_simple',
                'download_ready': True
            }
    
    def _wrap_text(self, text: str, font, max_width: int) -> List[str]:
        """Quebra texto em linhas para caber na imagem"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Usar aproximação se não conseguir medir fonte
            if len(test_line) * 20 < max_width:  # Aproximação
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines or [text]
    
    async def generate_ad_creatives(self, product_data: Dict, copies: List[Dict]) -> List[Dict]:
        """Combina imagens com copies para criar criativos completos"""
        
        # Gerar imagens do produto
        images = await self.generate_product_mockups(product_data, 3)
        
        # Combinar imagens com copies
        creatives = []
        
        for i, (image, copy) in enumerate(zip(images, copies)):
            creative = {
                'id': i + 1,
                'image': image,
                'copy': copy,
                'combined_confidence': (image['confidence'] + copy.get('confidence', 0.8)) / 2,
                'creative_type': f"{image['style']} + {copy.get('estrategia', 'Standard')}",
                'preview_ready': True,
                'estimated_performance': {
                    'ctr': copy.get('ctr_estimado', '2.5%'),
                    'engagement_score': round((image['confidence'] + copy.get('confidence', 0.8)) * 50, 1),
                    'visual_appeal': image['confidence'] * 100
                }
            }
            creatives.append(creative)
        
        return creatives

# Instância global
image_generator = ImageGenerator()