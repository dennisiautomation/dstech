from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Criar uma imagem 200x100 com fundo branco
width, height = 200, 100
img = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(img)

# Desenhar um retângulo azul
draw.rectangle([(20, 20), (180, 80)], fill='#4b6cb7')

# Adicionar texto
try:
    # Tentar usar uma fonte padrão
    font = ImageFont.truetype("Arial", 24)
    draw.text((40, 35), "Lavanderia", fill="white", font=font)
except:
    # Se não encontrar a fonte, usar a fonte padrão
    draw.text((40, 35), "Lavanderia", fill="white")

# Salvar a imagem
img.save('logo.png')
print("Logo criado com sucesso!")
