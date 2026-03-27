import google.generativeai as genai
from gemini_helper import get_gemini_api_key
import time

key = get_gemini_api_key()
genai.configure(api_key=key)

models_to_test = [
    'gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash-001',
    'gemini-1.5-flash-002',
    'gemini-1.5-flash-8b',
    'gemini-pro',
    'gemini-1.0-pro',
    'gemini-1.5-pro',
    'gemini-1.5-pro-latest',
    'gemini-1.5-pro-001',
    'gemini-1.5-pro-002',
    'gemini-2.0-flash-exp'
]

print(f"--- TESTING MODELS WITH KEY ENDING IN ...{key[-5:] if key else 'None'} ---")

valid_model = None

for m in models_to_test:
    print(f"Trying: {m} ... ", end="", flush=True)
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("Hello, assume this is a test.")
        if response and response.text:
            print(f"✅ WORKS! (Response: {response.text[:20]}...)")
            valid_model = m
            break # Stop at first working model to save time/quota? No, let's find the BEST one.
            # Actually, let's stick with the first modern one that works.
    except Exception as e:
        error_str = str(e)
        if "404" in error_str:
             print("❌ 404 Not Found")
        elif "429" in error_str:
             print("⚠️ 429 Quota Exceeded (Exists but limited)")
        else:
             print(f"❌ Error: {error_str[:50]}...")
    time.sleep(1) # Avoid self-rate-limiting

if valid_model:
    print(f"!!! WINNER: {valid_model} !!!")
else:
    print("!!! NO WORKING MODELS FOUND !!!")
