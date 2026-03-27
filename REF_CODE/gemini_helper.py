import google.generativeai as genai
import re
import os
import json
import time
import threading

# Global lock
key_lock = threading.Lock()

# Models to try in order
# Key is mapped to experimental models like gemini-2.5-flash
MODEL_PRIORITY = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash']

def get_all_api_keys():
    try:
        key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GeminiKey', 'geminiKey.txt')
        if os.path.exists(key_path):
            with open(key_path, 'r') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading Gemini API Keys: {e}")
    return []

def get_gemini_api_key():
    """Legacy compatibility: returns the first key"""
    keys = get_all_api_keys()
    return keys[0] if keys else None

class RobustGeminiModel:
    def __init__(self, keys):
        self.keys = keys
        self.current_key_index = 0
        self.current_model_index = 0
        self.model_name = MODEL_PRIORITY[0]
        
        self._configure_current_key()
        self.model = genai.GenerativeModel(self.model_name)

    def _configure_current_key(self):
        if not self.keys: return
        key = self.keys[self.current_key_index]
        genai.configure(api_key=key, transport='rest')
        print(f"🔑 Using Key #{self.current_key_index + 1} | Model: {self.model_name}")

    def _rotate_strategy(self):
        with key_lock:
            next_key_idx = (self.current_key_index + 1)
            if next_key_idx < len(self.keys):
                self.current_key_index = next_key_idx
                print(f"🔄 Switching to Key #{self.current_key_index + 1}...")
            else:
                self.current_key_index = 0
                next_model_idx = (self.current_model_index + 1) % len(MODEL_PRIORITY)
                self.current_model_index = next_model_idx
                self.model_name = MODEL_PRIORITY[next_model_idx]
                self.model = genai.GenerativeModel(self.model_name)
                print(f"🔄 Switching to Model: {self.model_name}...")
            self._configure_current_key()

    def start_chat(self, *args, **kwargs):
        chat_session = self.model.start_chat(*args, **kwargs)
        return RobustChatSession(chat_session, self, args, kwargs)

    def _retry_operation(self, func, *args, **kwargs):
        max_retries = 15
        last_error = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                if "429" in error_str or "quota" in error_str or "404" in error_str:
                    print(f"⚠️ Error ({error_str[:30]}...) on Key #{self.current_key_index + 1}/{self.model_name}.")
                    self._rotate_strategy()
                    time.sleep(1)
                    if hasattr(self.model, 'generate_content') and func.__name__ == 'generate_content':
                         func = self.model.generate_content
                    continue
                else:
                    raise e
        raise Exception(f"All keys/models exhausted. Last error: {last_error}")
    
    def generate_content(self, *args, **kwargs):
        return self._retry_operation(self.model.generate_content, *args, **kwargs)

class RobustChatSession:
    def __init__(self, chat_session, parent, start_args, start_kwargs):
        self.chat = chat_session
        self.parent = parent
        self.start_args = start_args
        self.start_kwargs = start_kwargs

    def send_message(self, *args, **kwargs):
        max_retries = 15
        for attempt in range(max_retries):
            try:
                return self.chat.send_message(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "quota" in error_str:
                    print(f"⚠️ Chat Error. Rotating credentials...")
                    self.parent._rotate_strategy()
                    time.sleep(1)
                    old_history = self.chat.history
                    self.chat = self.parent.model.start_chat(history=old_history)
                    continue
                raise e

def get_chat_model():
    keys = get_all_api_keys()
    if not keys: return None
    return RobustGeminiModel(keys)

# --- Restored Helper Functions ---

def extract_json_from_text(text):
    """Trích xuất khối JSON từ phản hồi của Gemini"""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
    return {"sentiment": "neutral", "action": "continue"}

def build_system_prompt(lesson_content):
    """Tạo Prompt kỹ thuật để Gemini đóng vai Gia sư PKT"""
    return f"""
    BẠN LÀ: Một gia sư AI thấu cảm (Empathetic Tutor) môn Thương mại điện tử.
    CONTEXT BÀI HỌC: {lesson_content}
    NHIỆM VỤ:
    1. Trả lời câu hỏi của sinh viên ngắn gọn, chính xác.
    2. Nếu sinh viên trả lời sai câu hỏi quiz, hãy giải thích tại sao sai.
    3. QUAN TRỌNG: Phân tích cảm xúc ngầm ẩn của sinh viên.
    OUTPUT FORMAT:
    Cuối câu trả lời, bạn BẮT BUỘC phải xuống dòng và viết một đoạn JSON:
    ---SEPARATOR---
    {{"sentiment": "neutral|confused|frustrated|excited", "correctness": true|false|null, "short_feedback": "..."}}
    """
