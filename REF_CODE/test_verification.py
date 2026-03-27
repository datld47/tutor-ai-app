import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

async def run_verification():
    print("🚀 Starting Verification...")
    
    # 1. Test Data Manager
    print("\n[1] Testing Data Manager...")
    try:
        from data_manager import data_manager
        concepts = data_manager.get_all_concepts()
        print(f"✅ Data Loaded: {len(concepts)} concepts found.")
    except Exception as e:
        print(f"❌ Data Manager Failed: {e}")

    # 2. Test Database & Models
    print("\n[2] Testing Database & PKT Engine...")
    try:
        from database import create_db_and_tables
        create_db_and_tables()
        from pkt_engine import StudentState
        student = StudentState(user_db_id=999)
        elo = student.get_elo("test_concept")
        print(f"✅ StudentState Initialized. Default Elo: {elo}")
    except Exception as e:
         print(f"❌ Database/PKT Failed: {e}")

    # 3. Test Deep Tech Services
    print("\n[3] Testing Services (Prediction, RAG)...")
    try:
        from services.prediction_service import prediction_service
        prob = prediction_service.predict_next_performance(999, "test_concept")
        print(f"✅ Prediction Service Warning: Win Prob = {prob}")
        
        from services.query_transform_service import query_transform_service
        # Mocking genai for test if no key
        if not os.environ.get("GOOGLE_API_KEY"):
            print("⚠️ No API Key found, skipping actual API calls.")
        else:
            rewritten = await query_transform_service.rewrite_query("Nó là gì?", "User: GAKT là gì?\nAI: Là thuật toán...")
            print(f"✅ Query Transform: {rewritten}")
            
    except Exception as e:
        print(f"❌ Services Failed: {e}")

    print("\n✅ Verification Complete.")

if __name__ == "__main__":
    asyncio.run(run_verification())
