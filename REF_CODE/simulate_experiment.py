import random
import pandas as pd
import matplotlib.pyplot as plt
from pkt_engine import StudentState

# Định nghĩa các Hồ sơ Người học (Personas)
PROFILES = {
    "The Star": {"accuracy": 0.9, "stamina": 1.2, "learning_rate": 1.5},    # Học giỏi, ít mệt
    "The Struggler": {"accuracy": 0.4, "stamina": 0.8, "learning_rate": 0.8}, # Học yếu, nhanh mệt
    "The Grinder": {"accuracy": 0.6, "stamina": 2.0, "learning_rate": 1.0},   # Cần cù bù thông minh
}

def run_simulation(profile_name, steps=50):
    params = PROFILES[profile_name]
    # Mock user_db_id for simulation
    student = StudentState(user_db_id=random.randint(1000, 9999))
    
    data_log = []
    
    for t in range(steps):
        # 1. Giả lập làm bài
        # Xác suất đúng dựa trên accuracy cơ bản + độ mệt mỏi
        current_fatigue = student.current_fatigue
        effective_accuracy = params["accuracy"] * (1 - current_fatigue * 0.5)
        is_correct = random.random() < effective_accuracy
        
        # 2. Giả lập cảm xúc (Phụ thuộc kết quả)
        if is_correct:
            sentiment = "neutral" if random.random() > 0.3 else "excited"
        else:
            sentiment = "frustrated" if random.random() > 0.5 else "confused"
            
        # 3. Đưa vào PKT Engine
        # Giả sử concept_id thay đổi tuần tự hoặc ngẫu nhiên
        concept_id = f"C1_T{random.randint(1, 10)}"
        student.process_interaction(concept_id, is_correct, sentiment, difficulty=0.5)
        
        # 4. Giả lập Healing Mode (Nếu Engine kích hoạt)
        if student.current_fatigue > 0.8:
            # Nghỉ ngơi 3 bước thời gian
            student.current_fatigue = 0.2 # Hồi phục
            data_log.append({"step": t, "fatigue": 0.8, "mastery": student.get_mastery(concept_id), "event": "HEALING"})
        
        data_log.append({
            "step": t, 
            "fatigue": student.current_fatigue, 
            "mastery": student.get_mastery(concept_id), 
            "event": "study"
        })
        
    return pd.DataFrame(data_log)

def plot_results():
    plt.figure(figsize=(12, 6))
    
    for name in PROFILES.keys():
        df = run_simulation(name)
        plt.plot(df['step'], df['fatigue'], label=f"{name} (Fatigue)")
        # Có thể vẽ thêm Mastery đường nét đứt
    
    plt.title("Mô phỏng Động lực học Tải Nhận thức (Bio-Cybernetic Simulation)")
    plt.xlabel("Interaction Steps")
    plt.ylabel("Fatigue / Cognitive Load")
    plt.axhline(y=0.8, color='r', linestyle='--', label='Burnout Threshold')
    plt.legend()
    plt.grid(True)
    plt.savefig("simulation_results.png")
    print("✅ Đã xuất biểu đồ mô phỏng: simulation_results.png")

if __name__ == "__main__":
    plot_results()
