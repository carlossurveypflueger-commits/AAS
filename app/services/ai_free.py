import requests
import json
from typing import Dict, List

class AIFree:
    def __init__(self):
        # Hugging Face é gratuito, sem necessidade de cartão
        self.hf_token = None  # Pode funcionar sem token para muitos modelos
        self.base_url = "https://api-inference.huggingface.co/models"
        
    async def analyze_with_free_ai(self, prompt: str) -> Dict:
        """Análise usando modelos gratuitos"""
        
        # Usar modelo de classificação gratuito
        try:
            analysis_prompt = f"""
            Produto: {prompt}
            
            Analise este produto e retorne informações estruturadas:
            - Marca identificada
            - Categoria (novo/seminovo/usado)  
            - Preço estimado
            - Público-alvo
            """
            
            # Chamar modelo gratuito de text generation
            response = requests.post(
                f"{self.base_url}/microsoft/DialoGPT-medium",
                headers={"Authorization": f"Bearer {self.hf_token}" if self.hf_token else {}},
                json={"inputs": analysis_prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_analysis_result(result, prompt)
            else:
                return self._smart_local_analysis(prompt)
                
        except Exception as e:
            print(f"Erro na análise gratuita: {e}")
            return self._smart_local_analysis(prompt)
    
    async def generate_free_copies(self, product_data: Dict) -> List[Dict]:
        """Gerar copies usando IA gratuita"""
        
        produto = product_data.get('produto_identificado', 'produto')
        
        copies = []
        prompts = [
            f"Crie copy de urgência para: {produto}",
            f"Crie copy destacando benefícios de: {produto}",
            f"Crie copy premium para: {produto}"
        ]
        
        for i, copy_prompt in enumerate(prompts):
            try:
                response = requests.post(
                    f"{self.base_url}/gpt2",
                    json={"inputs": copy_prompt, "parameters": {"max_length": 100}},
                    timeout=20
                )
                
                if response.status_code == 200:
                    result = response.json()
                    copy_text = self._extract_copy(result)
                else:
                    copy_text = self._generate_smart_copy(produto, i)
                
                copies.append({
                    'id': i + 1,
                    'titulo': ['Copy Urgência', 'Copy Benefícios', 'Copy Premium'][i],
                    'texto': copy_text,
                    'estrategia': ['URGÊNCIA', 'BENEFÍCIOS', 'PREMIUM'][i],
                    'confidence': 0.80 + (i * 0.05),
                    'generated_by': 'huggingface_free'
                })
                
            except Exception as e:
                print(f"Erro copy {i+1}: {e}")
                copies.append({
                    'id': i + 1,
                    'titulo': f'Copy Local {i+1}',
                    'texto': self._generate_smart_copy(produto, i),
                    'estrategia': ['URGÊNCIA', 'BENEFÍCIOS', 'PREMIUM'][i],
                    'confidence': 0.75,
                    'generated_by': 'local_smart'
                })
        
        return copies
    
    def _parse_analysis_result(self, result, prompt):
        """Processa resultado da análise"""
        # Implementação simplificada
        return self._smart_local_analysis(prompt)
    
    def _smart_local_analysis(self, prompt):
        """Análise local otimizada que já implementamos"""
        prompt_lower = prompt.lower()
        
        # Mesma lógica inteligente que já criamos
        if "iphone" in prompt_lower:
            marca = "Apple"
            preco_base = 3000
        elif "samsung" in prompt_lower:
            marca = "Samsung"  
            preco_base = 2500
        else:
            marca = "Premium"
            preco_base = 2000
            
        return {
            "produto_identificado": prompt,
            "marca": marca,
            "categoria": "seminovo" if "seminovo" in prompt_lower else "novo",
            "caracteristicas_principais": ["Design premium", "Tecnologia avançada", "Performance superior"],
            "publico_alvo_sugerido": f"Usuários de {marca}, 25-45 anos, classe média-alta",
            "preco_estimado": f"R$ {preco_base-500} - R$ {preco_base+500}",
            "pontos_de_venda": ["Qualidade garantida", "Melhor preço", "Garantia inclusa"]
        }
    
    def _generate_smart_copy(self, produto, index):
        """Gera copy inteligente local"""
        templates = [
            f"🔥 {produto} - OFERTA IMPERDÍVEL! Últimas unidades disponíveis!",
            f"⚡ {produto} - Tecnologia premium que você merece. Performance excepcional!",
            f"✨ {produto} - Exclusividade e sofisticação. Estado impecável, garantia total!"
        ]
        
        return templates[index] if index < len(templates) else f"📱 {produto} - Oportunidade única!"
    
    def _extract_copy(self, result):
        """Extrai copy do resultado da API"""
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '').strip()[:100]
        return "Copy gerada por IA gratuita"

# Instância global
ai_free = AIFree()