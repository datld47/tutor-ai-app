import google.generativeai as genai
import asyncio
import os
from gemini_helper import get_gemini_api_key

# Cấu hình API Key
from gemini_helper import get_gemini_api_key, get_chat_model

GOOGLE_API_KEY = get_gemini_api_key()
genai.configure(api_key=GOOGLE_API_KEY)
# Use a lightweight model for query rewriting if possible, or same flash model
model = get_chat_model()

class QueryTransformService:
    async def rewrite_query(self, current_query: str, history_str: str) -> str:
        """
        Biến đổi câu hỏi mơ hồ thành câu hỏi đầy đủ ngữ nghĩa (Standalone Query).
        """
        if not history_str:
            return current_query

        prompt = f"""
        LỊCH SỬ HỘI THOẠI:
        {history_str}
        
        CÂU HỎI HIỆN TẠI CỦA SINH VIÊN:
        "{current_query}"
        
        NHIỆM VỤ:
        Câu hỏi hiện tại có thể thiếu chủ ngữ hoặc dùng từ thay thế (nó, cái đó, ông ấy...).
        Hãy viết lại câu hỏi này thành một câu hoàn chỉnh, rõ nghĩa để tôi có thể dùng nó tìm kiếm trong tài liệu.
        Nếu câu hỏi đã rõ ràng, hãy giữ nguyên.
        CHỈ TRẢ VỀ CÂU HỎI ĐÃ VIẾT LẠI, KHÔNG GIẢI THÍCH GÌ THÊM.
        
        Ví dụ:
        - History: "GAKT là gì?" -> AI: "Là Graph-Aware Knowledge Tracing..."
        - Current: "Tại sao nó tốt?"
        -> Output: "Tại sao GAKT lại tốt?"
        """
        
        # Gọi Gemini (Dùng model Flash cho nhanh)
        try:
             response = await asyncio.to_thread(model.generate_content, prompt)
             rewritten_query = response.text.strip()
             print(f"🔄 [Query Rewrite] '{current_query}' -> '{rewritten_query}'")
             return rewritten_query
        except Exception as e:
            print(f"Error rewriting query: {e}")
            return current_query

query_transform_service = QueryTransformService()
