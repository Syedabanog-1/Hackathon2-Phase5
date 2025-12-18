"""
Test script to verify backend API functionality before deployment
"""
import asyncio
import json
from src.cli.chatbot_cli import app
from src.cli.chatbot_cli import ChatRequest

# Test the API endpoints directly
async def test_api():
    # Test health endpoint
    with app.test_client() as client:
        # Test health check
        response = await client.get("/")
        print("Health check:", response.status_code, response.json)

        # Test chat endpoint (this requires the app to be properly initialized)
        # For now, we'll just verify the endpoints exist

if __name__ == "__main__":
    print("Testing API endpoints...")
    asyncio.run(test_api())