import os
import google.generativeai as genai
import sys

with open('key_test_results.txt', 'w', encoding='utf-8') as out:
    def get_keys():
        key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GeminiKey', 'geminiKey.txt')
        with open(key_path, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]

    keys = get_keys()
    out.write(f"Loaded {len(keys)} keys\n")
    
    for i, key in enumerate(keys):
        out.write(f"\nTesting Key {i+1}: {key[:10]}...\n")
        out.flush()
        try:
            genai.configure(api_key=key, transport='rest')
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content('Say hello')
            out.write(f"Success! Response: {response.text.strip()}\n")
        except Exception as e:
            out.write(f"Error ({type(e).__name__}): {e}\n")
        out.flush()
