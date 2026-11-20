from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User prompt to send to the AI")
    system_prompt: str = Field(
        default="You are a helpful, concise AI assistant.",
        description="System behavior instruction"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class ChatResponse(BaseModel):
    reply: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int