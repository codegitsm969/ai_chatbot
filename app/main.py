import json
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from groq import AsyncGroq
from app.schemas import ChatRequest, ChatResponse

# Resolve project root (one level above app/)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError(f"GROQ_API_KEY is missing. Checked: {ENV_PATH}")

app = FastAPI(title="AI Chatbot API", version="0.4.0")
client = AsyncGroq(api_key=api_key)
MODEL = "openai/gpt-oss-120b"
MAX_HISTORY = 20

# In-memory session store: {session_id: [{"role": ..., "content": ...}]}
sessions: dict[str, list[dict]] = {}

# Support frontend/ either in project root (ai_chatbot/frontend) or inside app/ (ai_chatbot/app/frontend)
ROOT_FRONTEND = BASE_DIR / "frontend"
APP_FRONTEND = Path(__file__).resolve().parent / "frontend"
FRONTEND_DIR = ROOT_FRONTEND if ROOT_FRONTEND.exists() else APP_FRONTEND

if not FRONTEND_DIR.exists():
    raise RuntimeError(f"frontend directory not found at {ROOT_FRONTEND} or {APP_FRONTEND}")

app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")


def get_or_create_session(session_id: str, system_prompt: str) -> list[dict]:
    if session_id not in sessions:
        sessions[session_id] = [{"role": "system", "content": system_prompt}]
    return sessions[session_id]


def trim_history(session_id: str) -> list[dict]:
    history = sessions[session_id]
    if len(history) > MAX_HISTORY + 1:
        sessions[session_id] = [history[0]] + history[-MAX_HISTORY:]
    return sessions[session_id]


@app.get("/")
async def serve_ui():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
async def health_check():
    return {"status": "online", "model": MODEL, "active_sessions": len(sessions)}


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    return {"session_id": session_id, "messages": sessions.get(session_id, [])}


@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    sessions.pop(session_id, None)
    return {"status": "cleared", "session_id": session_id}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    history = get_or_create_session(req.session_id, req.system_prompt)
    history.append({"role": "user", "content": req.message})
    history = trim_history(req.session_id)

    try:
        completion = await client.chat.completions.create(
            model=MODEL,
            messages=history,
            temperature=req.temperature,
        )
        reply_text = completion.choices[0].message.content or ""
        usage = completion.usage
        history.append({"role": "assistant", "content": reply_text})

        return ChatResponse(
            session_id=req.session_id,
            reply=reply_text,
            turn_count=(len(history) - 1) // 2,
            model=MODEL,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )
    except Exception as e:
        if history and history[-1]["role"] == "user":
            history.pop()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    history = get_or_create_session(req.session_id, req.system_prompt)
    history.append({"role": "user", "content": req.message})
    history = trim_history(req.session_id)

    async def event_generator():
        full_reply = []
        try:
            stream = await client.chat.completions.create(
                model=MODEL,
                messages=history,
                temperature=req.temperature,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full_reply.append(delta)
                    yield f"data: {json.dumps({'token': delta})}\n\n"

            history.append({"role": "assistant", "content": "".join(full_reply)})
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            if history and history[-1]["role"] == "user":
                history.pop()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")