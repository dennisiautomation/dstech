"""
Script para gerar um logo simples para o dashboard
"""
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import os

# Criar uma imagem simples com texto
def create_logo():
    # Criar uma imagem com fundo branco
    img = Image.new('RGB', (200, 100), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Desenhar um retângulo azul
    d.rectangle([(0, 0), (200, 100)], fill=(0, 98, 204))
    
    # Adicionar texto
    try:
        # Tentar usar uma fonte do sistema
        font = ImageFont.truetype("Arial", 24)
    except:
        # Se não encontrar, usar a fonte padrão
        font = ImageFont.load_default()
    
    d.text((20, 40), "Lavanderia", fill=(255, 255, 255), font=font)
    
    # Salvar a imagem
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.png')
    img.save(img_path)
    print(f"Logo criado em: {img_path}")
    
    return img_path

if __name__ == "__main__":
    create_logo()
