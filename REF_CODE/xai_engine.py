# xai_engine.py

# Placeholder for Prerequisites, ideally loaded from course_metadata or a similar source
PREREQUISITES = {} 

def explain_recommendation(concept_id, student_state):
    """
    Sinh ra lời giải thích dựa trên logic GAKT và CLADC
    """
    # 1. Kiểm tra tiên quyết
    prereqs = PREREQUISITES.get(concept_id, [])
    weak_prereqs = []
    for p in prereqs:
        if student_state.get_mastery(p) < 0.6:
            weak_prereqs.append(p)
            
    # 2. Kiểm tra tải nhận thức
    fatigue = student_state.current_fatigue
    
    # 3. Tổng hợp lời giải thích
    reasons = []
    
    if not weak_prereqs:
        reasons.append("✅ Bạn đã nắm vững các kiến thức nền tảng.")
    else:
        reasons.append(f"⚠️ Bạn cần củng cố kiến thức: {', '.join(weak_prereqs)}.")
        
    if fatigue > 0.6:
        reasons.append("📉 Năng lượng não bộ đang thấp, hệ thống chọn bài này vì nó có nhiều Video (dễ tiếp thu) hơn là bài tập.")
    else:
        reasons.append("🚀 Năng lượng đang cao, đây là thời điểm vàng để chinh phục kiến thức mới!")
        
    return "\n".join(reasons)
