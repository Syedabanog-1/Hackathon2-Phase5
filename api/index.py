"""
Vercel serverless deployment - Simplified FastAPI app
Lightweight version without heavy dependencies for serverless environment
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="AI Todo Chatbot API",
    version="1.0.0",
    description="Serverless AI-powered todo chatbot"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your GitHub Pages URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for todos (serverless - no persistence)
todos_storage: List[dict] = []
todo_counter = 0

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "en"

class TodoItem(BaseModel):
    id: int
    title: str
    completed: bool = False

# Simple OpenAI integration
def process_with_openai(message: str) -> str:
    """Process message with OpenAI API"""
    try:
        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "⚠️ OpenAI API key not configured. Please add OPENAI_API_KEY environment variable in Vercel settings."

        client = openai.OpenAI(api_key=api_key)

        # Simple chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful todo list assistant. Help users manage their tasks. Be concise and friendly."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=150,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"

def parse_todo_command(message: str) -> dict:
    """Parse simple todo commands"""
    global todo_counter, todos_storage

    message_lower = message.lower()

    # Add task
    if "add" in message_lower and "task" in message_lower:
        # Extract task from message
        task = message.replace("add task:", "").replace("add task", "").strip()
        if ":" in message:
            task = message.split(":", 1)[1].strip()

        todo_counter += 1
        new_todo = {
            "id": todo_counter,
            "title": task,
            "completed": False
        }
        todos_storage.append(new_todo)
        return {
            "success": True,
            "message": f"✅ Added task: {task}",
            "todos": todos_storage
        }

    # Show tasks
    elif "show" in message_lower or "list" in message_lower or "get" in message_lower:
        if not todos_storage:
            return {
                "success": True,
                "message": "📝 No tasks yet. Add one to get started!",
                "todos": []
            }

        task_list = "\n".join([
            f"{'✓' if t['completed'] else '○'} {t['id']}. {t['title']}"
            for t in todos_storage
        ])
        return {
            "success": True,
            "message": f"📋 Your tasks:\n{task_list}",
            "todos": todos_storage
        }

    # Mark complete
    elif "complete" in message_lower or "done" in message_lower:
        # Try to find task ID or name
        for todo in todos_storage:
            if str(todo['id']) in message or todo['title'].lower() in message_lower:
                todo['completed'] = True
                return {
                    "success": True,
                    "message": f"✅ Marked as complete: {todo['title']}",
                    "todos": todos_storage
                }

        return {
            "success": False,
            "message": "❌ Task not found",
            "todos": todos_storage
        }

    # Delete task
    elif "delete" in message_lower or "remove" in message_lower:
        for i, todo in enumerate(todos_storage):
            if str(todo['id']) in message or todo['title'].lower() in message_lower:
                removed = todos_storage.pop(i)
                return {
                    "success": True,
                    "message": f"🗑️ Deleted task: {removed['title']}",
                    "todos": todos_storage
                }

        return {
            "success": False,
            "message": "❌ Task not found",
            "todos": todos_storage
        }

    # Use AI for other queries
    else:
        ai_response = process_with_openai(message)
        return {
            "success": True,
            "message": ai_response,
            "todos": todos_storage
        }

# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "AI Todo Chatbot API is running",
        "mode": "serverless-vercel",
        "features": ["chat", "todos", "ai-powered"]
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
        "todos_count": len(todos_storage)
    }

@app.get("/api/todos")
async def get_todos():
    """Get all todos"""
    return [
        {
            "id": todo["id"],
            "title": todo["title"],
            "completed": todo["completed"]
        }
        for todo in todos_storage
    ]

@app.post("/api/chat")
async def web_chat(request: ChatRequest):
    """Main chat endpoint for web interface"""
    try:
        result = parse_todo_command(request.message)

        return {
            "response": result.get("message", ""),
            "success": result.get("success", True),
            "todos": result.get("todos", todos_storage)
        }

    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "success": False,
            "todos": todos_storage
        }

@app.post("/chat")
async def simple_chat(request: ChatRequest):
    """Simple chat endpoint"""
    try:
        result = parse_todo_command(request.message)
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

# Static files (if needed)
@app.get("/")
async def serve_index():
    """Serve frontend if available"""
    index_path = Path(__file__).parent.parent / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend not available in serverless mode"}

@app.get("/index.html")
async def serve_index_html():
    """Serve frontend if available"""
    index_path = Path(__file__).parent.parent / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend not available in serverless mode"}

# Serve static files
@app.get("/{path:path}.{ext:css|js|png|jpg|jpeg|gif|ico|svg}")
async def serve_static(path: str, ext: str):
    """Serve static files"""
    file_path = Path(__file__).parent.parent / f"{path}.{ext}"
    if file_path.exists():
        return FileResponse(file_path)
    return {"error": "File not found"}

# Export for Vercel
__all__ = ['app']
