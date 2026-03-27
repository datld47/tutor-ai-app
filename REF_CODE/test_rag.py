from knowledge_base import query_knowledge_base
import time

def test():
    print("🔍 Testing RAG Retrieval...")
    query = "Thương mại điện tử theo nghĩa hẹp là gì?"
    results = query_knowledge_base(query, n_results=5)
    
    found_quiz = False
    found_script = False
    
    print(f"\nQUERY: '{query}'\n")
    for r in results:
        meta = r['metadata']
        m_type = meta.get('type', 'unknown')
        src = meta.get('source', 'unknown')
        print(f"[{m_type.upper()}] {src}: {r['text'][:100]}...")
        
        if m_type == 'quiz_explanation': found_quiz = True
        if m_type == 'lecture_script': found_script = True
        
    print("\n" + "="*30)
    if found_quiz: print("✅ Quiz Data Found!")
    else: print("❌ Quiz Data MISSING.")
    
    if found_script: print("✅ Script Data Found!")
    else: print("❌ Script Data MISSING.")

if __name__ == "__main__":
    test()
