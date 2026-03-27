from knowledge_base import query_knowledge_base
from services.query_transform_service import query_transform_service
from services.memory_service import memory_service
from gemini_helper import get_gemini_api_key
import google.generativeai as genai
import asyncio
import os

from gemini_helper import get_gemini_api_key, get_chat_model

GOOGLE_API_KEY = get_gemini_api_key()
genai.configure(api_key=GOOGLE_API_KEY)
model = get_chat_model()

class AdvancedRAGService:
    async def answer_with_citation(self, user_id: int, user_query: str, student_state: dict) -> dict:
        # 1. Lấy lịch sử
        history_str = memory_service.get_history_string(user_id)
        
        # 2. Tái cấu trúc câu hỏi (Bước quan trọng nhất của Advanced RAG)
        standalone_query = await query_transform_service.rewrite_query(user_query, history_str)
        
        # 3. Tìm kiếm trong Vector DB bằng câu hỏi ĐÃ SỬA
        # Trả về list các đoạn văn kèm metadata (Trang, Tên file)
        docs = await asyncio.to_thread(query_knowledge_base, standalone_query, n_results=3)
        
        # Format context cho Gemini
        context_str = ""
        sources = []
        for doc in docs:
            # doc structure giả định: {'text': '...', 'metadata': {'source': 'Paper1.pdf', 'page': 10}}
            context_str += f"[Nguồn: {doc['metadata']['source']}, Trang {doc['metadata']['page']}]: {doc['text']}\n\n"
            sources.append(doc['metadata'])

        # 4. Tạo Prompt trả lời cuối cùng
        final_prompt = f"""
        Bạn là Gia sư AI chuyên nghiệp. Hãy trả lời sinh viên dựa trên thông tin sau:
        
        THÔNG TIN TÌM THẤY (CONTEXT):
        {context_str}
        
        LỊCH SỬ CHAT:
        {history_str}
        
        CÂU HỎI (Đã làm rõ): "{standalone_query}"
        
        YÊU CẦU:
        - Trả lời chính xác, ngắn gọn.
        - Nếu thông tin có trong Context, hãy trích dẫn dạng [Tên file, Tr. X].
        - Nếu không có thông tin, hãy nói "Tài liệu hiện tại chưa đề cập vấn đề này".
        """
        
        # 5. Gọi AI trả lời
        response = await asyncio.to_thread(model.generate_content, final_prompt)
        answer = response.text
        
        # 6. Cập nhật bộ nhớ
        memory_service.add_message(user_id, "user", user_query)
        memory_service.add_message(user_id, "assistant", answer)
        
        return {
            "answer": answer,
            "sources": sources,
            "rewritten_query": standalone_query # Để debug xem AI hiểu thế nào
        }

advanced_rag = AdvancedRAGService()
