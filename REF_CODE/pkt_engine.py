from database import engine, Session, select, KnowledgeState, log_interaction
from datetime import datetime

class StudentState:
    def __init__(self, user_db_id):
        self.user_db_id = user_db_id
        self.current_fatigue = 0.0
        self.current_concept_id = None
        self.quiz_history = {} # {concept_id: {question_idx: 'correct'/'wrong'}}
        # Load Elo từ DB khi khởi tạo
        self.knowledge_cache = self._load_from_db()

    def _load_from_db(self):
        """Đọc trạng thái từ DB lên Cache"""
        cache = {}
        with Session(engine) as session:
            statement = select(KnowledgeState).where(KnowledgeState.user_id == self.user_db_id)
            results = session.exec(statement)
            for row in results:
                cache[row.concept_id] = row.elo_rating
        return cache

    def get_elo(self, concept_id):
        return self.knowledge_cache.get(concept_id, 1200.0)
    
    def get_mastery(self, concept_id):
        # Convert Elo to 0.0 - 1.0 scale for visualization
        # Elo 2000 -> 1.0, Elo 1200 -> 0.5, Elo 400 -> 0.0
        elo = self.get_elo(concept_id)
        return max(0.0, min(1.0, (elo - 400) / 1600))

    def update_elo(self, concept_id, is_correct, sentiment="neutral"):
        # 1. Tính toán Elo (Logic cũ giữ nguyên)
        current_elo = self.get_elo(concept_id)
        expected = 1 / (1 + 10 ** ((1200 - current_elo) / 400)) # Giả sử độ khó tb = 1200
        actual = 1.0 if is_correct else 0.0
        k_factor = 32
        new_elo = current_elo + k_factor * (actual - expected)
        
        # 2. Cập nhật Cache (RAM)
        self.knowledge_cache[concept_id] = new_elo
        
        # 3. Cập nhật DB (Disk) - Upsert
        with Session(engine) as session:
            statement = select(KnowledgeState).where(
                KnowledgeState.user_id == self.user_db_id,
                KnowledgeState.concept_id == concept_id
            )
            record = session.exec(statement).first()
            
            if not record:
                record = KnowledgeState(user_id=self.user_db_id, concept_id=concept_id)
            
            record.elo_rating = new_elo
            record.last_review = datetime.now()
            
            session.add(record)
            session.commit()
            
        # Update Fatigue based on sentiment and result
        self.update_fatigue(sentiment, is_correct)

        # 4. Ghi Log chi tiết hành vi
        log_interaction(
            user_id=self.user_db_id,
            concept=concept_id,
            action="quiz_attempt",
            mastery=new_elo,
            fatigue=self.current_fatigue,
            sentiment=sentiment,
            details_dict={"correct": is_correct, "expected_score": expected}
        )
        
        return new_elo

    def update_fatigue(self, sentiment, is_correct):
        fatigue_increment = 0.05
        if sentiment == "frustrated": fatigue_increment = 0.15
        if sentiment == "bored": fatigue_increment = 0.1
        if sentiment == "excited": fatigue_increment = -0.05 # Hồi phục năng lượng
        
        self.current_fatigue = max(0.0, min(1.0, self.current_fatigue + fatigue_increment))

    def process_interaction(self, concept_id, correctness, sentiment, difficulty=0.5):
        # Wrapper for update_elo to match previous logic structure if needed
        new_elo = self.update_elo(concept_id, correctness, sentiment)
        return {
            "mastery": self.get_mastery(concept_id),
            "fatigue": self.current_fatigue,
            "recommendation": self._get_recommendation()
        }

    def _get_recommendation(self):
        """Logic của CLADC: Quyết định hành động tiếp theo"""
        if self.current_fatigue > 0.8:
            return "REST" # Bắt buộc nghỉ ngơi
        if self.current_fatigue > 0.6:
            return "VIDEO" # Chuyển sang thụ động (xem video) để giảm tải
        return "QUIZ" # Tiếp tục thử thách

    def to_dict(self):
        """Serialize state for storage"""
        return {
            "user_db_id": self.user_db_id,
            "current_fatigue": self.current_fatigue,
            "current_concept_id": self.current_concept_id,
            "quiz_history": self.quiz_history,
            "last_fatigue_update": datetime.now().strftime("%Y-%m-%d")
        }

    @classmethod
    def from_dict(cls, data):
        """Restore state from storage"""
        instance = cls(data["user_db_id"])
        instance.current_fatigue = data.get("current_fatigue", 0.0)
        instance.current_concept_id = data.get("current_concept_id")
        
        # Restore and Migrate Quiz History
        raw_history = data.get("quiz_history", {})
        migrated_history = {}
        
        for cid, questions in raw_history.items():
            migrated_history[cid] = {}
            for qid, val in questions.items():
                if isinstance(val, str):
                    # Migration: 'correct' -> {'correct': 1, 'wrong': 0}
                    if val == 'correct':
                        migrated_history[cid][qid] = {'correct': 1, 'wrong': 0}
                    else:
                        migrated_history[cid][qid] = {'correct': 0, 'wrong': 1}
                else:
                    migrated_history[cid][qid] = val
                    
        instance.quiz_history = migrated_history
        
        # --- DAILY RESET LOGIC ---
        last_update_str = data.get("last_fatigue_update")
        if not last_update_str:
            # Handle legacy data or new user without date -> Reset to 0.0
            instance.current_fatigue = 0.0
        else:
            last_date = datetime.strptime(last_update_str, "%Y-%m-%d").date()
            if datetime.now().date() > last_date:
                instance.current_fatigue = 0.0 # Reset for new day
        
        return instance
