"""
Vercel Serverless Deployment - FastAPI AI Todo Chatbot
Clean, fixed & production-ready with SQLite persistence
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.task import Task
from src.services.task_repository import TaskRepository

# =========================
# App Initialization
# =========================
app = FastAPI(
    title="AI Todo Chatbot API",
    version="2.1.0",
    description="Serverless AI-powered Todo Chatbot with SQLite Persistence, Multilingual Support, and Conversation Context"
)

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Database Initialization
# =========================
# Initialize TaskRepository with SQLite database
db_path = Path(__file__).parent.parent / "data" / "tasks.db"
task_repo = TaskRepository(str(db_path))

# =========================
# Models
# =========================
class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "en"

# =========================
# OpenAI Client Initialization
# =========================
def get_openai_client():
    """Get OpenAI client with API key validation."""
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing in environment variables")

    return OpenAI(api_key=api_key)

# =========================
# Language Detection (FR-008)
# =========================
def detect_language(text: str) -> str:
    """
    Detect the language of input text using OpenAI API.
    Returns ISO 639-1 language code (e.g., 'en', 'es', 'fr').
    """
    try:
        client = get_openai_client()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a language detection expert. Respond with ONLY the ISO 639-1 language code (2 letters) of the input text. Examples: en, es, fr, ar, hi, de, zh"},
                {"role": "user", "content": f"Detect language: {text}"}
            ],
            max_tokens=10,
            temperature=0.0
        )

        lang_code = response.choices[0].message.content.strip().lower()
        # Validate it's a 2-letter code
        if len(lang_code) == 2:
            return lang_code
        return "en"  # Default to English if invalid

    except Exception as e:
        print(f"Language detection error: {e}")
        return "en"  # Default to English on error

# =========================
# Translation Service (FR-009)
# =========================
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source language to target language using OpenAI.

    Args:
        text: Text to translate
        source_lang: Source language code (e.g., 'es')
        target_lang: Target language code (e.g., 'en')

    Returns:
        Translated text
    """
    if source_lang == target_lang:
        return text  # No translation needed

    try:
        client = get_openai_client()

        lang_names = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French',
            'ar': 'Arabic', 'hi': 'Hindi', 'de': 'German',
            'zh': 'Mandarin Chinese', 'ur': 'Urdu'
        }

        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text from {source_name} to {target_name}. Preserve the meaning and tone. Respond with ONLY the translation."},
                {"role": "user", "content": text}
            ],
            max_tokens=200,
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text on error

# =========================
# OpenAI helper (with translation support)
# =========================
def ask_openai(message: str, language: str = "en") -> str:
    """
    Ask OpenAI for help with a message, with optional translation.

    Args:
        message: User message (in any language)
        language: Target language for response

    Returns:
        AI response in target language
    """
    try:
        client = get_openai_client()

        # Translate to English if needed
        message_en = message
        if language != "en":
            message_en = translate_text(message, language, "en")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI Todo assistant. Be concise and friendly."},
                {"role": "user", "content": message_en}
            ],
            max_tokens=120,
            temperature=0.6
        )

        response_en = response.choices[0].message.content

        # Translate response back if needed
        if language != "en":
            return translate_text(response_en, "en", language)

        return response_en

    except Exception as e:
        error_msg = f"❌ OpenAI Error: {e}"
        if language != "en":
            try:
                return translate_text(error_msg, "en", language)
            except:
                pass
        return error_msg

# =========================
# Helper: Convert Task to dict
# =========================
def task_to_dict(task: Task) -> dict:
    """Convert Task object to frontend-compatible dict."""
    return {
        "id": task.id,
        "title": task.description,
        "completed": task.status == "completed"
    }

# =========================
# Conversation Context (FR-014)
# =========================
conversation_history: List[dict] = []
MAX_CONTEXT_SIZE = 5

def add_to_context(user_message: str, bot_response: str, language: str = "en"):
    """Track conversation context (last 5 exchanges)."""
    global conversation_history

    conversation_history.append({
        "user": user_message,
        "bot": bot_response,
        "language": language,
        "timestamp": datetime.now().isoformat()
    })

    # Keep only last 5 exchanges
    if len(conversation_history) > MAX_CONTEXT_SIZE:
        conversation_history = conversation_history[-MAX_CONTEXT_SIZE:]

def get_context_summary() -> str:
    """Get summary of recent conversation for context-aware responses."""
    if not conversation_history:
        return ""

    recent = conversation_history[-3:]  # Last 3 exchanges
    return "\n".join([f"User: {ex['user']}\nBot: {ex['bot']}" for ex in recent])

# =========================
# Todo Logic with Multilingual Support
# =========================
def handle_message(message: str, language: str = "en"):
    """
    Handle user message with multilingual support and conversation context.

    Args:
        message: User message (in any language)
        language: Detected or selected language

    Returns:
        Response message in the same language
    """
    # Translate to English for processing if needed
    message_en = message
    if language != "en":
        message_en = translate_text(message, language, "en")

    msg = message_en.lower()

    # ADD TASK
    if "add" in msg and "task" in msg:
        title = message_en.split(":", 1)[-1].strip()
        if not title or title.lower() in ["add task", "task"]:
            # Extract from natural language
            parts = message_en.split("add", 1)
            if len(parts) > 1:
                title = parts[1].replace("task", "").replace(":", "").strip()

        new_task = Task(
            description=title,
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        task_repo.create(new_task)
        response_en = f"✅ Task added: {title}"

        # Translate response back if needed
        if language != "en":
            return translate_text(response_en, "en", language)
        return response_en

    # LIST TASKS
    if "list" in msg or "show" in msg or "tasks" in msg:
        tasks = task_repo.get_all()
        if not tasks:
            response_en = "📝 No tasks available."
            if language != "en":
                return translate_text(response_en, "en", language)
            return response_en

        task_list = "\n".join(
            [f"{'✓' if t.status == 'completed' else '○'} {t.id}. {t.description}"
             for t in tasks]
        )

        if language != "en":
            return translate_text(task_list, "en", language)
        return task_list

    # COMPLETE TASK
    if "complete" in msg or "done" in msg or "finish" in msg:
        tasks = task_repo.get_all()
        for t in tasks:
            if str(t.id) in msg or t.description.lower() in message_en.lower():
                t.status = "completed"
                task_repo.update(t)
                response_en = f"✅ Completed: {t.description}"

                if language != "en":
                    return translate_text(response_en, "en", language)
                return response_en

        response_en = "❌ Task not found."
        if language != "en":
            return translate_text(response_en, "en", language)
        return response_en

    # DELETE TASK
    if "delete" in msg or "remove" in msg:
        tasks = task_repo.get_all()
        for t in tasks:
            if str(t.id) in msg or t.description.lower() in message_en.lower():
                task_repo.delete(t.id)
                response_en = f"🗑️ Deleted: {t.description}"

                if language != "en":
                    return translate_text(response_en, "en", language)
                return response_en

        response_en = "❌ Task not found."
        if language != "en":
            return translate_text(response_en, "en", language)
        return response_en

    # AI fallback with context and language support
    return ask_openai(message, language)

# =========================
# API ROUTES
# =========================

@app.get("/api")
async def api_root():
    task_count = len(task_repo.get_all())
    return {
        "status": "ok",
        "service": "AI Todo Chatbot with SQLite",
        "version": "2.1.0",
        "todos": task_count,
        "database": "SQLite (persistent)",
        "features": {
            "multilingual": True,
            "language_detection": True,
            "translation": True,
            "conversation_context": True,
            "supported_languages": ["en", "es", "fr", "ar", "hi", "de", "zh", "ur"]
        }
    }

@app.get("/api/todos")
async def get_todos():
    tasks = task_repo.get_all()
    return [task_to_dict(t) for t in tasks]

@app.get("/api/context")
async def get_conversation_context():
    """Get current conversation context (last 5 exchanges)."""
    return {
        "context": conversation_history,
        "size": len(conversation_history),
        "max_size": MAX_CONTEXT_SIZE
    }

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Process user message with multilingual support and conversation context.

    Supports:
    - Automatic language detection (if language='auto')
    - Translation for non-English input
    - Conversation context tracking (last 5 exchanges)
    - Intent-driven todo management
    """
    # Detect language if set to 'auto' or not provided
    language = req.language if req.language and req.language != 'auto' else None

    if not language:
        language = detect_language(req.message)

    # Process message with language support
    reply = handle_message(req.message, language)

    # Add to conversation context
    add_to_context(req.message, reply, language)

    # Get all tasks
    tasks = task_repo.get_all()

    return {
        "response": reply,
        "todos": [task_to_dict(t) for t in tasks],
        "detected_language": language,
        "context_size": len(conversation_history)
    }

# =========================
# Frontend Serving
# =========================
@app.get("/")
async def serve_frontend():
    index_file = Path(__file__).parent.parent / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend not found. API is running."}

# =========================
# Static files
# =========================
@app.get("/{file_path:path}")
async def static_files(file_path: str):
    file = Path(__file__).parent.parent / file_path
    if file.exists():
        return FileResponse(file)
    return {"error": "File not found"}

# =========================
# Vercel export
# =========================
__all__ = ["app"]
