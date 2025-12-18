#!/bin/bash
# Deployment script for Chatbot Todo App
# This script helps automate the deployment process

echo "==========================================="
echo "Chatbot Todo App Deployment Script"
echo "==========================================="

echo
echo "Step 1: Verifying repository is up to date..."
git status

echo
echo "Step 2: Checking if all required files are present..."
REQUIRED_FILES=(
    "Dockerfile"
    "run_server.py"
    "src/cli/chatbot_cli.py"
    "index.html"
    "styles.css"
    "script.js"
    "README.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file - Found"
    else
        echo "✗ $file - Missing"
        exit 1
    fi
done

echo
echo "Step 3: API endpoints verification..."
echo "The following endpoints are available in the backend:"
echo "  - GET / (health check)"
echo "  - POST /chat (chat endpoint)"
echo "  - GET /api/todos (get todos)"
echo "  - POST /api/chat (web chat endpoint)"

echo
echo "Step 4: Deployment Instructions"
echo
echo "BACKEND (Railway):"
echo "  1. Go to https://railway.app"
echo "  2. Create new project -> Deploy from GitHub"
echo "  3. Select repository: Syedabanog-1/ChatbotTodoApp"
echo "  4. Set environment variable: OPENAI_API_KEY=your_api_key_here"
echo "  5. Railway will auto-detect Dockerfile and deploy"
echo "  6. Note your Railway URL (e.g., https://your-app.railway.app)"
echo
echo "FRONTEND (GitHub Pages):"
echo "  1. Go to GitHub repo Settings"
echo "  2. Navigate to Pages section"
echo "  3. Set Source to main branch, folder /"
echo "  4. Frontend will be at https://Syedabanog-1.github.io/ChatbotTodoApp"
echo
echo "POST-DEPLOYMENT:"
echo "  1. Update script.js with your Railway URL"
echo "  2. Commit and push the change"
echo

echo "Step 5: Environment setup reminder"
echo "Make sure you have:"
echo "  - OpenAI API key ready"
echo "  - GitHub repository connected to Railway"
echo "  - Admin access to GitHub repository for Pages settings"

echo
echo "Deployment checklist:"
echo "□ Backend deployed to Railway with OPENAI_API_KEY"
echo "□ Frontend deployed to GitHub Pages"
echo "□ script.js updated with Railway backend URL"
echo "□ Application tested and working"
echo

echo "==========================================="
echo "Deployment preparation complete!"
echo "==========================================="