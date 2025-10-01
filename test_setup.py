"""Test script to verify setup"""

import sys
import os

print("Python Path:")
for p in sys.path:
    print(f"  - {p}")

print("\nCurrent Directory:", os.getcwd())

print("\nFiles in current directory:")
for f in os.listdir('.'):
    print(f"  - {f}")

print("\nTesting imports:")

try:
    import openai
    print("✓ openai imported successfully")
    print(f"  Version: {openai.__version__}")
except ImportError as e:
    print(f"✗ openai import failed: {e}")

try:
    from config import Config
    print("✓ config imported successfully")
except ImportError as e:
    print(f"✗ config import failed: {e}")

try:
    from models import PatientInfo
    print("✓ models imported successfully")
except ImportError as e:
    print(f"✗ models import failed: {e}")

try:
    from processors import ProcessorFactory
    print("✓ processors imported successfully")
except ImportError as e:
    print(f"✗ processors import failed: {e}")

try:
    from services import AIExtractor
    print("✓ services imported successfully")
except ImportError as e:
    print(f"✗ services import failed: {e}")

try:
    from main import AidaAIAssistant
    print("✓ main imported successfully")
except ImportError as e:
    print(f"✗ main import failed: {e}")

print("\n" + "="*50)
print("If all imports show ✓, your setup is correct!")
print("="*50)