import os
import chromadb
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction
from gemini_helper import get_gemini_api_key

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_PATH = os.path.join(BASE_DIR, 'DB', 'vector_store')

# Helper to get collection
def get_collection():
    # Force local embeddings to avoid API issues
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    embedding_func = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    try:
        client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
        return client.get_or_create_collection(
            name="course_knowledge",
            embedding_function=embedding_func
        )
    except Exception as e:
        print(f"Error accessing ChromaDB: {e}")
        return None

def query_knowledge_base(query, n_results=3):
    """
    Search in ChromaDB for relevant documents.
    """
    collection = get_collection()
    if not collection:
        print("❌ DB not found, returning empty.")
        return []
    
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        # Results structure: 
        # {'documents': [['text1', 'text2']], 'metadatas': [[{'source':..}, {'source':..}]]}
        
        formatted_results = []
        if results['documents']:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            
            for i in range(len(docs)):
                formatted_results.append({
                    "text": docs[i],
                    "metadata": metas[i]
                })
                
        return formatted_results

    except Exception as e:
        print(f"❌ Error querying DB: {e}")
        return []
