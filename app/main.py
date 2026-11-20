import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from groq import AsyncGroq

# Explicitly load .env from the project root (one level above app/)
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError(f"GROQ_API_KEY is missing. Checked: {ENV_PATH}")

app = FastAPI(title="AI Chatbot API", version="0.1.0")
client = AsyncGroq(api_key=api_key)
MODEL = "openai/gpt-oss-120b"

@app.get("/health")
async def health_check():
    return {"status": "online", "model": MODEL}