import asyncio
import json
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from app.core.config import settings

class AIGenerator:
    def __init__(self):
        # Inicializa clientes de IA apenas se as chaves estão configuradas
        self.openai_client = None
        self.claude_client = None
        
        if settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        if settings.anthropic_api_key:
            self.claude_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    def is_available(self) -> Dict[str, bool]:
        """Verifica quais IAs estão disponíveis"""
        return {
            "openai": self.openai_client is not None,
            "claude": self.claude_client is not None
        }
    
    async def analyze_product_prompt(self, prompt: str) -> Dict:
        """
        Analisa o prompt do usuário e extrai dados do produto
        """
        if not self.claude_client and not self.openai_client:
            return self._generate_mock_analysis(prompt)
        
        analysis_prompt = f"""
        Analise este prompt para criação de campanha publicitária: "{prompt}"
        
        Extraia as seguintes informações e retorne um JSON:
        {{
            "produto_identificado": "nome completo do produto",
            "marca": "marca do produto",
            "categoria": "novo/seminovo/usado",
            "caracteristicas_principais": ["lista", "de", "features"],
            "publico_alvo_sugerido": "descrição do público",
            "tom_de_comunicacao": "casual/formal/jovem/premium",
            "preco_estimado": "faixa de preço estimada",
            "pontos_de_venda": ["vantagens", "principais"],
            "keywords_sugeridas": ["palavra1", "palavra2", "palavra3"]
        }}
        
        Responda APENAS com o JSON, sem explicações adicionais.
        """
        
        try:
            # Tenta usar Claude primeiro (melhor para análise)
            if self.claude_client:
                response = await self.claude_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                result = response.content[0].text
            
            # Fallback para OpenAI
            elif self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": analysis_prompt}],
                    temperature=0.3
                )
                result = response.choices[0].message.content
            
            # Tenta fazer parse do JSON
            try:
                return json.loads(result.strip())
            except json.JSONDecodeError:
                # Se não conseguir parsear, extrai dados básicos
                return self._extract_basic_info(prompt)
                
        except Exception as e:
            print(f"Erro na análise do produto: {e}")
            return self._generate_mock_analysis(prompt)
    
    async def generate_copy_variations(self, product_data: Dict, num_variations: int = 3) -> List[Dict]:
        """
        Gera múltiplas variações de copy para o produto
        """
        if not self.openai_client and not self.claude_client:
            return self._generate_mock_copies(product_data, num_variations)
        
        strategies = [
            "URGÊNCIA - Crie senso de urgência e escassez",
            "BENEFÍCIOS - Foque nas vantagens técnicas", 
            "LIFESTYLE - Mostre como melhora a vida do usuário"
        ]
        
        copies = []
        
        for i, strategy in enumerate(strategies[:num_variations]):
            copy_prompt = f"""
            Crie uma copy para anúncio do Facebook/Instagram sobre: {product_data.get('produto_identificado')}
            
            Estratégia: {strategy}
            Público-alvo: {product_data.get('publico_alvo_sugerido')}
            Tom: {product_data.get('tom_de_comunicacao')}
            
            Requisitos:
            - Máximo 125 caracteres
            - Inclua 1-2 emojis relevantes
            - Call-to-action claro
            - Linguagem brasileira natural
            
            Retorne apenas a copy, sem aspas ou explicações.
            """
            
            try:
                if self.openai_client:
                    response = await self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Você é especialista em copywriting para redes sociais no Brasil."},
                            {"role": "user", "content": copy_prompt}
                        ],
                        temperature=0.8,
                        max_tokens=100
                    )
                    copy_text = response.choices[0].message.content.strip()
                
                elif self.claude_client:
                    response = await self.claude_client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=100,
                        messages=[{"role": "user", "content": copy_prompt}]
                    )
                    copy_text = response.content[0].text.strip()
                
                copies.append({
                    'id': i + 1,
                    'copy': copy_text,
                    'strategy': strategy.split(' - ')[0],
                    'confidence': 0.85 + (i * 0.03),
                    'estimated_ctr': 0.025 + (i * 0.005)
                })
                
            except Exception as e:
                print(f"Erro ao gerar copy {i+1}: {e}")
                # Gera copy mock em caso de erro
                copies.append(self._generate_mock_copy(product_data, i + 1))
        
        return copies
    
    def _generate_mock_analysis(self, prompt: str) -> Dict:
        """Gera análise mock quando IA não está disponível"""
        return {
            "produto_identificado": prompt,
            "marca": "Smartphone",
            "categoria": "novo",
            "caracteristicas_principais": ["Tela HD", "Câmera avançada", "Bateria longa duração"],
            "publico_alvo_sugerido": "Adultos de 25-45 anos interessados em tecnologia",
            "tom_de_comunicacao": "casual",
            "preco_estimado": "R$ 800-1500",
            "pontos_de_venda": ["Ótimo custo-benefício", "Tecnologia avançada", "Garantia estendida"],
            "keywords_sugeridas": ["smartphone", "celular", "tecnologia", "oferta"]
        }
    
    def _generate_mock_copies(self, product_data: Dict, num_variations: int) -> List[Dict]:
        """Gera copies mock quando IA não está disponível"""
        mock_copies = [
            f"🔥 {product_data.get('produto_identificado')} com desconto especial! Aproveite enquanto durarem os estoques!",
            f"✨ Descubra o {product_data.get('produto_identificado')}. Tecnologia que transforma seu dia a dia!",
            f"🚀 LANÇAMENTO: {product_data.get('produto_identificado')}! Seja um dos primeiros a ter essa novidade!"
        ]
        
        return [
            {
                'id': i + 1,
                'copy': mock_copies[i],
                'strategy': ['URGÊNCIA', 'LIFESTYLE', 'LANÇAMENTO'][i],
                'confidence': 0.75,
                'estimated_ctr': 0.028
            }
            for i in range(min(num_variations, len(mock_copies)))
        ]
    
    def _generate_mock_copy(self, product_data: Dict, copy_id: int) -> Dict:
        """Gera uma copy mock individual"""
        return {
            'id': copy_id,
            'copy': f"🔥 {product_data.get('produto_identificado')} disponível! Não perca essa oportunidade única!",
            'strategy': 'URGÊNCIA',
            'confidence': 0.70,
            'estimated_ctr': 0.025
        }
    
    def _extract_basic_info(self, prompt: str) -> Dict:
        """Extrai informações básicas do prompt sem IA"""
        return {
            "produto_identificado": prompt,
            "marca": "Não identificada",
            "categoria": "não especificada",
            "caracteristicas_principais": ["Produto de qualidade"],
            "publico_alvo_sugerido": "Público geral",
            "tom_de_comunicacao": "casual",
            "preco_estimado": "A consultar",
            "pontos_de_venda": ["Boa qualidade", "Preço competitivo"],
            "keywords_sugeridas": prompt.split()
        }

# Instância global do gerador de IA
ai_generator = AIGenerator()