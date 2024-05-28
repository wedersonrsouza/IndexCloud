import cv2
import pytesseract
import numpy as np
import easyocr
import torch
torch.backends.nnpack.enabled = False


def extract_text_from_image(image_path):
    # Carregar a imagem usando OpenCV
    # image = cv2.imread(image_path)

    # # Converter a imagem para escala de cinza
    # imagem_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # # Executar OCR na imagem
    # text = pytesseract.image_to_string(imagem_gray)
    
    reader = easyocr.Reader(['pt']) # pass list of languages to recognize
    
    ocr_result = reader.readtext(image_path)
    
    # Extrair apenas os textos
    only_texts = [item[1] for item in ocr_result]

    text = ''
    # Agora a variável 'only_texts' contém apenas os only_texts extraídos
    for value in only_texts:
        text +='\n'+value
        
    # print(text)
    
    return text