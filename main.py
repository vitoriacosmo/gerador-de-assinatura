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

    # centraliza a assinatura na imagem branca
    x = (largura - output_image.width) // 2
    y = (altura - output_image.height) // 2
    imagem_branca.paste(output_image, (x, y), output_image)


    # texto
    # escreve nome e crm na imagem branca
    draw = ImageDraw.Draw(imagem_branca)
    try:
        font = ImageFont.truetype("arialbd.ttf", 11)
    except:
        font = ImageFont.load_default()
    texto = f"{nome}\nCRM: {crm}"

    # calcula tamanho do texto 
    bbox = draw.textbbox((0, 0), texto, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    # centraliza o texto na imagem
    px = (largura - w) // 2
    py = altura - h - 11

    draw.text((px, py), texto, fill=(0, 0, 0), font=font, align="center", spacing=0.5)

    # salva imagem pronta com nome do médico
    arquivo_final = f"Assinatura - {nome}.png"
    imagem_branca.save(arquivo_final, "PNG")

    imagem_branca.show()
    print(f"Imagem final gerada com sucesso: {arquivo_final}")
