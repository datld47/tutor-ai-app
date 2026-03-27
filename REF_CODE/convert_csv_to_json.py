# -*- coding: utf-8 -*-
import os
import pandas as pd
import json
import uuid
import sys

# Ensure UTF-8 output for print
# sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình đường dẫn tuyệt đối để tránh lỗi relative path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, 'DB', 'TMDT_Chuong1')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'DB', 'JSON_Data')

import re

def generate_concept_id(filename):
    try:
        # Tương thích nhiều định dạng: Chương_1_Tiết 1.csv, Chương_2_Tiết_2.csv, Chuong 3 Tiet 1.csv
        match = re.search(r'(?:Chương|Chuong)\D*(\d+)\D*(?:Tiết|Tiet)\D*(\d+)', filename, re.IGNORECASE)
        if match:
            chapter = match.group(1)
            lesson = match.group(2)
            return f"Chuong_{chapter}_Tiet_{lesson}"
        return f"CONCEPT_{uuid.uuid4().hex[:6]}"
    except:
        return f"CONCEPT_{uuid.uuid4().hex[:6]}"

def convert_csv_to_json():
    print(f"📂 INPUT_FOLDER: {INPUT_FOLDER}", flush=True)
    print(f"📂 OUTPUT_FOLDER: {OUTPUT_FOLDER}", flush=True)

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"✅ Created directory: {OUTPUT_FOLDER}")

    if not os.path.exists(INPUT_FOLDER):
        print(f"❌ Error: Input folder '{INPUT_FOLDER}' does not exist.")
        return

    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".csv")]
    print(f"🔍 Found {len(files)} CSV files.")

    for filename in files:
        file_path = os.path.join(INPUT_FOLDER, filename)
        
        try:
            # Thêm engine='python' để support unicode filename tốt hơn
            try:
                df = pd.read_csv(file_path, encoding='utf-8', engine='python')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='utf-16', engine='python')
            
            df.columns = [c.strip().lower() for c in df.columns]
            
            # Debug columns
            print(f"📄 Processing: {filename}")
            print(f"📊 Columns found: {df.columns.tolist()}", flush=True)
            
            questions = []
            for index, row in df.iterrows():
                # Mapping mới dựa trên file thực tế
                # QuestionContent -> question
                # AAnswer -> a, BAnswer -> b ...
                
                q_text = str(row.get('questioncontent', row.get('question', row.get('câu hỏi', '')))).strip()
                
                options = []
                # Map AAnswer -> A, BAnswer -> B, etc.
                for opt_key, col_name in [('A', 'aanswer'), ('B', 'banswer'), ('C', 'canswer'), ('D', 'danswer')]:
                    # Fallback to 'a', 'b', 'c', 'd' if 'aanswer' not found
                    val = row.get(col_name, row.get(opt_key.lower(), row.get(f"{opt_key.lower()}ansver")))
                    if pd.notna(val):
                        options.append({
                            "key": opt_key,
                            "text": str(val).strip()
                        })
                
                # Correct Answer
                # CSV có cột 'Answer' (chứa 'B') và 'ResultAnswer' (chứa nội dung). Ta lấy 'Answer'.
                correct = str(row.get('answer', '')).strip().upper()
                if len(correct) > 1: correct = correct[-1] # Handle if format is "B. Content"

                q_obj = {
                    "id": f"{generate_concept_id(filename)}_{index}",
                    "type": "multiple_choice",
                    "content": q_text,
                    "options": options,
                    "correct_answer": correct,
                    "explanation": str(row.get('explanation', row.get('explain', row.get('giải thích', '')))).strip(),
                    "pkt_tags": {"difficulty": 0.5, "bloom_level": "understand", "avg_time_sec": 30}
                }
                questions.append(q_obj)

            final_json = {
                "metadata": {
                    "concept_id": generate_concept_id(filename),
                    "concept_name": filename.replace('.csv', ''),
                    "file_source": filename
                },
                "questions": questions
            }

            output_filename = filename.replace('.csv', '.json')
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_json, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Converted: {filename}")
            
        except Exception as e:
            print(f"❌ Error converting {filename}: {e}")

if __name__ == "__main__":
    with open("conversion.log", "w", encoding="utf-8") as log_file:
        sys.stdout = log_file
        sys.stderr = log_file
        convert_csv_to_json()
