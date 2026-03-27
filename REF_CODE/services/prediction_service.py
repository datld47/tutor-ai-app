import torch
import torch.nn as nn
import torch.optim as optim
from models.dkt_model import DKT
from database import Session, engine, select, InteractionLog
import json # Import json to parse details

class PredictionService:
    def __init__(self):
        # Giả sử ta có 100 concept ID khác nhau (trong thực tế cần mapping chính xác)
        self.num_concepts = 100 
        self.model = DKT(num_concepts=self.num_concepts)
        
        # Optimizer để model "học" ngay lập tức sau mỗi lần tương tác
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.01)
        self.criterion = nn.BCELoss()
        
        # Load weights đã train (nếu có), ở đây ta khởi tạo ngẫu nhiên cho Demo
        self.model.eval()

    def _encode_history(self, logs):
        """Chuyển đổi log lịch sử thành chuỗi input cho LSTM"""
        # Logic DKT: Input = Concept_ID + (0 nếu sai, num_concepts nếu đúng)
        # Ví dụ: Concept 5 đúng -> Input 105. Concept 5 sai -> Input 5.
        
        sequence = []
        for log in logs:
            # Cần một hàm hash concept_id (string) sang int (0-99)
            # Ở đây giả lập hash đơn giản
            c_idx = abs(hash(log.concept_id)) % self.num_concepts
            
            # Lấy kết quả đúng sai từ details
            try:
                details = json.loads(log.details)
                is_correct = details.get("correct", False) # Correct key name based on pkt_engine.py
            except:
                is_correct = False
            
            # Mã hóa
            val = c_idx + (self.num_concepts if is_correct else 0)
            sequence.append(val)
            
        return torch.tensor([sequence], dtype=torch.long) # Batch size = 1

    def predict_next_performance(self, user_id, next_concept_id):
        """Dự đoán xác suất làm đúng bài tiếp theo"""
        with Session(engine) as session:
            # Lấy 20 tương tác gần nhất
            logs = session.exec(
                select(InteractionLog)
                .where(InteractionLog.user_id == user_id)
                .order_by(InteractionLog.timestamp)
            ).all()
            
            if not logs:
                return 0.5 # Cold start: Chưa có dữ liệu thì đoán 50/50

            input_seq = self._encode_history(logs)
            
            # Inference
            with torch.no_grad():
                output = self.model(input_seq)
            
            # Lấy dự đoán của bước cuối cùng
            last_step_pred = output[0, -1, :] 
            
            # Lấy xác suất của concept tiếp theo
            c_idx = abs(hash(next_concept_id)) % self.num_concepts
            probability = last_step_pred[c_idx].item()
            
            return probability

    def train_one_step(self, user_id, concept_id, is_correct):
        """
        Online Learning: Cập nhật trọng số mạng ngay sau khi sinh viên làm bài.
        """
        self.model.train()
        # (Trong thực tế cần code đoạn backpropagation lấy history làm input và next step làm label)
        print(f"🧠 [DKT Model] Đang cập nhật trọng số nơ-ron cho user {user_id}...")
        self.model.eval()

prediction_service = PredictionService()
