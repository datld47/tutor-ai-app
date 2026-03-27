from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select
from datetime import datetime
import json
import os

# --- ĐỊNH NGHĨA BẢNG (TABLES) ---

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    full_name: str
    role: str = "student" # student, researcher, admin
    group: str = "control" # control (đối chứng) vs experimental (thực nghiệm)
    created_at: datetime = Field(default_factory=datetime.now)

class InteractionLog(SQLModel, table=True):
    """Bảng này lưu từng click chuột, từng câu chat"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    timestamp: datetime = Field(default_factory=datetime.now)
    concept_id: str
    action_type: str # quiz_answer, chat_query, video_pause, tab_switch
    
    # Các chỉ số quan trọng cho Bio-PKT
    mastery_score: float = 0.0
    fatigue_level: float = 0.0
    sentiment: str = "neutral"
    
    # Lưu chi tiết (JSON string) để phân tích sâu sau này
    details: str = "{}" 

class KnowledgeState(SQLModel, table=True):
    """Lưu trạng thái hiện tại (Snapshot) để resume khi user đăng nhập lại"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    concept_id: str
    elo_rating: float = 1200.0
    last_review: datetime = Field(default_factory=datetime.now)

# --- CẤU HÌNH ENGINE ---
sqlite_file_name = "pkt_research.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- CÁC HÀM TIỆN ÍCH (CRUD) ---

def get_user_by_username(username: str):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        results = session.exec(statement)
        return results.first()

def create_user(username, password, full_name, role="student"):
    with Session(engine) as session:
        user = User(username=username, password=password, full_name=full_name, role=role)
        session.add(user)
        session.commit()
        return user

def log_interaction(user_id, concept, action, mastery, fatigue, sentiment, details_dict):
    with Session(engine) as session:
        log = InteractionLog(
            user_id=user_id,
            concept_id=concept,
            action_type=action,
            mastery_score=mastery,
            fatigue_level=fatigue,
            sentiment=sentiment,
            details=json.dumps(details_dict, ensure_ascii=False)
        )
        session.add(log)
        session.commit()
