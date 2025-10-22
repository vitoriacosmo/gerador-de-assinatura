from rembg import remove, new_session
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import datetime, io
from tkinter import Tk, filedialog

session = new_session("isnet-general-use")  # modelo 

while True:
    
    nome = input("Digite o nome do médico com Dr./Dra.: ")
    crm = input("Digite o CRM com estado: ")

    # imagem
    # abre imagem
    Tk().withdraw()
    img = filedialog.askopenfilename(title="Selecione a imagem: ")

    # lê a imagem em bytes
    with open(img, 'rb') as input_file:
        input_data = input_file.read()

    # remove o fundo
    output_data = remove(input_data, session=session)
    output_image = Image.open(io.BytesIO(output_data)).convert("RGBA")

    # suaviza bordas
    output_image = output_image.filter(ImageFilter.GaussianBlur(0.5))

    # remove pixels meio transparentes
    r, g, b, a = output_image.split()
    a = a.point(lambda i: 0 if i < 15 else i)
    output_image = Image.merge("RGBA", (r, g, b, a))

    # transparência opcional
    transparencia = 230
    a = a.point(lambda i: int(i * (transparencia / 255)))
    output_image = Image.merge("RGBA", (r, g, b, a))

    # cria imagem branca no tamanho da assinatura padrão
    largura = 480
    altura = 120
    imagem_branca = Image.new('RGBA', (largura, altura), 'white')

    # texto
    # define fonte e draw
    try:
        font = ImageFont.truetype("arialbd.ttf", 11)
    except:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(imagem_branca)

    texto = f"{nome}\nCRM: {crm}"

    # margem
    margem_horizontal = 20
    margem_superior = 10
    margem_texto = 5

    # calcula tamanho do texto
    bbox_texto = draw.multiline_textbbox((0,0), texto, font=font, spacing=1)
    altura_texto = bbox_texto[3] - bbox_texto[1]

    # define altura da assinatura
    altura_disponivel = altura - altura_texto - margem_texto - margem_superior
    max_largura = largura - (margem_horizontal * 2)
    max_altura = altura_disponivel

    # redimensiona assinatura proporcionalmente
    largura_img, altura_img = output_image.size
    if largura_img > max_largura or altura_img > max_altura:
        proporcao = min(max_largura / largura_img, max_altura / altura_img)
        nova_largura = int(largura_img * proporcao)
        nova_altura = int(altura_img * proporcao)
        output_image = output_image.resize((nova_largura, nova_altura), Image.LANCZOS)

    # centraliza assinatura na horizontal
    x = (largura - output_image.width) // 2
    y = margem_superior
    imagem_branca.paste(output_image, (x, y), output_image)

    # centraliza texto abaixo da assinatura
    px = (largura - (bbox_texto[2]-bbox_texto[0])) // 2
    py = altura - altura_texto - 5
    draw.multiline_text((px, py), texto, fill=(0,0,0), font=font, align="center", spacing=0.75)

    # salva imagem pronta com nome do médico
    arquivo_final = f"Assinatura - {nome}.png"
    imagem_branca.save(arquivo_final, "PNG")

    imagem_branca.show()
    print(f"Imagem final gerada com sucesso: {arquivo_final}")
