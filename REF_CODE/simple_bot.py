import google.generativeai as genai
import os
import time

print("--- SIMPLE GEMINI BOT DIAGNOSTIC ---")

# 1. Get Key
key = None
try:
    with open('GeminiKey/geminiKey.txt', 'r') as f:
        key = f.readline().strip()
    print(f"✅ Key Found: {key[:5]}...{key[-5:] if len(key)>5 else ''}")
except Exception as e:
    print(f"❌ Error reading key: {e}")
    exit()

if not key:
    print("❌ Key file is empty!")
    exit()

genai.configure(api_key=key)

# 2. Test Gemini 2.0 Flash
print("\n--- Testing gemini-2.0-flash ---")
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("Attempting to generate 'Hello'...")
    response = model.generate_content("Hello")
    print(f"🎉 SUCCESS! Response: {response.text}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# 3. Test Gemini 1.5 Flash
print("\n--- Testing gemini-1.5-flash ---")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Attempting to generate 'Hello'...")
    response = model.generate_content("Hello")
    print(f"🎉 SUCCESS! Response: {response.text}")
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n--- DONE ---")
input("Press Enter to close...")
