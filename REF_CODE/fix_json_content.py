import os
import json
import csv
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Absolute paths
INPUT_FOLDER = r"d:\MY_CODE\WebPersionalLearning\DB\TMDT_Chuong1"
OUTPUT_FOLDER = r"d:\MY_CODE\WebPersionalLearning\DB\JSON_Data"

def generate_concept_id(filename):
    # Simple ID generation
    name = filename.replace('.csv', '')
    # Try to keep it somewhat consistent or just use the filename as base
    # Clean up spaces for ID
    clean_id = name.replace(' ', '').replace('_', '')
    return clean_id[:20]

def fix_content():
    log_path = os.path.join(os.getcwd(), "fix_debug.txt")
    with open(log_path, "w", encoding="utf-8") as log:
        def log_print(msg):
            print(msg)
            log.write(msg + "\n")
            
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)
            
        files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.csv')]
        log_print(f"Found {len(files)} CSV files.")
        
        for filename in files:
            csv_path = os.path.join(INPUT_FOLDER, filename)
            json_path = os.path.join(OUTPUT_FOLDER, filename.replace('.csv', '.json'))
            
            log_print(f"Processing {filename}...")
            
            questions = []
            
            # Try encodings
            encodings = ['utf-8-sig', 'utf-16', 'utf-8', 'cp1252', 'latin1']
            success_read = False
            rows = []
            headers = []
            
            for enc in encodings:
                try:
                    with open(csv_path, 'r', encoding=enc) as f:
                        # Inspect first line
                        sample = f.read(1024)
                        f.seek(0)
                        if '\x00' in sample: # likely utf-16
                            if enc == 'utf-8': continue
                            
                        reader = csv.DictReader(f)
                        headers = [h.strip().lower() for h in (reader.fieldnames or [])]
                        rows = list(reader)
                        
                        # Validate if it looks like a CSV
                        if len(headers) > 1:
                            log_print(f"  Matches encoding: {enc}")
                            log_print(f"  Headers: {headers}")
                            success_read = True
                            break
                except Exception as e:
                    continue
            
            if not success_read:
                log_print(f"  ❌ Failed to read {filename} with any encoding")
                continue

            for idx, row in enumerate(rows):
                # Normalized mapping
                # Normalize row keys too
                row_norm = {k.strip().lower(): v for k, v in row.items() if k}
                
                content = row_norm.get('questioncontent', row_norm.get('question', '')).strip()
                if not content: # Fallback
                     for k, v in row_norm.items():
                         if 'question' in k and v:
                             content = v.strip()
                             break
                
                options = []
                for key in ['a', 'b', 'c', 'd']:
                    opt_text = ''
                    # Try direct match
                    opt_text = row_norm.get(f'{key}answer', row_norm.get(key, '')).strip()
                    # Try fuzzy
                    if not opt_text:
                        for k, v in row_norm.items():
                            if key in k and 'answer' in k and v:
                                opt_text = v.strip()
                                break
                    if opt_text:
                        options.append({'key': key.upper(), 'text': opt_text})
                
                correct = ''
                # Try finding answer column
                for k, v in row_norm.items():
                    if 'answer' in k and 'result' not in k and len(v.strip()) < 5:
                         correct = v.strip().upper()
                         break
                if not correct:
                     correct = row_norm.get('answer', '').strip().upper()

                if len(correct) > 1: correct = correct[0]
                
                explanation = row_norm.get('explanation', row_norm.get('explain', '')).strip()
                if not explanation:
                     for k, v in row_norm.items():
                         if 'explain' in k or 'explanation' in k:
                             explanation = v.strip()
                             break
                if not explanation: explanation = "Chưa có giải thích chi tiết."

                q_obj = {
                    "id": f"{generate_concept_id(filename)}_{idx}",
                    "type": "multiple_choice",
                    "content": content,
                    "options": options,
                    "correct_answer": correct,
                    "explanation": explanation,
                     "pkt_tags": {"difficulty": 0.5, "bloom_level": "understand", "avg_time_sec": 30}
                }
                questions.append(q_obj)
            
            # Write JSON
            final_data = {
                "metadata": {
                    "concept_id": generate_concept_id(filename),
                    "concept_name": filename.replace('.csv', ''),
                    "file_source": filename
                },
                "questions": questions
            }
            
            with open(json_path, 'w', encoding='utf-8') as jf:
                json.dump(final_data, jf, ensure_ascii=False, indent=2)
            log_print(f"  ✅ Saved {len(questions)} questions")

if __name__ == "__main__":
    fix_content()
