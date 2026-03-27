from datetime import datetime
import pandas as pd
import os

def generate_report(user_id, student_history):
    """
    Input: student_history (List of dicts từ PKT Engine)
    Output: Chuỗi LaTeX hoàn chỉnh
    """
    df = pd.DataFrame(student_history)
    
    # Tính thống kê
    total_time = len(df) * 2 # Giả sử mỗi step 2 phút
    avg_mastery = df['mastery'].mean() if 'mastery' in df and not df.empty else 0
    healing_count = len(df[df['event'] == 'HEALING']) if 'event' in df else 0
    
    latex_content = f"""
    \\documentclass{{article}}
    \\usepackage{{graphicx}}
    \\usepackage[utf8]{{inputenc}}
    \\begin{{document}}
    
    \\title{{Báo cáo Cá nhân hóa: {user_id}}}
    \\date{{{datetime.now().strftime('%Y-%m-%d')}}}
    \\maketitle
    
    \\section{{Tổng quan Hiệu suất}}
    Sinh viên đã hoàn thành phiên học với các chỉ số sau:
    \\begin{{itemize}}
        \\item Tổng thời gian tương tác: {total_time} phút
        \\item Mức độ thành thạo trung bình: {avg_mastery:.2f}
        \\item Số lần kích hoạt Healing Mode: {healing_count}
    \\end{{itemize}}
    
    \\section{{Phân tích Chi tiết}}
    Dưới đây là bảng dữ liệu 5 tương tác cuối cùng:
    
    \\begin{{table}}[h]
    \\centering
    \\begin{{tabular}}{{|c|c|c|}}
    \\hline
    Step & Mastery & Fatigue \\\\
    \\hline
    """
    
    # Thêm dòng dữ liệu vào bảng
    if not df.empty:
        for idx, row in df.tail(5).iterrows():
            latex_content += f"{row.get('step', 'N/A')} & {row.get('mastery', 0):.2f} & {row.get('fatigue', 0):.2f} \\\\\n\\hline\n"
        
    latex_content += """
    \\end{tabular}
    \\caption{Nhật ký tương tác gần nhất}
    \\end{table}
    
    \\end{document}
    """
    
    filename = f"report_{user_id}.tex"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(latex_content)
    
    print(f"✅ Đã tạo file báo cáo LaTeX: {filename}")
