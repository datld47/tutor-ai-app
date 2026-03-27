import google.generativeai as genai
from gemini_helper import get_gemini_api_key
import time

key = get_gemini_api_key()
genai.configure(api_key=key)

models_to_test = [
    'gemini-1.5-flash',
    'gemini-1.5-flash-001',
    'gemini-pro',
    'gemini-1.0-pro',
    'gemini-1.5-pro',
    'gemini-2.0-flash-exp'
]

print(f"Testing models with Key: {key[:5]}...")

working_model = None

for m in models_to_test:
    print(f"Testing {m}...", end=" ")
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("Hello")
        if response.text:
            print("✅ SUCCESS")
            working_model = m
            break
    except Exception as e:
        print(f"❌ FAILED ({str(e)[:50]}...)")
    time.sleep(1)

if working_model:
    print(f"\n🎉 FOUND WORKING MODEL: {working_model}")
    with open('working_model.txt', 'w') as f:
        f.write(working_model)
else:
    print("\n❌ NO WORKING MODEL FOUND.")
