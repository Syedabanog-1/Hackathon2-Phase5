"""
Test script to verify the chatbot functionality before deployment
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_chatbot_functionality():
    """Test the core chatbot functionality"""
    print("Testing chatbot functionality...")

    try:
        # Import the initialization function
        from src.cli.chatbot_cli import initialize_application

        # Initialize the application
        print("Initializing application...")
        task_repo, user_prefs, master_agent, logger, voice_service, translation_service = initialize_application()

        print("✓ Application initialized successfully")

        # Test basic chat functionality
        print("\nTesting chat functionality...")

        # Test adding a task
        result = master_agent.process("Add a task to buy groceries")
        print(f"Add task result: {result}")

        # Test listing tasks
        result = master_agent.process("Show my tasks")
        print(f"List tasks result: {result}")

        # Test completing a task
        result = master_agent.process("Mark task 1 as completed")
        print(f"Complete task result: {result}")

        # Test listing tasks again to see the change
        result = master_agent.process("Show my tasks")
        print(f"List tasks after completion: {result}")

        # Test deleting a task
        result = master_agent.process("Delete task 1")
        print(f"Delete task result: {result}")

        print("\n✓ Core functionality tests completed")

        # Test the repository directly
        print("\nTesting task repository...")
        all_tasks = task_repo.get_all()
        print(f"Current tasks in repository: {len(all_tasks)}")

        print("\n✓ All tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test that the API endpoints are properly defined"""
    print("\nTesting API endpoints...")

    try:
        from src.cli.chatbot_cli import app
        import json

        # Check if the new endpoints exist
        routes = [route.path for route in app.routes]

        required_endpoints = ['/', '/chat', '/api/todos', '/api/chat']
        missing_endpoints = [endpoint for endpoint in required_endpoints if endpoint not in routes]

        if missing_endpoints:
            print(f"❌ Missing endpoints: {missing_endpoints}")
            return False
        else:
            print("✓ All required API endpoints are defined")
            print(f"Available endpoints: {sorted(routes)}")
            return True

    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False

if __name__ == "__main__":
    print("Starting comprehensive functionality test...\n")

    # Test core functionality
    core_success = test_chatbot_functionality()

    # Test API endpoints
    api_success = test_api_endpoints()

    print(f"\n{'='*50}")
    print("TEST SUMMARY:")
    print(f"Core functionality: {'✓ PASS' if core_success else '❌ FAIL'}")
    print(f"API endpoints: {'✓ PASS' if api_success else '❌ FAIL'}")

    if core_success and api_success:
        print("\n🎉 All tests passed! The application is ready for deployment.")
        print("\nBefore deploying to Railway:")
        print("1. Make sure you have your OPENAI_API_KEY set in environment variables")
        print("2. The API endpoints are ready for web interface integration")
        print("3. Run 'python run_server.py' to start the server locally for testing")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above before deploying.")