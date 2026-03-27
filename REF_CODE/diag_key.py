import urllib.request
import json
import socket

# Set default timeout for sockets
socket.setdefaulttimeout(10)

key = "AIzaSyBU5I_s2K-5ThLaFFiHIr76HTAiqMza_oI"

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
data = json.dumps({"contents": [{"parts": [{"text": "hello"}]}]}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

with open("diag_result.txt", "w", encoding="utf-8") as out:
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res = response.read().decode('utf-8')
            out.write(f"Success! {res[:100]}\n")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        out.write(f"HTTPError {e.code}: {body}\n")
    except Exception as e:
        out.write(f"Error: {e}\n")
