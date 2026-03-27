import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import json
import re
from pypdf import PdfReader

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_PATH = os.path.join(BASE_DIR, 'DB', 'vector_store')

# Paths to Data Sources
PDF_DIR = os.path.join(BASE_DIR, 'DB', 'Combine all ebooks')
VIDEO_DIR = os.path.join(BASE_DIR, 'DB', 'Video')
JSON_DIR = os.path.join(BASE_DIR, 'DB', 'JSON_Data')

# Force Local Embeddings (Fast & Free)
print("⚠️ Using Local Embeddings (all-MiniLM-L6-v2)...")
embedding_func = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def get_db_client():
    return chromadb.PersistentClient(path=VECTOR_DB_PATH)

def get_collection(client, reset=False):
    if reset:
        try:
            client.delete_collection("course_knowledge")
            print("🗑️ Deleted old collection.")
        except:
            pass
    
    return client.get_or_create_collection(
        name="course_knowledge",
        embedding_function=embedding_func
    )

# --- INGESTION LOGIC ---

def ingest_pdfs(collection):
    print("\n📚 Processing PDFs...")
    if not os.path.exists(PDF_DIR):
        print("❌ PDF Directory not found.")
        return 0

    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
    total_added = 0
    
    for filename in pdf_files:
        filepath = os.path.join(PDF_DIR, filename)
        print(f"   - Reading {filename}...")
        try:
            reader = PdfReader(filepath)
            text_chunks = []
            metadatas = []
            ids = []
            
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if not text: continue
                
                # Simple Overlap Chunking
                chunk_size = 1000
                overlap = 200
                start = 0
                while start < len(text):
                    end = start + chunk_size
                    chunk = text[start:end]
                    if len(chunk) > 50:
                        text_chunks.append(chunk)
                        metadatas.append({"source": filename, "page": page_idx + 1, "type": "book"})
                        ids.append(f"book_{filename}_p{page_idx}_c{start}")
                    start += (chunk_size - overlap)
            
            if text_chunks:
                collection.upsert(documents=text_chunks, metadatas=metadatas, ids=ids)
                total_added += len(text_chunks)
                print(f"     -> Added {len(text_chunks)} chunks.")
        
        except Exception as e:
            print(f"     ❌ Error: {e}")
            
    return total_added

def ingest_scripts(collection):
    print("\n🎬 Processing Lecture Scripts (Videos)...")
    if not os.path.exists(VIDEO_DIR):
        print("❌ Video Directory not found.")
        return 0
        
    total_added = 0
    
    # Walk through all subfolders
    for root, dirs, files in os.walk(VIDEO_DIR):
        if "script.txt" in files:
            script_path = os.path.join(root, "script.txt")
            folder_name = os.path.basename(root) # e.g., Chuong_1_Tiet_1
            
            print(f"   - Found script in: {folder_name}")
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split by Lines or Speakers, but simple chunking is often safer for RAG
                # Let's clean up speaker labels first? No, keep them for context.
                
                chunk_size = 800
                overlap = 150
                start = 0
                
                text_chunks = []
                metadatas = []
                ids = []
                
                while start < len(content):
                    end = start + chunk_size
                    chunk = content[start:end]
                    
                    if len(chunk) > 50:
                        text_chunks.append(chunk)
                        metadatas.append({
                            "source": f"Bài giảng {folder_name}", 
                            "page": 0, 
                            "type": "lecture_script"
                        })
                        ids.append(f"script_{folder_name}_{start}")
                    
                    start += (chunk_size - overlap)
                
                if text_chunks:
                    collection.upsert(documents=text_chunks, metadatas=metadatas, ids=ids)
                    total_added += len(text_chunks)
                    print(f"     -> Added {len(text_chunks)} chunks.")
                    
            except Exception as e:
                print(f"     ❌ Error reading script: {e}")
                
    return total_added

def ingest_quizzes(collection):
    print("\n🧠 Processing Quiz Explanations (JSON)...")
    if not os.path.exists(JSON_DIR):
        print("❌ JSON Directory not found.")
        return 0
    
    json_files = [f for f in os.listdir(JSON_DIR) if f.lower().endswith('.json')]
    total_added = 0
    
    for filename in json_files:
        filepath = os.path.join(JSON_DIR, filename)
        # print(f"   - Reading {filename}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            concept_name = data.get('metadata', {}).get('concept_name', filename)
            questions = data.get('questions', [])
            
            text_chunks = []
            metadatas = []
            ids = []
            
            for q in questions:
                # Format: Question + Correct Answer + Explanation
                # This is "Gold" knowledge
                content = f"""
                [HỎI THI / KIẾN THỨC]
                Chủ đề: {concept_name}
                Câu hỏi: {q['content']}
                Đáp án đúng: {q.get('correct_answer', '?')}
                Giải thích chi tiết: {q.get('explanation', 'Không có giải thích')}
                """
                
                text_chunks.append(content.strip())
                metadatas.append({
                    "source": filename, 
                    "page": 0, 
                    "type": "quiz_explanation"
                })
                ids.append(f"quiz_{q['id']}")
            
            if text_chunks:
                collection.upsert(documents=text_chunks, metadatas=metadatas, ids=ids)
                total_added += len(text_chunks)
                # print(f"     -> Added {len(text_chunks)} quiz items.")
                
        except Exception as e:
            print(f"     ❌ Error in {filename}: {e}")
            
    print(f"   -> Processed {len(json_files)} JSON files. Total Quiz Items: {total_added}")
    return total_added

def main():
    print("🚀 STARTING FULL KNOWLEDGE INGESTION...")
    
    client = get_db_client()
    collection = get_collection(client, reset=True) # Full reset to ensure clean state
    
    count_pdf = ingest_pdfs(collection)
    count_script = ingest_scripts(collection)
    count_quiz = ingest_quizzes(collection)
    
    total = count_pdf + count_script + count_quiz
    print("\n" + "="*50)
    print(f"✅ INGESTION COMPLETE!")
    print(f"📚 PDFs: {count_pdf} chunks")
    print(f"🎬 Scripts: {count_script} chunks")
    print(f"🧠 Quizzes: {count_quiz} items")
    print(f"running total: {total} knowledge units")
    print("="*50)

if __name__ == "__main__":
    main()
