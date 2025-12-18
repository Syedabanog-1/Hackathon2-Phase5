@echo off
REM Deployment script for Chatbot Todo App (Windows)
REM This script helps automate the deployment process

echo ===========================================
echo Chatbot Todo App Deployment Script (Windows)
echo ===========================================

echo.
echo Step 1: Verifying repository is up to date...
git status

echo.
echo Step 2: Checking if all required files are present...

if exist "Dockerfile" (echo.✓ Dockerfile - Found) else (echo.✗ Dockerfile - Missing & goto error)
if exist "run_server.py" (echo.✓ run_server.py - Found) else (echo.✗ run_server.py - Missing & goto error)
if exist "src/cli/chatbot_cli.py" (echo.✓ src/cli/chatbot_cli.py - Found) else (echo.✗ src/cli/chatbot_cli.py - Missing & goto error)
if exist "index.html" (echo.✓ index.html - Found) else (echo.✗ index.html - Missing & goto error)
if exist "styles.css" (echo.✓ styles.css - Found) else (echo.✗ styles.css - Missing & goto error)
if exist "script.js" (echo.✓ script.js - Found) else (echo.✗ script.js - Missing & goto error)
if exist "README.md" (echo.✓ README.md - Found) else (echo.✗ README.md - Missing & goto error)

echo.
echo Step 3: API endpoints verification...
echo The following endpoints are available in the backend:
echo   - GET / (health check)
echo   - POST /chat (chat endpoint)
echo   - GET /api/todos (get todos)
echo   - POST /api/chat (web chat endpoint)

echo.
echo Step 4: Deployment Instructions
echo.
echo BACKEND (Railway^):
echo   1. Go to https://railway.app
echo   2. Create new project -^> Deploy from GitHub
echo   3. Select repository: Syedabanog-1/ChatbotTodoApp
echo   4. Set environment variable: OPENAI_API_KEY=your_api_key_here
echo   5. Railway will auto-detect Dockerfile and deploy
echo   6. Note your Railway URL ^(e.g., https://your-app.railway.app^)
echo.
echo FRONTEND (GitHub Pages^):
echo   1. Go to GitHub repo Settings
echo   2. Navigate to Pages section
echo   3. Set Source to main branch, folder /
echo   4. Frontend will be at https://Syedabanog-1.github.io/ChatbotTodoApp
echo.
echo POST-DEPLOYMENT:
echo   1. Update script.js with your Railway URL
echo   2. Commit and push the change
echo.

echo Step 5: Environment setup reminder
echo Make sure you have:
echo   - OpenAI API key ready
echo   - GitHub repository connected to Railway
echo   - Admin access to GitHub repository for Pages settings

echo.
echo Deployment checklist:
echo □ Backend deployed to Railway with OPENAI_API_KEY
echo □ Frontend deployed to GitHub Pages
echo □ script.js updated with Railway backend URL
echo □ Application tested and working
echo.

echo ===========================================
echo Deployment preparation complete!
echo ===========================================
goto end

:error
echo.
echo Error: Required files are missing. Please check the output above.
exit /b 1

:end
pause