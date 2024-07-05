from fastapi import FastAPI, HTTPException
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = FastAPI()

# Lista de orígenes permitidos para CORS
origins = [
    "http://localhost:3000",  # Ajusta esto a los orígenes que necesites permitir
    "http://127.0.0.1:3000",
]

# Configuración del middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Orígenes permitidos
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Métodos permitidos
    allow_headers=["X-Requested-With", "Content-Type"],  # Encabezados permitidos
)

model_name = 'hackathon-pln-es/t5-small-finetuned-spanish-to-quechua'
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)


import requests

url = "https://l34fzzlj-8000.brs.devtunnels.ms/"


class TranslationRequest(BaseModel):
    sentence: str

class ReceiptRequest(BaseModel):
    sentence: str


def webscrappingrecetas():
    driver = webdriver.Chrome()
    driver.get('https://www.recetasnestle.com.pe')
    titulo =driver.title
    print("Título de la página:", driver.title)
    driver.quit()
    return titulo

def buscarreceta(receta):
    driver = webdriver.Chrome()
    driver.get('https://www.recetasnestle.com.pe')

    search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'edit-search-field'))
        )
    search_box.send_keys(receta)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)
        
        # Localiza el botón "No preguntar otra vez" y haz clic en él
    no_preguntar_otra_vez_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-webpush-button-cancel]'))
    )
    no_preguntar_otra_vez_button.click()
        
    primera_imagen = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.pageSearch__list .recipeCard__image img'))
        )
    primera_imagen.click()
    titulo =driver.title
     
    WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.recipeDetail__stepItem div'))
        )

    pasos_receta = driver.find_elements(By.CSS_SELECTOR, '.recipeDetail__stepItem div')


    pasos = [paso.text.strip() for paso in pasos_receta]
    pasos.insert(0, f'La receta de {titulo.split("|")[0].strip()} es:')
    driver.quit()
    return pasos 

@app.post("/translate/")
async def translate(request: TranslationRequest):
    sentence = request.sentence
    url = "https://l34fzzlj-8000.brs.devtunnels.ms/translate/"
    # Construye la URL completa con el parámetro de consulta
    full_url = f"{url}?text={sentence}"

# Realiza una solicitud GET al endpoint
    response = requests.get(full_url)
    
    print(response.json()) 
    
    return {"translate": "hola"}

@app.get("/web/titulo")
async def obtenertitulo():
    return webscrappingrecetas()

@app.get("/web/buscar")
async def obtenerReceta(receipt:ReceiptRequest):
    receipe = buscarreceta(receipt.sentence)
    texto_concatenado = ""
    for _ in receipe:
        texto_concatenado += _ + " "
    
    print(texto_concatenado)    
    url = "https://l34fzzlj-8000.brs.devtunnels.ms/translate/"
        # Construye la URL completa con el parámetro de consulta
    full_url = f"{url}?text={texto_concatenado}"
    response = requests.get(full_url)
        
        # Verifica si la respuesta fue exitosa y es tipo JSON antes de decodificar
    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
        try:
            respuesta = response.json()
        except ValueError:
            # Maneja el caso donde la respuesta no puede ser decodificada como JSON
            print("La respuesta no es un JSON válido.")
    else:
        # Maneja el caso de respuestas no exitosas o no JSON
        print(f"Error en la solicitud: Código de estado {response.status_code}, Tipo de contenido {response.headers.get('Content-Type')}")
    
    return {"translate": respuesta}

