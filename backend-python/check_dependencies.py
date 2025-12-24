"""Check all dependencies and provide installation instructions"""
import sys

missing = []
installed = []

deps = {
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'google.genai': 'google-genai',
    'dotenv': 'python-dotenv',
    'websockets': 'websockets',
}

print("Checking dependencies...\n")

for module, package in deps.items():
    try:
        if module == 'dotenv':
            __import__('dotenv')
        elif module == 'google.genai':
            __import__('google.genai')
        else:
            __import__(module)
        installed.append(package)
        print(f"[OK] {package}")
    except ImportError:
        missing.append(package)
        print(f"[MISSING] {package}")

if missing:
    print(f"\n[MISSING] {len(missing)} package(s): {', '.join(missing)}")
    print("\nTo install, run:")
    print("  pip install -r requirements.txt")
    print("\nOr install individually:")
    for pkg in missing:
        print(f"  pip install {pkg}")
    sys.exit(1)
else:
    print(f"\n[OK] All dependencies installed!")
    print("\nYou can now run the server:")
    print("  python main.py")

