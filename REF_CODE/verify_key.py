import google.generativeai as genai
import os
import time

# Define path to key file
key_file_path = os.path.join("GeminiKey", "geminiKey.txt")

print(f"--- Checking ALL API Keys in {key_file_path} ---")

MODELS_TO_TEST = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro-latest']

def test_key(key, index):
    if not key or len(key) < 10:
        print(f"Key #{index}: ❌ Invalid/Empty")
        return False
        
    print(f"\n🔑 Key #{index}: {key[:10]}...{key[-5:]}")
    genai.configure(api_key=key, transport='rest')
    
    working = False
    for model_name in MODELS_TO_TEST:
        try:
            print(f"   Testing {model_name}...", end=" ")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi", generation_config={'max_output_tokens': 1})
            print(f"✅ WORKING!")
            working = True
            # If one model works, we consider the key valid for now, but helpful to know which one
            # return True 
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg:
                 print("⚠️  RATE LIMITED (429)")
            elif "404" in error_msg:
                 print("❌ MODEL NOT FOUND (404)")
            else:
                 print(f"❌ ERROR: {str(e)[:50]}...")
    
    return working

valid_keys = []
try:
    with open(key_file_path, 'r') as f:
        keys = [line.strip() for line in f.readlines() if line.strip()]
        
    if not keys:
        print("❌ Error: Key file is empty!")
    else:
        print(f"ℹ️  Found {len(keys)} keys.")
        for i, key in enumerate(keys):
            if test_key(key, i+1):
                valid_keys.append(key)
                
    print("\n--- Summary ---")
    print(f"Working Keys: {len(valid_keys)} / {len(keys)}")
    
    if len(valid_keys) > 0:
        print("✅ At least one key/model combination works.")
    else:
        print("❌ All keys/models failed. Free tier might be exhausted for your IP/Account.")

except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")

print("\nPress Enter to exit...")
input()
