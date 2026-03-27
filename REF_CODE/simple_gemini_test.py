import google.generativeai as genai
import os

# 1. Read Key
try:
    with open('GeminiKey/geminiKey.txt', 'r') as f:
        key = f.readline().strip()
    print(f"Key read: {key[:5]}...{key[-5:] if len(key)>5 else ''}")
except Exception as e:
    print(f"Error reading key: {e}")
    exit()

# 2. Configure
genai.configure(api_key=key)

# 3. Test Models
models = ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-2.0-flash']

print("\n--- MODEL TEST ---")
for m in models:
    print(f"Testing {m}...", end=" ")
    try:
        model = genai.GenerativeModel(m)
        resp = model.generate_content("Hello")
        print(f"✅ Success! Response: {resp.text.strip()}")
        # If one works, we are good.
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}")
