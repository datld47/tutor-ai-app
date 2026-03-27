import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_PATH = os.path.join(BASE_DIR, 'DB', 'vector_store')

def check_db():
    print("🔍 Verifying Vector DB...")
    embedding_func = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    
    try:
        collection = client.get_collection(name="course_knowledge", embedding_function=embedding_func)
        count = collection.count()
        print(f"✅ Total Items in DB: {count}")
        
        # Check Distribution
        results = collection.get(include=['metadatas'])
        metas = results['metadatas']
        
        types = {}
        for m in metas:
            t = m.get('type', 'unknown')
            types[t] = types.get(t, 0) + 1
            
        print("\n📊 Content Breakdown:")
        for t, c in types.items():
            print(f"   - {t}: {c} items")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_db()
