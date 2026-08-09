from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from core.llm_engine import LLMEngine
from core.rag_engine import RAGEngine
from core.code_validator import CodeValidator
from core.persona import Persona

app = FastAPI(title="GhostFrame Chat v2", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("[GhostFrame] Initializing engines...")
llm = LLMEngine()
rag = RAGEngine()
validator = CodeValidator()
persona = Persona("Vex")
print(f"[GhostFrame] AI Model loaded: {llm.is_loaded()}")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {
        "status": "GhostFrame Chat v2 operational",
        "persona": persona.name,
        "ai_loaded": llm.is_loaded(),
        "mode": "neural" if llm.is_loaded() else "fallback"
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "ai_loaded": llm.is_loaded(),
        "terminal_tools": rag.check_terminal_tools()
    }

@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Empty message")

    # 1. RAG: Search the net + terminal tools
    context = rag.gather_context(user_msg)

    # 2. AI Generation
    if llm.is_loaded():
        prompt = persona.build_prompt(user_msg, context)
        raw_response = llm.generate(prompt, max_tokens=512)

        if raw_response:
            # 3. Validate code blocks in AI reply
            final_response = validator.validate_code_blocks(raw_response)
            mode = "neural"
        else:
            final_response = persona.fallback_response(user_msg, context)
            mode = "fallback"
    else:
        final_response = persona.fallback_response(user_msg, context)
        mode = "fallback"

    sources_count = len(context.split("\n\n")) if context else 0

    return {
        "response": final_response,
        "mode": mode,
        "persona": persona.name,
        "sources_count": sources_count
    }
