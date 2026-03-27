import os
import json
import google.generativeai as genai
import pandas as pd
from glob import glob
import time

from gemini_helper import get_gemini_api_key

# Cấu hình Gemini
from gemini_helper import get_gemini_api_key, get_chat_model

GOOGLE_API_KEY = get_gemini_api_key()
genai.configure(api_key=GOOGLE_API_KEY)
model = get_chat_model()

DATA_DIR = 'DB/JSON_Data'

def analyze_lesson_content(file_path):
    """Đọc nội dung JSON và nhờ Gemini tóm tắt"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Lấy nội dung câu hỏi để làm ngữ cảnh
        questions = data.get('questions', [])[:5]
        sample_content = json.dumps(questions, ensure_ascii=False)
        
        prompt = f"""
        Dưới đây là dữ liệu câu hỏi trắc nghiệm của một bài học TMĐT:
        {sample_content}
        
        Nhiệm vụ:
        1. Tóm tắt nội dung bài học này trong 1 câu ngắn gọn (tiếng Việt).
        2. Trích xuất 3 từ khóa chuyên ngành quan trọng nhất.
        3. Đánh giá độ khó (1-5) dựa trên độ phức tạp của thuật ngữ.
        
        Trả về JSON format:
        {{
            "summary": "...",
            "keywords": ["...", "...", "..."],
            "difficulty": 3
        }}
        """
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        print(f"⚠️ Lỗi khi phân tích {file_path}: {e}")
        return {"summary": "Đang cập nhật...", "keywords": [], "difficulty": 1}

def generate_full_metadata(concepts):
    """Xây dựng cấu trúc + Metadata chi tiết"""
    
    print("🚀 Đang phân tích nội dung từng bài học...")
    metadata_map = {}
    
    for concept in concepts:
        print(f"   Analyzing: {concept['name']}...")
        details = analyze_lesson_content(concept['path'])
        metadata_map[concept['id']] = {
            "name": concept['name'],
            **details
        }
        time.sleep(1) # Tránh hit rate limit của Gemini
        
    return metadata_map

if __name__ == "__main__":
    files = glob(os.path.join(DATA_DIR, "*.json"))
    concepts = []
    
    # Tạo dummy file nếu chưa có để test logic code
    if not files:
         print("No JSON files found. Skipping analysis.")
    else:
        for f in files:
            with open(f, 'r', encoding='utf-8') as json_file:
                content = json.load(json_file)
                cid = content['metadata']['concept_id']
                name = content['metadata']['concept_name']
                concepts.append({"id": cid, "name": name, "path": f})

        # Chạy phân tích
        if concepts:
            meta = generate_full_metadata(concepts)
            
            # Lưu ra file Python để main.py import
            with open('course_metadata.py', 'w', encoding='utf-8') as f:
                f.write("COURSE_METADATA = " + json.dumps(meta, indent=4, ensure_ascii=False))
                
            print("✅ Đã tạo file 'course_metadata.py' chứa dữ liệu phong phú!")
