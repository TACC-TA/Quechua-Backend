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
    input = tokenizer(sentence, return_tensors="pt")
    output = model.generate(input["input_ids"], max_length=40, num_beams=4, early_stopping=True)
    translated_sentence = tokenizer.decode(output[0], skip_special_tokens=True)
    return {"translate": translated_sentence}

@app.get("/web/titulo")
async def obtenertitulo():
    return webscrappingrecetas()

@app.get("/web/buscar")
async def obtenerReceta(receipt:ReceiptRequest):
    return buscarreceta(receipt.sentence)