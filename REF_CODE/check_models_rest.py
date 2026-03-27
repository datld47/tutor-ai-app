import requests
import os
from gemini_helper import get_gemini_api_key

API_KEY = get_gemini_api_key()
print(f"Checking models with Key: {API_KEY[:5]}...")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

try:
    response = requests.get(url)
    with open('models_output_direct.txt', 'w', encoding='utf-8') as f:
        if response.status_code == 200:
            models = response.json().get('models', [])
            f.write(f"Found {len(models)} models:\n")
            print(f"Found {len(models)} models:")
            for m in models:
                f.write(f" - {m['name']}\n")
                print(f" - {m['name']}")
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                     f.write(f"   [Chat Support] {m['name']}\n")
                     print(f"   [Chat Support] {m['name']}")
        else:
            f.write(f"Error: {response.status_code} - {response.text}\n")
            print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    with open('models_output_direct.txt', 'w', encoding='utf-8') as f:
        f.write(f"Exception: {e}\n")
    print(f"Exception: {e}")
