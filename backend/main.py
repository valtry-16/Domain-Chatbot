from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from router import stream_ollama

# 🔹 Tone control ONLY for chat
CHAT_TONE_PROMPT = (
    "You are a friendly, casual AI assistant. "
    "Speak naturally like a human friend. "
    "Keep responses warm and conversational. "
    "Avoid sounding robotic."
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    domain: str
    message: str

@app.get("/")
def root():
    return {"status": "Backend running"}

@app.post("/chat/stream")
def chat_stream(req: ChatRequest):

    # ✅ Apply tone ONLY for chat domain
    if req.domain == "chat":
        final_prompt = f"{CHAT_TONE_PROMPT}\n\nUser: {req.message}"
    else:
        # 🔥 coding & exam remain untouched
        final_prompt = req.message

    def generator():
        for chunk in stream_ollama(req.domain, final_prompt):
            yield chunk

    return StreamingResponse(generator(), media_type="text/plain")