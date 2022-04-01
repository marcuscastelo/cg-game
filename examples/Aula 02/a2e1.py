from PIL import Image
import requests
from io import BytesIO
from IPython.display import display  # to display images
url_imagem = 'http://imagens.usp.br/wp-content/uploads/13072012frutasfotoMarcosSantos008.jpg'
# %%
# lendo a imagem
response = requests.get(url_imagem)
img = Image.open(BytesIO(response.content))
# exibindo a imagem
display(img)
# %%
# informacoes da imagem
largura = img.size[0]
altura = img.size[1]
# obtem a matriz de pixeis da imagem
matrix_pixeis = img.load()
for i in range(largura):
    for j in range(altura):
        pixel = matrix_pixeis[i, j]  # tomamos o pixel na posicao i e j
        R = pixel[0]
        G = pixel[1]
        B = pixel[2]
        # Regra de clareamento: se a componente R é maior do que 32, então clarear o pixel (experimente ctiar outras)
        if R > 32:
            R = 2*R
            G = 2*G
            B = 2*B
        novo_pixel = (R, G, B)
        matrix_pixeis[i, j] = novo_pixel
# exibindo a imagem
display(img)
# %%
"""Maçã Verde"""
img = Image.open(BytesIO(response.content))
matrix_pixeis = img.load()
for i in range(largura):
    for j in range(altura):
        pixel = matrix_pixeis[i, j]
        R = pixel[0]
        G = pixel[1]
        B = pixel[2]
        if R > G:
            R, G = G, R
        novo_pixel = (R, G, B)
        matrix_pixeis[i, j] = novo_pixel
display(img)
# %%
"""Tons de cinza"""
img = Image.open(BytesIO(response.content))
matrix_pixeis = img.load()
for i in range(largura):
    for j in range(altura):
        pixel = matrix_pixeis[i, j]
        R = pixel[0]
        G = pixel[1]
        B = pixel[2]
        M = (R+G+B)//3
        novo_pixel = (M, M, M)
        matrix_pixeis[i, j] = novo_pixel
display(img)
