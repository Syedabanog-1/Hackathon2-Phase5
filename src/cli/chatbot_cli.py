

"""
Main entry point for the chatbot CLI application.
Console-first, API-ready design.
"""

import sys
import os
from pathlib import Path

# ==============================
# Windows UTF-8 Console Fix
# ==============================
if sys.platform == "win32":
    try:
        os.system("chcp 65001 > nul 2>&1")
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ==============================
# Path Fix for Imports
# ==============================
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ==============================
# FastAPI (API-ready layer)
# ==============================
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel

# Global API State
api_resources = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize application on startup
    try:
        task_repo, user_prefs, master_agent, logger, voice_service, translation_service = initialize_application()
        api_resources['agent'] = master_agent
        api_resources['prefs'] = user_prefs
        api_resources['translator'] = translation_service
        logger.info("API initialized successfully")
    except Exception as e:
        print(f"API Startup Error: {e}")
    yield
    # Cleanup if needed

app = FastAPI(title="AI Todo Chatbot API", version="1.0.0", lifespan=lifespan)

class ChatRequest(BaseModel):
    message: str
    language: str | None = None



@app.get("/health")
def health():
    return {"status": "ok", "mode": "api-ready"}

@app.get("/")
async def serve_index():
    """Serve the web interface."""
    index_path = Path(__file__).parent.parent.parent / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"status": "ok", "mode": "api-ready"}

@app.get("/styles.css")
async def serve_styles():
    """Serve the CSS file."""
    css_path = Path(__file__).parent.parent.parent / "styles.css"
    if css_path.exists():
        return FileResponse(css_path, media_type="text/css")
    return {"error": "Not found"}

@app.get("/script.js")
async def serve_script():
    """Serve the JavaScript file."""
    js_path = Path(__file__).parent.parent.parent / "script.js"
    if js_path.exists():
        return FileResponse(js_path, media_type="application/javascript")
    return {"error": "Not found"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Process a chat message via the AI Agent.
    """
    agent = api_resources.get('agent')
    if not agent:
        return {"success": False, "message": "Agent not active"}

    # Optional: Handle language translation here using api_resources['translator']
    # For now, pass direct message

    msg = request.message
    # If language is provided, we could translate input/output
    # But sticking to simple agent process for now as per minimal request

    result = agent.process(msg)
    return result


@app.get("/api/todos")
async def get_todos():
    """
    Get all todos from the repository.
    """
    try:
        agent = api_resources.get('agent')
        if not agent:
            return []

        # Access the repository through the agent
        # Using get_all() method which returns all tasks
        if hasattr(agent, 'repository'):
            todos = agent.repository.get_all()
            # Convert to simple dict format for JSON response
            # Note: Task model might have 'description' instead of 'title'
            return [{"id": t.id, "title": t.description, "completed": t.status == "completed"} for t in todos]
        else:
            return []
    except Exception as e:
        print(f"Error getting todos: {e}")
        return []


@app.post("/api/chat")
async def web_chat_endpoint(request: ChatRequest):
    """
    Web-specific chat endpoint that returns both response and todos.
    """
    agent = api_resources.get('agent')
    if not agent:
        return {"success": False, "message": "Agent not active"}

    msg = request.message
    result = agent.process(msg)

    # Get updated todos after processing the command
    todos = []
    try:
        if hasattr(agent, 'repository'):
            todo_objects = agent.repository.get_all()
            todos = [{"id": t.id, "title": t.description, "completed": t.status == "completed"} for t in todo_objects]
    except Exception as e:
        print(f"Error getting todos: {e}")

    # Return both the chat response and the updated todo list
    return {
        "response": result.get("message", ""),
        "success": result.get("success", False),
        "todos": todos
    }


# ==============================
# Internal Imports
# ==============================
from src.lib.config import config
from src.lib.logging_config import setup_logging
from src.services.task_repository import TaskRepository
from src.models.user_preferences import UserPreferences
from src.agents.master_chat_agent import MasterChatAgent
from src.services.voice_service import VoiceService
from src.services.translation_service import TranslationService


# ==============================
# Initialization
# ==============================
def initialize_application():
    """Initialize application components."""
    logger = setup_logging(config.log_level, config.log_file)
    logger.info("Starting AI-Powered Multilingual Voice-Enabled Todo Chatbot")

    is_valid, errors = config.validate()
    if not is_valid:
        print("\n❌ Configuration Error:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease check your .env file.")
        sys.exit(1)

    task_repo = TaskRepository(config.database_path)
    user_prefs = UserPreferences.load_from_file(config.preferences_path)
    user_prefs.save_to_file(config.preferences_path)

    master_agent = MasterChatAgent(
        api_key=config.openai_api_key,
        repository=task_repo
    )

    voice_service = VoiceService()
    translation_service = TranslationService()

    logger.info("Application initialized successfully")
    return task_repo, user_prefs, master_agent, logger, voice_service, translation_service


# ==============================
# CLI UI Helpers
# ==============================
def print_welcome():
    print("\n" + "=" * 60)
    print("🤖 AI-Powered Multilingual Voice-Enabled Todo Chatbot v1.0")
    print("=" * 60)
    print("\nType your command or '/help' for assistance.\n")


def print_help():
    print("\n📚 Available Commands:")
    print("  /help            - Show help")
    print("  /voice on|off    - Toggle voice mode")
    print("  /language <code> - Set preferred language")
    print("  /settings        - View settings")
    print("  /clear           - Clear context")
    print("  /exit            - Quit")
    print()


# ==============================
# CLI Main Loop
# ==============================
def main():
    try:
        task_repo, user_prefs, master_agent, logger, voice_service, translation_service = initialize_application()
        print_welcome()

        while True:
            try:
                # 1. Input Acquisition
                if user_prefs.voice_input_enabled:
                    # Capture voice
                    lang = user_prefs.preferred_language if user_prefs.preferred_language else 'en'
                    user_input = voice_service.listen(lang=lang)
                    if user_input:
                        print(f"You (Voice): {user_input}")
                    else:
                        # Fallback to text input if voice fails or user cancels
                        # Or loop? Better to allow fallback to text for that turn
                        # But loop expects input.
                        # If voice detected nothing, asking to type is good UX.
                        user_input = input("You (Voice failed, type here): ").strip()
                else:
                    user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input == "/help":
                    print_help()
                    continue

                if user_input == "/exit":
                    print("\n👋 Goodbye!")
                    break

                if user_input == "/settings":
                    print("\n⚙️ Settings:")
                    print(f" Language: {user_prefs.preferred_language or 'Auto'}")
                    print(f" Voice Input: {user_prefs.voice_input_enabled}")
                    print(f" Voice Output: {user_prefs.voice_output_enabled}")
                    continue

                if user_input.startswith("/voice "):
                    mode = user_input.split(" ", 1)[1].lower()
                    enabled = mode == "on"
                    user_prefs.voice_input_enabled = enabled
                    user_prefs.voice_output_enabled = enabled
                    user_prefs.save_to_file(config.preferences_path)
                    print(f"🎤 Voice mode {'enabled' if enabled else 'disabled'}")
                    continue

                if user_input.startswith("/language "):
                    lang = user_input.split(" ", 1)[1]
                    user_prefs.preferred_language = lang
                    user_prefs.save_to_file(config.preferences_path)
                    print(f"🌍 Language set to {lang}")
                    continue

                if user_input == "/clear":
                    master_agent.reset_context()
                    print("🧹 Context cleared")
                    continue

                # 2. Input Translation (to English)
                processed_input = user_input
                target_lang = user_prefs.preferred_language
                
                if target_lang and target_lang.lower() != 'en' and not user_input.startswith("/"):
                    # Translate to English for processing
                    print("🌐 Translating input...")
                    processed_input = translation_service.translate(user_input, "English")
                    # print(f"  [Translated]: {processed_input}")

                # 3. Process via AI Agent
                result = master_agent.process(processed_input)

                response_text = result.get('message')

                # 4. Output Translation (to Target Language)
                if target_lang and target_lang.lower() != 'en':
                    # Translate response back to user's language
                    # print("🌐 Translating response...")
                    response_text = translation_service.translate(response_text, target_lang)

                # 5. Output Display & Audio
                if result.get("success"):
                    print(f"Chatbot: {response_text}")
                else:
                    print(f"Chatbot: ❌ {response_text}")

                if user_prefs.voice_output_enabled:
                    voice_service.speak(response_text, lang=target_lang or 'en')

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

            except EOFError:
                print("\n👋 Goodbye!")
                break

            except Exception as e:
                logger.error(f"Runtime error: {e}", exc_info=True)
                print("❌ Error occurred. Try again.")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


# ==============================
# CLI Entry Point
# ==============================
if __name__ == "__main__":
    main()
