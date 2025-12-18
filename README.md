# AI-Powered Multilingual Voice-Enabled Todo Chatbot

A console-based AI-powered todo chatbot that accepts natural language commands in both text and voice formats, automatically detects and translates between 7+ languages, and uses a modular agent architecture for intent classification, task management, and multimodal interaction.

## Features

- **Text-Based Task Management**: Manage tasks using natural language English commands (add, view, update, delete)
- **Multilingual Support**: Interact in 7+ languages (English, Spanish, French, Mandarin, Arabic, Hindi, German)
- **Voice Input/Output**: Hands-free voice commands with speech-to-text and text-to-speech
- **Conversational Context**: Understand implicit references and follow-up questions
- **Partial Task Updates**: Modify individual task fields without re-specifying entire task

## Quick Start

### Prerequisites

- Python 3.11 or higher
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ChatbotTodoApp
git checkout 001-multimodal-todo-chatbot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp config/.env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Chatbot

```bash
python src/cli/chatbot_cli.py
```

### Basic Usage

```
You: add a task to buy groceries tomorrow
Chatbot: Task added: buy groceries (due December 14, 2025)

You: show my tasks
Chatbot: You have 1 task:
  1. [pending] buy groceries (due: Dec 14, 6:00 PM)

You: mark task 1 as completed
Chatbot: Task 1 marked as completed. Great job!
```

## Project Structure

```
ChatbotTodoApp/
├── src/
│   ├── agents/          # Agent implementations
│   ├── models/          # Data models (Task, ConversationContext, UserPreferences)
│   ├── services/        # Services (TaskRepository, Whisper, TTS, Translation)
│   ├── cli/             # CLI interface entry point
│   └── lib/             # Utilities (config, logging, MCP helpers)
├── tests/               # Tests (contract, integration, unit)
├── data/                # Database and preferences (auto-created)
├── config/              # Configuration templates
├── specs/               # Feature specifications and planning docs
└── docs/                # Documentation
```

## Development Status

### Completed (Phase 1 & 2: Foundation)
- ✅ Project directory structure
- ✅ Python environment and dependencies
- ✅ Configuration files (.env.example, .gitignore, requirements.txt)
- ✅ Task entity model
- ✅ ConversationContext entity
- ✅ UserPreferences entity
- ✅ TaskRepository service with SQLite database
- ✅ MCP helpers and logging configuration
- ✅ Basic CLI interface

### In Progress
- 🚧 Agent implementation (Intent Classifier, Language Detector, etc.)
- 🚧 Voice processing integration
- 🚧 Multi-language translation

### Planned
- ⏳ Full agent orchestration
- ⏳ Voice input/output
- ⏳ Comprehensive testing
- ⏳ Documentation

## Testing

Run tests:
```bash
pytest tests/ -v
```

## Documentation

For detailed documentation, see:
- [Quickstart Guide](specs/001-multimodal-todo-chatbot/quickstart.md)
- [Technical Plan](specs/001-multimodal-todo-chatbot/plan.md)
- [Data Model](specs/001-multimodal-todo-chatbot/data-model.md)
- [Research](specs/001-multimodal-todo-chatbot/research.md)

## Web Interface

The application now includes a web interface that can be hosted on GitHub Pages, with the backend deployed to Railway.

### Frontend Files
- `index.html` - Main web interface
- `styles.css` - Styling for the interface
- `script.js` - JavaScript functionality

### Deployment

#### Backend (Railway)

1. Create an account on [Railway](https://railway.app)
2. Create a new project and connect your GitHub repository
3. Set the following environment variables:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `DATABASE_PATH` - Path to SQLite database (default: `data/tasks.db`)
4. Set the start command to: `python run_server.py`
5. Deploy the application
6. Note the deployed URL (e.g., `https://your-app-name.up.railway.app`)

#### Frontend (GitHub Pages)

1. Push the frontend files (index.html, styles.css, script.js) to your repository
2. Go to your repository settings
3. In the "Pages" section, select source as the main branch
4. The frontend will be available at `https://your-username.github.io/repository-name`

#### Configuration

After deploying the backend, update the `BACKEND_URL` in `script.js`:

```javascript
const BACKEND_URL = 'https://your-railway-app-url.railway.app'; // Replace with your Railway URL
```

### API Endpoints

- `GET /` - Health check
- `POST /chat` - Process chat message (CLI endpoint)
- `GET /api/todos` - Get all todos
- `POST /api/chat` - Web chat endpoint (returns response + todos)

## Running the Server

To run the backend server locally:

```bash
python run_server.py
```

The server will start on `http://localhost:8000` with API documentation available at `http://localhost:8000/docs`.

## License

[Your License Here]

## Contributing

[Contributing Guidelines]
