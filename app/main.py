import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from groq import AsyncGroq
from app.schemas import ChatRequest, ChatResponse

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError(f"GROQ_API_KEY is missing. Checked: {ENV_PATH}")

app = FastAPI(title="AI Chatbot API", version="0.3.0")
client = AsyncGroq(api_key=api_key)
MODEL = "openai/gpt-oss-120b"
MAX_HISTORY = 20  # Keep system prompt + last 20 messages

# In-memory store: { "session_id": [ {"role": "...", "content": "..."}, ... ] }
sessions: dict[str, list[dict]] = {}

@app.get("/health")
async def health_check():
    return {"status": "online", "model": MODEL, "active_sessions": len(sessions)}

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    if session_id not in sessions:
        return {"session_id": session_id, "messages": []}
    return {"session_id": session_id, "messages": sessions[session_id]}

@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    sessions.pop(session_id, None)
    return {"status": "cleared", "session_id": session_id}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # 1. Initialize session with system prompt if new
    if req.session_id not in sessions:
        sessions[req.session_id] = [
            {"role": "system", "content": req.system_prompt}
        ]

    history = sessions[req.session_id]

    # 2. Append new user message
    history.append({"role": "user", "content": req.message})

    # 3. Sliding window: preserve system prompt (index 0) + last MAX_HISTORY messages
    if len(history) > MAX_HISTORY + 1:
        sessions[req.session_id] = [history[0]] + history[-MAX_HISTORY:]
        history = sessions[req.session_id]

    try:
        completion = await client.chat.completions.create(
            model=MODEL,
            messages=history,
            temperature=req.temperature,
        )

        reply_text = completion.choices[0].message.content or ""
        usage = completion.usage

        # 4. Save assistant reply back into session history
        history.append({"role": "assistant", "content": reply_text})

        # Count user/assistant turns (excluding system prompt)
        turns = (len(history) - 1) // 2

        return ChatResponse(
            session_id=req.session_id,
            reply=reply_text,
            turn_count=turns,
            model=MODEL,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )
    except Exception as e:
        # Roll back the failed user message so history stays valid
        history.pop()
        raise HTTPException(status_code=500, detail=str(e))