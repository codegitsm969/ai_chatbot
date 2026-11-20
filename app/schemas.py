from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str = Field(
        default="default",
        min_length=1,
        description="Unique ID to track conversation history across turns"
    )
    message: str = Field(..., min_length=1, description="User prompt")
    system_prompt: str = Field(
        default="You are a helpful, concise AI assistant.",
        description="System behavior instruction (applied when starting a new session)"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    turn_count: int
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int