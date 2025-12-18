
import uvicorn
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting AI Chatbot Server...")
    print("Documentation: http://localhost:8000/docs")
    print("API endpoints available at:")
    print("  - GET / (health check)")
    print("  - POST /chat (chat endpoint)")
    print("  - GET /api/todos (get todos)")
    print("  - POST /api/chat (web chat endpoint)")

    # Import the app from the module
    try:
        from src.cli.chatbot_cli import app
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=False)
    except Exception as e:
        print(f"Failed to start server: {e}")
        input("Press Enter to exit...")
