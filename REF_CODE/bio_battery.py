from nicegui import ui

class BioBattery:
    def __init__(self, container):
        with container:
            # Sử dụng HTML/CSS để vẽ viên pin
            self.battery_container = ui.html('''
                <div id="bio-battery" style="
                    width: 50px; height: 25px; 
                    border: 2px solid #333; border-radius: 4px; 
                    padding: 2px; position: relative;
                ">
                    <div id="battery-level" style="
                        width: 100%; height: 100%; 
                        background: #4caf50; border-radius: 2px;
                        transition: width 0.5s, background 0.5s;
                    "></div>
                    <div style="
                        position: absolute; right: -6px; top: 6px; 
                        width: 4px; height: 10px; 
                        background: #333; border-radius: 0 2px 2px 0;
                    "></div>
                </div>
            ''')
            self.label = ui.label('100%').classes('text-xs font-bold mt-1 text-center w-full')

    def update(self, fatigue_level):
        """
        fatigue_level: 0.0 (Khỏe) -> 1.0 (Kiệt sức)
        Energy = 1.0 - fatigue
        """
        energy = max(0, min(1, 1.0 - fatigue_level))
        percentage = int(energy * 100)
        
        # Đổi màu dựa trên mức năng lượng
        color = '#4caf50' # Green
        if energy < 0.5: color = '#ff9800' # Orange
        if energy < 0.2: color = '#f44336' # Red
        
        # Animation rung lắc khi pin yếu (< 20%)
        animation = "animation: shake 0.5s infinite;" if energy < 0.2 else ""
        
        # Cập nhật CSS qua JS
        ui.run_javascript(f'''
            var level = document.getElementById('battery-level');
            var batt = document.getElementById('bio-battery');
            if (level) {{
                level.style.width = '{percentage}%';
                level.style.background = '{color}';
            }}
            if (batt) {{
                batt.style.cssText += '{animation}';
            }}
        ''')
        
        self.label.set_text(f'{percentage}%')
        
        # Thêm CSS rung lắc vào head (chỉ chạy 1 lần)
        ui.add_head_html('''
            <style>
            @keyframes shake {
              0% { transform: translate(1px, 1px) rotate(0deg); }
              10% { transform: translate(-1px, -2px) rotate(-1deg); }
              20% { transform: translate(-3px, 0px) rotate(1deg); }
              30% { transform: translate(3px, 2px) rotate(0deg); }
              40% { transform: translate(1px, -1px) rotate(1deg); }
              50% { transform: translate(-1px, 2px) rotate(-1deg); }
              60% { transform: translate(-3px, 1px) rotate(0deg); }
              70% { transform: translate(3px, 1px) rotate(-1deg); }
              80% { transform: translate(-1px, -1px) rotate(1deg); }
              90% { transform: translate(1px, 2px) rotate(0deg); }
              100% { transform: translate(1px, -2px) rotate(-1deg); }
            }
            </style>
        ''')
