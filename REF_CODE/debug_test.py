import google.generativeai as genai
import os
import sys

def log(msg):
    with open('debug_log.txt', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    print(msg)

log("1. Starting script...")

try:
    log("2. Reading key...")
    with open('GeminiKey/geminiKey.txt', 'r') as f:
        key = f.readline().strip()
    log(f"3. Key Read: {key[:5]}...")
except Exception as e:
    log(f"Error reading key: {e}")
    sys.exit(1)

log("4. Configuring GenAI...")
try:
    genai.configure(api_key=key)
    log("5. Configured.")
except Exception as e:
    log(f"Error configuring: {e}")
    sys.exit(1)

log("6. Instantiating Model gemini-1.5-flash...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    log("7. Model instantiated.")
except Exception as e:
    log(f"Error instantiating: {e}")
    sys.exit(1)

log("8. Generating content (Hello)...")
try:
    response = model.generate_content("Hello")
    log(f"9. Response received: {response.text}")
except Exception as e:
    log(f"Error generating: {e}")

log("10. Done.")
