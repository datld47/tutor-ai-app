from collections import deque

class ConversationMemory:
    def __init__(self, max_history=5):
        # Lưu trữ Dictionary: {user_id: deque([...])}
        self._memories = {}
        self.max_history = max_history

    def add_message(self, user_id: int, role: str, content: str):
        if user_id not in self._memories:
            self._memories[user_id] = deque(maxlen=self.max_history * 2) # *2 vì có cả User và AI
        
        self._memories[user_id].append({"role": role, "content": content})

    def get_history_string(self, user_id: int) -> str:
        """Chuyển lịch sử thành chuỗi văn bản để đưa vào Prompt"""
        if user_id not in self._memories:
            return ""
        
        history_str = ""
        for msg in self._memories[user_id]:
            role_name = "Sinh viên" if msg["role"] == "user" else "Gia sư AI"
            history_str += f"{role_name}: {msg['content']}\n"
        return history_str

    def clear(self, user_id: int):
        if user_id in self._memories:
            del self._memories[user_id]

memory_service = ConversationMemory()
