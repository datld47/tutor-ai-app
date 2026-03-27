import google.generativeai as genai
from gemini_helper import get_gemini_api_key

GOOGLE_API_KEY = get_gemini_api_key()
genai.configure(api_key=GOOGLE_API_KEY)

print(f"API Key found: {bool(GOOGLE_API_KEY)}")

try:
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
