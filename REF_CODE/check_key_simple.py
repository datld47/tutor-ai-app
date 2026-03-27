import urllib.request
import json

key = "AIzaSyBU5I_s2K-5ThLaFFiHIr76HTAiqMza_oI"

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
data = json.dumps({"contents": [{"parts": [{"text": "hello"}]}]}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

with open("key_diag.txt", "w", encoding="utf-8") as out:
    try:
        with urllib.request.urlopen(req) as response:
            res = response.read().decode('utf-8')
            out.write(f"Success! Response: {res[:100]}\n")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        out.write(f"HTTPError {e.code}: {error_body}\n")
    except Exception as e:
        out.write(f"Error ({type(e).__name__}): {e}\n")
