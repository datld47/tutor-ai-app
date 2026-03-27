import urllib.request
import json
import os

key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GeminiKey', 'geminiKey.txt')
with open(key_path, 'r') as f:
    keys = [line.strip() for line in f.readlines() if line.strip()]

for i, key in enumerate(keys):
    print(f"Testing key {i+1}: {key[:10]}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    data = json.dumps({"contents": [{"parts": [{"text": "hello"}]}]}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res = response.read().decode('utf-8')
            print(f"Success! Response start: {res[:50]}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTPError {e.code}: {error_body}")
    except Exception as e:
        print(f"Error ({type(e).__name__}): {e}")
