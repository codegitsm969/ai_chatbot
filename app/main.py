import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from groq import AsyncGroq
from app.schemas import ChatRequest, ChatResponse

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

load_dotenv(dotenv_path=ENV_PATH, override=True)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError(f"GROQ_API_KEY is missing. Checked: {ENV_PATH}")

app = FastAPI(title="AI Chatbot API", version="0.2.0")
client = AsyncGroq(api_key=api_key)
MODEL = "openai/gpt-oss-120b"

@app.get("/health")
async def health_check():
    return {"status": "online", "model": MODEL}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        completion = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": req.system_prompt},
                {"role": "user", "content": req.message},
            ],
            temperature=req.temperature,
        )

        reply_text = completion.choices[0].message.content or ""
        usage = completion.usage

        return ChatResponse(
            reply=reply_text,
            model=MODEL,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))