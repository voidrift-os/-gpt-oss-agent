from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class PromptRequest(BaseModel):
    prompt: str

class TextResponse(BaseModel):
    text: str

@app.post("/generate", response_model=TextResponse)
async def generate(request: PromptRequest):
    prompt = request.prompt
    # Placeholder: Replace with real model inference (e.g., llama-cpp-python)
    # Example:
    # from llama_cpp import Llama
    # llm = Llama(model_path="/models/llama.bin")
    # output = llm(prompt)
    # text = output["choices"][0]["text"]
    text = f"Echo: {prompt}"
    logging.info(f"Prompt: {prompt} | Response: {text}")
    return {"text": text}

@app.get("/health")
async def health():
    return {"status": "ok"}
