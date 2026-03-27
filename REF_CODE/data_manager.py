import json
import os
from glob import glob

class CourseDataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CourseDataManager, cls).__new__(cls)
            cls._instance.data = {}
            cls._instance.load_data()
        return cls._instance

    def load_data(self):
        # Đường dẫn đến thư mục JSON bạn đã convert
        json_path = "DB/JSON_Data/*.json"
        files = glob(json_path)
        for f in files:
            with open(f, 'r', encoding='utf-8') as file:
                try:
                    content = json.load(file)
                    concept_id = content['metadata']['concept_id']
                    self.data[concept_id] = content
                except Exception as e:
                    print(f"Error loading {f}: {e}")
        print(f"✅ Đã load {len(self.data)} bài học vào bộ nhớ.")

    def get_lesson(self, concept_id):
        return self.data.get(concept_id)

    def get_all_concepts(self):
        # Trả về danh sách để tạo Menu
        return [{"id": k, "name": v['metadata']['concept_name']} for k, v in self.data.items()]

# Khởi tạo singleton
data_manager = CourseDataManager()
