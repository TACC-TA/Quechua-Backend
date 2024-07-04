from fastapi import FastAPI, HTTPException
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

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

@app.post("/translate/")
async def translate(request: TranslationRequest):
    sentence = request.sentence
    input = tokenizer(sentence, return_tensors="pt")
    output = model.generate(input["input_ids"], max_length=40, num_beams=4, early_stopping=True)
    translated_sentence = tokenizer.decode(output[0], skip_special_tokens=True)
    return {"translate": translated_sentence}