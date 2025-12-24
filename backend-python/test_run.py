"""Quick test to check if server can start"""
import sys
import os

print("Testing dependencies...")
try:
    import fastapi
    print("[OK] FastAPI installed")
except ImportError as e:
    print(f"[FAIL] FastAPI missing: {e}")
    sys.exit(1)

try:
    import uvicorn
    print("[OK] Uvicorn installed")
except ImportError as e:
    print(f"[FAIL] Uvicorn missing: {e}")
    sys.exit(1)

try:
    import google.genai
    print("[OK] google-genai installed")
except ImportError as e:
    print(f"[FAIL] google-genai missing: {e}")
    print("\nPlease run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("[OK] python-dotenv installed")
except ImportError as e:
    print(f"[FAIL] python-dotenv missing: {e}")
    sys.exit(1)

print("\nTesting imports...")
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from main import app
    print("[OK] Main module imports successfully")
    print("[OK] Server should be able to start!")
    print("\nTo start the server, run: python main.py")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

