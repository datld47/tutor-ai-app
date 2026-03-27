import os
import chromadb
from pypdf import PdfReader
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction
from gemini_helper import get_gemini_api_key

# Ensure NLTK data (optional, for better sentence splitting if needed, here we use simple split)
# import nltk
# nltk.download('punkt')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, 'DB', 'Combine all ebooks')
VECTOR_DB_PATH = os.path.join(BASE_DIR, 'DB', 'vector_store')

# Configure Embedding Function (Using Gemini if API key present, else Default)
# Configure Embedding Function (Force Local)
print("⚠️ Forcing Default Local Embeddings (all-MiniLM-L6-v2) to avoid API 404 errors")
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
embedding_func = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def ingest_pdfs():
    print("📂 Starting PDF Ingestion...")
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    
    # Check Embedding Mode Consistency
    config_path = os.path.join(BASE_DIR, 'DB', 'embedding_config.json')
    # current_mode = "gemini" if google_api_key else "local"
    current_mode = "local" # Force local mode as we are using local embeddings
    
    should_rebuild = False
    if os.path.exists(config_path):
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
            if config.get("mode") != current_mode:
                print(f"⚠️ Embedding mode changed ({config.get('mode')} -> {current_mode}). Rebuilding DB...")
                should_rebuild = True
    else:
        # First run or missing config
        should_rebuild = False # Let the count check decide, unless we want to enforce config creation

    if should_rebuild:
        try:
            client.delete_collection("course_knowledge")
            print("🗑️ Deleted old collection.")
        except:
            pass

    # Create or Get Collection
    # metadata={"hnsw:space": "cosine"} usually good for text
    collection = client.get_or_create_collection(
        name="course_knowledge",
        embedding_function=embedding_func
    )
    
    # Save current config
    import json
    with open(config_path, 'w') as f:
        json.dump({"mode": current_mode}, f)
    
    # Check if we should skip (simple check: if collection has items)
    if collection.count() > 0 and not should_rebuild:
        print(f"ℹ️ Collection already has {collection.count()} items. Skipping full re-ingestion.")
        return 

    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("❌ No PDF files found in", PDF_DIR)
        return

    total_chunks = 0
    
    for filename in pdf_files:
        filepath = os.path.join(PDF_DIR, filename)
        print(f"📖 Processing: {filename}...")
        
        try:
            reader = PdfReader(filepath)
            text_chunks = []
            metadatas = []
            ids = []
            
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if not text: continue
                
                # Simple Chunking: Split by paragraphs or rough character count
                # Here: Overlap chunking 1000 chars with 200 overlap
                chunk_size = 1000
                overlap = 200
                
                start = 0
                while start < len(text):
                    end = start + chunk_size
                    chunk = text[start:end]
                    
                    if len(chunk) > 50: # Ignore tiny chunks
                        text_chunks.append(chunk)
                        metadatas.append({
                            "source": filename,
                            "page": page_idx + 1
                        })
                        ids.append(f"{filename}_p{page_idx}_c{start}")
                    
                    start += (chunk_size - overlap)
            
            # Upsert to DB
            if text_chunks:
                print(f"   -> Found {len(text_chunks)} chunks. Indexing...")
                # Batch processing if needed, but for small inputs straight add is fine
                collection.upsert(
                    documents=text_chunks,
                    metadatas=metadatas,
                    ids=ids
                )
                total_chunks += len(text_chunks)
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

    print(f"✅ Ingestion Complete! Total Chunks Indexed: {total_chunks}")
    print(f"💾 Vector DB saved to: {VECTOR_DB_PATH}")

if __name__ == "__main__":
    ingest_pdfs()
