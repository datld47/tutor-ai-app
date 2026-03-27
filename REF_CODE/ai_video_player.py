from nicegui import ui, run
import re
import os
import asyncio
from utils import get_video_base_url
from gemini_helper import get_chat_model

class AIVideoPlayer:
    def __init__(self, container, concept_name, script_path):
        self.container = container
        self.concept_name = concept_name
        self.script_path = script_path
        self.base_url = get_video_base_url()
        # Normalize base url
        if not self.base_url.endswith('/'): self.base_url += '/'
        
        # Parse concept name to get folder: "Chương_1_Tiết 1..." -> "Chuong_1_Tiet_1"
        # Regex robust for "Chương...Tiết..." and "Chuong...Tiet"
        match = re.search(r'(?:Chương|Chuong)\D*(\d+)\D*(?:Tiết|Tiet)\D*(\d+)', concept_name, re.IGNORECASE)
        if match:
            self.folder_name = f"Chuong_{match.group(1)}_Tiet_{match.group(2)}"
            self.asset_base_url = f"{self.base_url}Video/{self.folder_name}/"
            print(f"[AIVidePlayer] Asset URL: {self.asset_base_url}")
        else:
            self.folder_name = "Unknown"
            self.asset_base_url = ""
            print(f"[AIVidePlayer] Could not parse concept: {concept_name}")

        self.slides = self.parse_script(script_path)
        
        # Load Video Links if available
        self.video_map = {}
        video_link_path = os.path.join(os.path.dirname(script_path), 'videoLink.txt')
        if os.path.exists(video_link_path):
            self.video_map = self.parse_video_links(video_link_path)
            
        self.current_slide_index = 0
        
        # Initialize AI
        self.chat_model = get_chat_model()
        self.chat_history_ui = None
        
        # Build UI
        self.build_ui()

    def parse_video_links(self, path):
        video_map = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            current_slide = None
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Match "Slide 6:"
                slide_match = re.match(r'^Slide\s+(\d+)[:\s]*', line, re.IGNORECASE)
                if slide_match:
                    current_slide = int(slide_match.group(1))
                    if current_slide not in video_map:
                         video_map[current_slide] = {'url': '', 'title': ''}
                elif current_slide is not None:
                     if line.startswith('http'):
                         video_map[current_slide]['url'] = line
                     elif line.startswith('Duration:'):
                         pass
                     else:
                         video_map[current_slide]['title'] = line
            print(f"[AIVideaPlayer] Loaded {len(video_map)} video links.")
        except Exception as e:
            print(f"Error parsing video links: {e}")
        return video_map

    def parse_script(self, path):
        slides = []
        try:
            if not os.path.exists(path):
                print(f"[AIVideoPlayer] Script not found: {path}")
                return []
                
            with open(path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # Basic parsing: Split by "Slide X:"
            current_slide = None
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Regex for "Slide 1:", "Slide 01", etc.
                match = re.match(r'^Slide\s+(\d+)[:\s]*(.*)$', line, re.IGNORECASE)
                if match:
                    # Save previous slide
                    if current_slide: slides.append(current_slide)
                    
                    current_slide = {
                        'id': int(match.group(1)),
                        'title': match.group(2),
                        'lines': []
                    }
                elif current_slide:
                    current_slide['lines'].append(line)
            
            # Append last slide
            if current_slide: slides.append(current_slide)
            
            print(f"[AIVideoPlayer] Parsed {len(slides)} slides from {path}")
            
        except Exception as e:
            print(f"[AIVideoPlayer] Error parsing script: {e}")
        
        return slides

    def build_ui(self):
        self.container.clear()
        if not self.slides:
            with self.container:
                ui.label(f"Không tìm thấy kịch bản hoặc lỗi định dạng tại: {self.script_path}").classes('text-red-500 font-bold')
            return

        # --- THEME CONFIG ---
        self.container.classes('p-0 gap-0 w-full h-[85vh] bg-gradient-to-br from-gray-900 via-slate-900 to-black text-white overflow-hidden relative shadow-2xl rounded-xl border border-white/10')
        
        with self.container:
             # Layout: Row (Image 70%, Sidebar 30%)
             with ui.row().classes('w-full h-full no-wrap gap-0'):
                 
                 # --- LEFT: CINEMA VIEW (Video/Slide) ---
                 with ui.column().classes('w-3/4 h-full items-center justify-center bg-black relative'):
                     # Main Visual
                     self.img = ui.image().classes('w-full h-full object-contain').props('no-spinner')
                     
                     # Video Element
                     self.video_player = ui.video(src='').classes('hidden w-full h-full max-h-full bg-black')
                     self.video_player.on('ended', self.next_slide)
                     
                     # Audio Element
                     self.audio = ui.audio(src='').classes('hidden')
                     self.audio.on('ended', self.next_slide)
                     
                     # Loading Spinner
                     self.spinner = ui.spinner('dots', size='3em', color='blue-400').classes('absolute')
                     self.img.on('load', lambda: self.spinner.set_visibility(False))
                     self.img.on('error', lambda: ui.notify('Lỗi tải ảnh slide', type='negative'))

                     # Floating Controls Bar (Glassmorphism - Darker for Contrast)
                     with ui.row().classes('absolute bottom-6 left-1/2 transform -translate-x-1/2 bg-black/60 backdrop-blur-md border border-white/20 rounded-full px-6 py-2 items-center gap-4 transition-all hover:bg-black/80 shadow-lg'):
                         
                         ui.button(icon='skip_previous', on_click=self.prev_slide).props('flat round color=white').classes('opacity-90 hover:opacity-100 hover:bg-white/10')
                         
                         self.btn_play = ui.button(icon='play_arrow', on_click=self.toggle_play).props('flat round color=white size=lg').classes('scale-110 hover:scale-125 transition-transform hover:text-blue-400')
                         
                         ui.button(icon='skip_next', on_click=self.next_slide).props('flat round color=white').classes('opacity-90 hover:opacity-100 hover:bg-white/10')
                         
                         ui.separator().props('vertical spaced').classes('bg-white/30 h-6')
                         
                         self.lbl_counter = ui.label('00 / 00').classes('font-mono text-xs text-blue-200 tracking-widest')
                         
                         ui.separator().props('vertical spaced').classes('bg-white/30 h-6')

                         # Toggles
                         with ui.row().classes('items-center gap-2 group'):
                            ui.label('Auto').classes('text-[10px] text-gray-300 uppercase tracking-wider font-bold')
                            self.switch_auto = ui.switch(value=True).props('dense color=blue size=xs')

                         with ui.row().classes('items-center gap-2 group'):
                            ui.label('AI Exam').classes('text-[10px] text-cyan-400 uppercase tracking-wider font-bold')
                            self.switch_examiner = ui.switch(value=False).props('dense color=cyan size=xs keep-color').tooltip('Chế độ AI kiểm tra bài')


                 # --- RIGHT: INTELLIGENT SIDEBAR ---
                 with ui.column().classes('w-1/4 h-full bg-gray-900 border-l border-white/10 p-0'):
                     
                     # Check: Use Splitter for robust Resizing/Visibility
                     with ui.splitter(horizontal=True, value=60).classes('w-full h-full') as right_splitter:
                         
                         # TOP: TRANSCRIPT
                         with right_splitter.before:
                             with ui.column().classes('w-full h-full flex flex-col relative group'):
                                # Header
                                with ui.row().classes('w-full items-center justify-between p-3 border-b border-white/10 bg-white/5'):
                                     with ui.row().classes('items-center gap-2'):
                                         ui.icon('description', color='blue-400').classes('text-lg')
                                         ui.label('TRANSCRIPT').classes('text-xs font-bold text-blue-100 tracking-wider opacity-80')
                                
                                # Content
                                with ui.scroll_area().classes('w-full flex-grow p-4') as self.scroll_area:
                                    self.script_container = ui.column().classes('w-full gap-3')
                     
                         # BOTTOM: AI TUTOR
                         with right_splitter.after:
                             with ui.column().classes('w-full h-full flex flex-col bg-slate-800/50'):
                                # Header
                                with ui.row().classes('w-full items-center justify-between p-3 border-b border-white/10 bg-blue-900/20'):
                                     with ui.row().classes('items-center gap-2'):
                                         ui.icon('smart_toy', color='cyan-400').classes('text-lg')
                                         ui.label('AI TUTOR').classes('text-xs font-bold text-cyan-100 tracking-wider')
                                         ui.badge('Online', color='green').props('floating dense rounded')

                                # Chat History
                                with ui.scroll_area().classes('w-full flex-grow p-3 gap-3') as self.chat_scroll:
                                    self.chat_container = ui.column().classes('w-full gap-3')
                                    # Welcome
                                    with self.chat_container:
                                        with ui.row().classes('w-full items-start gap-2'):
                                            ui.avatar(icon='smart_toy', color='cyan-900', text_color='cyan-200').classes('shadow-lg border border-cyan-500/30')
                                            ui.label('Chào bạn! Mình là AI Tutor. Hỏi mình bất cứ điều gì về bài học nhé!').classes('bg-slate-700/80 p-3 rounded-2xl rounded-tl-none text-sm leading-relaxed text-gray-100 shadow-sm border border-white/5')
                                
                                # Input
                                with ui.row().classes('w-full p-3 bg-black/20 border-t border-white/5 gap-2 items-center'):
                                    self.chat_input = ui.input(placeholder='Hỏi về slide này...').props('rounded outlined bg-color=grey-900 dense input-class="text-white"').classes('flex-grow text-white').on('keydown.enter', self.send_chat)
                                    ui.button(icon='send_sparkles', on_click=self.send_chat).props('round flat color=cyan').classes('shadow-lg hover:bg-cyan-900/50')

        # Use Timer to load first slide to ensure UI is ready
        ui.timer(0.1, lambda: self.load_slide(0), once=True)

        # --- PRE-CREATE DIALOGS (Styled) ---
        
        # 1. Processing Dialog
        with ui.dialog() as self.processing_dialog, ui.card().classes('bg-gray-900 border border-blue-500/50 items-center justify-center p-8 rounded-2xl shadow-2xl'):
             ui.spinner('orbit', size='3em', color='cyan-400')
             self.processing_label = ui.label('AI đang phân tích kiến thức...').classes('text-cyan-200 animate-pulse mt-4 font-bold tracking-wide')

        # 2. Quiz Dialog
        with ui.dialog() as self.quiz_dialog, ui.card().classes('w-full max-w-2xl bg-slate-900 border border-white/10 rounded-2xl shadow-2xl p-0 overflow-hidden'):
            # Header
            with ui.row().classes('w-full bg-gradient-to-r from-blue-900 to-slate-900 p-4 items-center gap-3 border-b border-white/10'):
                 ui.icon('psychology', color='white').classes('text-2xl')
                 ui.label('AI EXAMINER').classes('text-xl font-black text-white tracking-widest')
            
            with ui.column().classes('p-6 w-full gap-6'):
                self.quiz_question_label = ui.label('').classes('text-xl font-medium text-white leading-relaxed')
                
                # Options Grid
                self.quiz_option_btns = []
                with ui.column().classes('w-full gap-3'):
                    for i in range(4):
                        btn = ui.button('', on_click=lambda ix=i: self.submit_quiz_answer(ix)).props('no-caps align=left').classes('w-full p-4 text-left text-gray-200 bg-white/5 border border-white/10 rounded-xl hover:bg-blue-600/20 hover:border-blue-500 transition-all duration-300 hidden text-md')
                        self.quiz_option_btns.append(btn)

                self.quiz_result_area = ui.label('').classes('font-bold text-center w-full min-h-[20px]')

    async def check_understanding(self, slide_id):
        """Generates a question for the current slide and blocks navigation until answered."""
        slide = self.slides[self.current_slide_index]
        context_text = "\n".join(slide.get('lines', []))
        
        # Skip if too short
        if len(context_text) < 50:
            self.load_slide(self.current_slide_index + 1)
            return

        # Show processing
        self.processing_dialog.open()

        prompt = f"""
        CONTENT:
        {context_text}
        
        TASK:
        Đóng vai một giáo viên nghiêm khắc và thông minh. Hãy tạo 1 câu hỏi trắc nghiệm (4 lựa chọn) để kiểm tra kiến thức quan trọng trong nội dung trên.
        
        YÊU CẦU QUAN TRỌNG:
        1. Ngôn ngữ: TIẾNG VIỆT 100%.
        2. Độ khó: Các phương án nhiễu (distractors) phải hợp lý, GẦN GIỐNG đáp án đúng, không quá ngớ ngẩn.
        3. Độ dài: Cố gắng để các lựa chọn có độ dài TƯƠNG ĐƯƠNG nhau. Đừng để đáp án đúng dài nhất một cách lộ liễu.
        
        Return ONLY valid RAW JSON format (No Markdown code blocks):
        {{
            "question": "Câu hỏi ở đây?",
            "options": ["A. Lựa chọn 1", "B. Lựa chọn 2", "C. Lựa chọn 3", "D. Lựa chọn 4"],
            "correct_index": 0,
            "explanation": "Giải thích ngắn gọn tại sao đúng."
        }}
        """
        
        try:
            # Generate Question
            response = await run.io_bound(self.chat_model.generate_content, prompt)
            
            # Clean up JSON
            text = response.text
            # Remove markdown code blocks if present
            text = text.replace('```json', '').replace('```', '').strip()
            
            import json
            # Find JSON block using strict regex if simple clean fails
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                 self.current_quiz_data = json.loads(match.group(0))
            else:
                 # Try parsing the whole text if regex fails (sometimes it's just raw json)
                 try:
                    self.current_quiz_data = json.loads(text)
                 except:
                    print(f"Failed JSON Text: {text}")
                    raise Exception("No valid JSON found")

            self.processing_dialog.close()

            # Update Quiz Dialog UI
            self.quiz_question_label.text = self.current_quiz_data['question']
            self.quiz_result_area.text = ''
            
            # Update Buttons
            options = self.current_quiz_data.get('options', [])
            for i, btn in enumerate(self.quiz_option_btns):
                if i < len(options):
                    btn.text = options[i]
                    btn.classes(remove='hidden')
                    btn.enable()
                else:
                    btn.classes(add='hidden')
            
            self.quiz_dialog.open()
            
        except Exception as e:
            print(f"Error generating quiz: {e}")
            self.processing_dialog.close()
            # ui.notify needs context, safer to skip
            self.load_slide(self.current_slide_index + 1)

    def submit_quiz_answer(self, idx):
        if not hasattr(self, 'current_quiz_data'): return
        
        if idx == self.current_quiz_data['correct_index']:
            self.quiz_result_area.text = "✅ Chính xác! " + self.current_quiz_data['explanation']
            self.quiz_result_area.classes('text-green-600')
            ui.timer(2.0, lambda: [self.quiz_dialog.close(), self.load_slide(self.current_slide_index + 1)], once=True)
        else:
            self.quiz_result_area.text = "❌ Chưa đúng. Hãy thử lại!"
            self.quiz_result_area.classes('text-red-500')

    async def send_chat(self):
        text = self.chat_input.value
        if not text: return
        
        self.chat_input.value = ''
        
        # Display User Message
        with self.chat_container:
            ui.chat_message(text, sent=True)
        self.chat_scroll.scroll_to(percent=1.0)
        
        # Prepare Context
        current_slide = self.slides[self.current_slide_index]
        context_lines = current_slide.get('lines', [])
        context_text = "\n".join(context_lines)
        
        prompt = f"""
        CONTEXT (Nội dung Slide/Video hiện tại):
        {context_text}
        
        CÂU HỎI CỦA SINH VIÊN:
        {text}
        
        YÊU CẦU:
        Bạn là AI Tutor. Hãy trả lời câu hỏi dựa trên CONTEXT trên.
        - Nếu câu trả lời có trong context, hãy giải thích rõ ràng.
        - Nếu context không đề cập, hãy dùng kiến thức chung của bạn để trả lời nhưng nhớ nói thêm là "Slide này chưa đề cập, nhưng theo kiến thức mở rộng thì...".
        - Trả lời ngắn gọn, thân thiện, khuyến khích học tập.
        """
        
        # Show Typing Indicator
        with self.chat_container:
            spinner = ui.spinner(type='dots')
        self.chat_scroll.scroll_to(percent=1.0)
        
        # Call AI (Run in thread to avoid blocking)
        try:
            if self.chat_model:
                response = await run.io_bound(self.chat_model.generate_content, prompt)
                response_text = response.text
            else:
                response_text = "Lỗi: Không kết nối được với AI Model."
        except Exception as e:
            response_text = f"Đã có lỗi xảy ra: {str(e)}"
        
        # Remove spinner and show response
        self.chat_container.remove(spinner)
        with self.chat_container:
            ui.chat_message(response_text, sent=False, avatar='https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg')
        self.chat_scroll.scroll_to(percent=1.0)



    def load_slide(self, index):
        if 0 <= index < len(self.slides):
            self.current_slide_index = index
            slide = self.slides[index]
            slide_id = slide['id']
            
            # Check if this slide is a VIDEO
            is_video = slide_id in self.video_map
            
            self.spinner.set_visibility(True)
            self.lbl_counter.text = f"{index + 1:02d} / {len(self.slides):02d}"

            if is_video:
                 video_data = self.video_map[slide_id]
                 print(f"[Debug] Slide {slide_id} is Video: {video_data['url']}")
                 
                 # Show Video, Hide Image
                 self.img.classes('hidden')
                 self.video_player.classes(remove='hidden')
                 
                 self.video_player.source = video_data['url']
                 self.audio.pause() # Ensure audio is off
                 
                 if self.switch_auto.value:
                     self.video_player.play()
                     self.btn_play.props('icon=pause')
                 else:
                     self.btn_play.props('icon=play_arrow')
                     
                 self.spinner.set_visibility(False) # Immediate hide for video
                 
            else:
                # Normal Slide (Image + Audio)
                img_url = f"{self.asset_base_url}images/slide-{slide_id}.png"
                audio_url = f"{self.asset_base_url}audio/slide_{slide_id}.mp3"
                
                print(f"[Debug] Loading Slide {slide_id}: {img_url}")
                
                # Show Image, Hide Video
                self.video_player.classes('hidden')
                self.video_player.pause()
                self.img.classes(remove='hidden')
                
                self.img.source = img_url
                self.audio.source = audio_url
                
                if self.switch_auto.value: 
                    self.audio.play()
                    self.btn_play.props('icon=pause')
                else:
                    self.btn_play.props('icon=play_arrow')

            # Update Script (Teleprompter Style)
            self.script_container.clear()
            with self.script_container:
                # Title
                ui.label(f"SLIDE {slide['id']}: {slide['title'].upper()}").classes('font-bold text-blue-400 text-sm tracking-widest mb-4')
                # Dialog content
                for line in slide['lines']:
                    # Highlight Speaker
                    if ':' in line:
                        parts = line.split(':', 1)
                        with ui.row().classes('w-full items-start gap-2 mb-2'):
                            ui.label(parts[0] + ':').classes('font-bold text-cyan-500 whitespace-nowrap text-sm')
                            ui.label(parts[1]).classes('text-gray-300 leading-loose text-md font-light')
                    else:
                        ui.label(line).classes('text-gray-400 leading-relaxed italic text-sm pl-4 border-l-2 border-gray-700')
            
            # Scroll to top of script
            self.scroll_area.scroll_to(percent=0)

    def toggle_play(self):
        # We need a way to check state. But ui.audio doesn't expose 'paused' prop easily in Python sync.
        # We will assume toggle based on icon or just call JS.
        # Simplify: Just toggle icon and call corresponding method.
        # But we don't know if it's playing.
        # Let's use run_javascript to check or simple toggle logic.
        curr_icon = self.btn_play.props['icon']
        if curr_icon == 'play_arrow':
            self.audio.play()
            self.btn_play.props('icon=pause')
        else:
            self.audio.pause()
            self.btn_play.props('icon=play_arrow')




    def next_slide(self):
        # Helper to actually move
        def force_next():
             if self.current_slide_index < len(self.slides) - 1:
                self.load_slide(self.current_slide_index + 1)

        if self.current_slide_index < len(self.slides) - 1:
            # Check if Examiner Mode is ON
            if self.switch_examiner.value:
                # Run async check
                # We need to run async function from sync event handler
                # NiceGUI handles this if we just loop.create_task or similar, 
                # but better to use background task
                asyncio.create_task(self.check_understanding(self.current_slide_index))
            else:
                self.load_slide(self.current_slide_index + 1)
    
    def prev_slide(self):
         if self.current_slide_index > 0:
            self.load_slide(self.current_slide_index - 1)

