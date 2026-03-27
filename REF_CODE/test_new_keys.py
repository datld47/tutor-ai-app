import os
import google.generativeai as genai

def get_keys():
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GeminiKey', 'geminiKey.txt')
    with open(key_path, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

keys = get_keys()
print(f"Loaded {len(keys)} keys")

for i, key in enumerate(keys):
    print(f"\nTesting Key {i+1}: {key[:10]}...")
    try:
        genai.configure(api_key=key, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content('Say hello')
        print(f"Success! Response: {response.text.strip()}")
    except Exception as e:
        print(f"Error ({type(e).__name__}): {e}")
