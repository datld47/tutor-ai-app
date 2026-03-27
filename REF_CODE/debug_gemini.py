import google.generativeai as genai
from gemini_helper import get_gemini_api_key
import os

key = get_gemini_api_key()
print(f"Key loaded: {key[:5]}...{key[-5:] if key else 'None'}")

if not key:
    print("KEY NOT FOUND!")
    exit(1)

genai.configure(api_key=key)

print("\n--- Available Models ---")
try:
    for m in genai.list_models():
        print(f"Name: {m.name}")
        print(f"Methods: {m.supported_generation_methods}")
        print("-" * 20)
except Exception as e:
    print(f"List models error: {e}")

print("\n--- Test Embedding ---")
try:
    # Try default
    # result = genai.embed_content(model="models/embedding-001", content="Hello world", task_type="retrieval_document")
    # print("embedding-001 works!")
    
    # Try text-embedding-004
    result = genai.embed_content(model="models/text-embedding-004", content="Hello world")
    print("text-embedding-004 works!")
except Exception as e:
    print(f"Embedding error: {e}")
