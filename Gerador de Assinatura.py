from rembg import remove, new_session
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
import io
from tkinter import Tk, filedialog

session = new_session("isnet-general-use")  # modelo

while True:
    nome = input("Digite o nome do médico com Dr./Dra.: ")
    crm = input("Digite o CRM com estado: ")

    add_frase = input("Adicionar frase a mais? (S/N): ").strip().lower()
    frase_extra = ""
    if add_frase == "s":
        frase_extra = input("Digite a frase que deseja adicionar: ")

    Tk().withdraw()
    img = filedialog.askopenfilename(title="Selecione a imagem da assinatura: ")
    if not img:
        print("Nenhuma imagem selecionada.")
        break

    # lê e remove fundo
    with open(img, 'rb') as input_file:
        input_data = input_file.read()
    output_data = remove(input_data, session=session)
    output_image = Image.open(io.BytesIO(output_data)).convert("RGBA")

    # aumenta contraste 
    enhancer = ImageEnhance.Contrast(output_image)
    output_image = enhancer.enhance(3.0)
    
    # aumenta nitidez 
    output_image = output_image.filter(ImageFilter.SHARPEN)

    # limpa pixels fracos e aplica preto
    r, g, b, a = output_image.split()
    a = a.point(lambda i: 0 if i < 25 else 250)  # 98% de opacidade
    preto = Image.new("RGBA", output_image.size, (0, 0, 0, 250))
    output_image = Image.composite(preto, Image.new("RGBA", output_image.size, (0,0,0,0)), a)

    # correção do erro onde cortava cantos da imagem
    bbox = output_image.getbbox()
    if bbox:
        # adiciona margem de 10 pixels em cada lado
        margem = 10
        bbox_expandido = (
            max(0, bbox[0] - margem),
            max(0, bbox[1] - margem),
            min(output_image.width, bbox[2] + margem),
            min(output_image.height, bbox[3] + margem)
        )
        output_image = output_image.crop(bbox_expandido)

    # configura fonte
    try:
        font = ImageFont.truetype("arialbd.ttf", 11)
    except:
        font = ImageFont.load_default()

    # monta texto completo
    texto = f"{nome}\nCRM: {crm}"
    if frase_extra:
        texto += f"\n{frase_extra}"

    # calcula tamanho do texto
    temp_img = Image.new("RGBA", (1,1))
    draw_temp = ImageDraw.Draw(temp_img)
    bbox_texto = draw_temp.multiline_textbbox((0,0), texto, font=font, spacing=1)
    altura_texto = bbox_texto[3] - bbox_texto[1]
    largura_texto = bbox_texto[2] - bbox_texto[0]

    # dimensões fixas da imagem final
    largura_final = 480
    altura_final = 120
    
    # área disponível para a assinatura
    margem_horizontal = 40
    margem_superior = 10
    margem_inferior = 5
    espaco_texto = altura_texto + margem_inferior
    
    # limite máximo para a assinatura (60% da largura e 50% da altura disponível)
    max_largura_assinatura = min(280, largura_final - margem_horizontal)  # máximo 280px
    max_altura_assinatura = min(50, altura_final - margem_superior - espaco_texto - margem_inferior)  # máximo 50px
    
    # redimensiona assinatura proporcionalmente
    largura_img, altura_img = output_image.size
    proporcao = min(max_largura_assinatura / largura_img, max_altura_assinatura / altura_img)
    
    # correção do erro onde não redimensionava a imagem seja pequena
    nova_largura = int(largura_img * proporcao)
    nova_altura = int(altura_img * proporcao)
    output_image = output_image.resize((nova_largura, nova_altura), Image.LANCZOS)
    
    # tira um pouco da suavidade a assinatura após redimensionar
    output_image = output_image.filter(ImageFilter.GaussianBlur(0.6))
    
    # mantém contraste mais escuro
    enhancer_final = ImageEnhance.Contrast(output_image)
    output_image = enhancer_final.enhance(1.2)
    
    # escurece ainda mais, mexe com o brilho
    enhancer_brilho = ImageEnhance.Brightness(output_image)
    output_image = enhancer_brilho.enhance(0.85)
    
    # cria imagem final com tamanho fixo
    imagem_final = Image.new("RGBA", (largura_final, altura_final), "white")
    draw = ImageDraw.Draw(imagem_final)
    
    # calcula altura total do conteúdo (assinatura + texto)
    altura_conteudo = nova_altura + margem_inferior + altura_texto
    
    # centraliza verticalmente
    y_inicio_assinatura = (altura_final - altura_conteudo) // 2
    x_inicio_assinatura = (largura_final - nova_largura) // 2
    
    # cola assinatura
    imagem_final.paste(output_image, (x_inicio_assinatura, y_inicio_assinatura), output_image)
    
    # cola texto abaixo da assinatura, centralizado
    x_texto = (largura_final - largura_texto) // 2
    y_texto = y_inicio_assinatura + nova_altura + margem_inferior
    draw.multiline_text((x_texto, y_texto), texto, fill=(0,0,0), font=font, align="center", spacing=1)

    # salva
    arquivo_final = f"Assinatura - {nome}.png"
    imagem_final.save(arquivo_final, "PNG")
    imagem_final.show()
    print(f"Assinatura gerada: {arquivo_final}")