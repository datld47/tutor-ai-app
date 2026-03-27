from nicegui import ui, app, run
from data_manager import data_manager
from pkt_engine import StudentState
from bio_battery import BioBattery
from gemini_helper import extract_json_from_text, build_system_prompt, get_gemini_api_key
import google.generativeai as genai
from database import create_db_and_tables, create_user, get_user_by_username
import os
import asyncio

from utils import get_video_url


from services.prediction_service import prediction_service
from services.rag_service import advanced_rag
from services.task_broker import task_broker
from services.task_broker import task_broker
from visuals.dynamic_graph import render_dynamic_tree
from xai_engine import explain_recommendation
from ai_video_player import AIVideoPlayer
import re

# Create DB
create_db_and_tables()

# Serve local files
app.add_static_files('/audio', os.path.join(os.getcwd(), 'DB', 'audio'))
app.add_static_files('/user_data', os.path.join(os.getcwd(), 'user_data'))

# Cấu hình Gemini
from gemini_helper import get_gemini_api_key, get_chat_model

GOOGLE_API_KEY = get_gemini_api_key()
genai.configure(api_key=GOOGLE_API_KEY, transport='rest')

# Use robust model selector
model = get_chat_model()

# Start Task Broker
app.on_startup(task_broker.start_worker)

# Main Page
@ui.page('/')
async def main_page():
    # User Mock Login
    user = get_user_by_username("sv01")
    if not user:
        user = create_user("sv01", "password", "Sinh Vien 01")
    
    app.storage.user['id'] = user.id
    app.storage.user['username'] = user.username

    # Initialize Student State
    if 'student_state_data' in app.storage.user:
        # Hydrate from dict
        state = StudentState.from_dict(app.storage.user['student_state_data'])
    else:
        # New State
        state = StudentState(user.id)
        app.storage.user['student_state_data'] = state.to_dict()
    
    # Function to persist state
    def save_state():
        app.storage.user['student_state_data'] = state.to_dict()

    # --- UI Components ---
    # --- UI Components ---
    # Flat header design (no border, no shadow)
    with ui.header().classes(replace='row items-center bg-white text-slate-800 p-2 h-[60px] z-20') as header:
        ui.label('PKT Bio-Tutor').classes('text-xl font-bold text-blue-600 mr-4')
        
        # --- TABS IN HEADER ---
        with ui.tabs().classes('w-auto justify-center mr-4') as tabs:
            tab_knowledge = ui.tab('Kiến Thức', icon='hub')
            tab_create_tree = ui.tab('Tạo Cây', icon='account_tree')
            tab_video = ui.tab('Video', icon='movie')
            tab_quiz = ui.tab('Quiz', icon='quiz')

        # --- DYNAMIC LESSON TITLE IN HEADER ---
        header_lesson_container = ui.row().classes('items-center gap-2 flex-grow overflow-hidden')
        # Will be populated in load_lesson_ui

        # Prediction Label
        prediction_label = ui.label('').classes('text-sm font-bold text-blue-700 mr-4 whitespace-nowrap')

        # Component Pin Sinh học
        ui.label('Bio:').classes('text-xs mr-1 text-gray-500')
        battery = BioBattery(ui.row())
        
        # Avatar & User Info
        with ui.row().classes('items-center ml-4'):
            ui.avatar(icon='person', color='blue-100', text_color='blue-600').props('size=sm')
            ui.label(user.full_name).classes('font-bold text-sm hidden md:block')

    # Hàm cập nhật Dashboard loop
    def update_ui_loop():
        battery.update(state.current_fatigue)
        if graph_container: # Update graph if needed or periodically
             pass 

    ui.timer(1.0, update_ui_loop)

    # UI Elements references
    chat_container = None
    loading_spinner = None
    graph_container = None
    video_container = None
    quiz_container = None
    # tabs, tab_video, etc. are defined in header above, do not reset them here!
    # prediction_label is defined in header above
    # header_lesson_container is defined in header above (replaced video_header_row)

    # Hàm xử lý Chat với Advanced RAG
    async def chat_response():
        user_msg = input_box.value
        if not user_msg: return
        
        with chat_container:
            ui.chat_message(user_msg, sent=True).classes('font-medium')
        input_box.value = ''
        
        # Show loading in chat
        with chat_container:
            spinner_row = ui.row().classes('items-center gap-2')
            with spinner_row:
                 ui.spinner('dots', size='md', color='blue-500')
                 ui.label('AI đang suy nghĩ...').classes('text-gray-400 text-xs italic')
        
        try:
            if rag_switch.value:
                # Use Advanced RAG
                result = await advanced_rag.answer_with_citation(user.id, user_msg, state.to_dict())
                answer = result['answer']
                sources = result['sources']
            else:
                 # Direct Chat
                response = await run.io_bound(model.generate_content, user_msg)
                answer = response.text
                sources = []
            
            # Remove spinner
            chat_container.remove(spinner_row)

            with chat_container:
                msg = ui.chat_message(answer, sent=False, avatar='https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg').classes('bg-blue-50/50 p-2 rounded-lg')
                with msg:
                    if sources:
                        ui.separator().classes('my-2 bg-blue-100')
                        with ui.row().classes('items-center gap-1'):
                            ui.icon('library_books', color='blue-500').classes('text-xs')
                            ui.label('Nguồn tham khảo:').classes('text-xs font-bold text-blue-600')
                        
                        with ui.row().classes('gap-2 mt-1'):
                            seen = set()
                            for src in sources:
                                key = f"{src['source']}-p{src['page']}"
                                if key not in seen:
                                    # Create a "Card" look for citations
                                    with ui.link(target='#').classes('no-underline group'):
                                         with ui.card().classes('flex-row items-center gap-2 px-2 py-1 bg-white border border-blue-100 shadow-sm hover:shadow-md hover:border-blue-300 transition-all cursor-pointer'):
                                             ui.icon('description', color='blue-400').classes('text-xs group-hover:text-blue-600')
                                             with ui.column().classes('gap-0'):
                                                 ui.label(src['source'][:15] + '...').classes('text-[10px] font-bold text-gray-700 leading-none group-hover:text-blue-700')
                                                 ui.label(f"Trang {src['page']}").classes('text-[9px] text-gray-500 leading-none')
                                    seen.add(key)
        except Exception as e:
            if 'spinner_row' in locals(): chat_container.remove(spinner_row)
            with chat_container:
                ui.chat_message(f"Error: {str(e)}", sent=False).classes('text-red-500')
        
        # Scroll to bottom
        # chat_container.scroll_to(percent=1.0) # ui.column doesn't have scroll_to, the scroll_area does. We need to refactor layout to expose scroll_area.

    # Content Loading
    def load_lesson_ui(concept_id):
        state.current_concept_id = concept_id
        save_state()
        lesson_data = data_manager.get_lesson(concept_id)
        
        # Calculate Prediction
        win_prob = prediction_service.predict_next_performance(user.id, concept_id)
        
        # Switch to Video Tab
        if tabs and tab_video:
            tabs.value = tab_video

        # Update Labels
        if lesson_label_quiz: lesson_label_quiz.text = lesson_data['metadata']['concept_name']
        
        # --- UPDATE HEADER PREDICTION ---
        if prediction_label:
            prediction_label.text = f"Dự đoán: {int(win_prob*100)}%"

        # --- UPDATE GLOBAL HEADER (Title + Why) ---
        if header_lesson_container:
            header_lesson_container.clear()
            with header_lesson_container:
                 # Truncate title if too long for header
                 title = lesson_data['metadata']['concept_name']
                 if len(title) > 50: title = title[:47] + "..."
                 
                 ui.label(title).classes('text-lg font-bold text-gray-800 whitespace-nowrap overflow-hidden text-ellipsis')
                 
                 with ui.button(icon='help', color='blue-1').props('flat round dense').tooltip('Tại sao gợi ý này?'):
                      with ui.menu().classes('bg-white p-4 max-w-lg shadow-xl border'):
                          ui.label('Tại sao gợi ý bài này?').classes('font-bold text-lg mb-2 text-blue-600')
                          ui.markdown(explain_recommendation(concept_id, state)).classes('text-sm text-gray-700')

        # --- LOAD VIDEO ---
        if video_container:
            video_container.clear()
            
            # Check for AI Script first
            concept_name = lesson_data['metadata']['concept_name']
            # Handle "Chương_1_Tiết 1" or "Chuong_2_Tiet_2"
            match = re.search(r'(?:Chương|Chuong)\D*(\d+)\D*(?:Tiết|Tiet)\D*(\d+)', concept_name, re.IGNORECASE)
            script_found = False
            
            if match:
                folder_name = f"Chuong_{match.group(1)}_Tiet_{match.group(2)}"
                script_path = os.path.join(os.getcwd(), 'DB', 'Video', folder_name, 'script.txt')
                
                if os.path.exists(script_path):
                    print(f"[Main] Script found at {script_path}. Loading AI Player.")
                    AIVideoPlayer(video_container, concept_name, script_path)
                    script_found = True
            
            if not script_found:
                 with video_container:
                    video_url = get_video_url(concept_name)
                    if video_url:
                         # Overlay Button
                         ui.button(icon='open_in_new', on_click=lambda url=video_url: ui.open(url, new_tab=True)) \
                            .classes('absolute top-4 right-4 z-10 bg-white text-blue-600 opacity-80 hover:opacity-100').props('flat round dense').tooltip('Mở trong tab mới')
                         
                         ui.element('iframe').props(f'src="{video_url}" allowfullscreen').classes('w-full h-full border-none bg-black')
                    else:
                         ui.label("Video chưa khả dụng cho bài học này.").classes('italic text-gray-500 m-4')

        # --- LOAD QUIZ ---
        if quiz_container:
            quiz_container.clear()
            with quiz_container:
                questions = lesson_data.get('questions', [])
                if not questions:
                    ui.label("Chưa có câu hỏi cho bài này.").classes('italic text-gray-500')
                else:
                    # --- QUIZ STATE MANAGEMENT ---
                    class QuizController:
                        def __init__(self, questions, state_ref):
                            self.questions = questions
                            self.current_index = 0
                            self.state_ref = state_ref
                            
                            # Load history for current concept
                            cid = self.state_ref.current_concept_id
                            if cid not in self.state_ref.quiz_history:
                                self.state_ref.quiz_history[cid] = {}
                            
                            # Convert string keys back to int if needed
                            self.user_answers = {}
                            if cid in self.state_ref.quiz_history:
                                for k, v in self.state_ref.quiz_history[cid].items():
                                    self.user_answers[int(k)] = v

                            self.container = None
                            self.palette_container = None
                            self.q_card = None
                            self.progress_bar = None
                            
                        def render(self):
                            with ui.row().classes('w-full items-start gap-6 no-wrap'):
                                # Left Column: Question Area
                                with ui.column().classes('w-3/4 flex-grow'):
                                    with ui.element('div').classes('w-full bg-gray-200 rounded-full h-2.5 mb-6'):
                                        self.progress_bar = ui.element('div').classes('bg-blue-600 h-2.5 rounded-full transition-all duration-300').style('width: 0%')
                                    self.container = ui.column().classes('w-full')
                                    self.render_current_question()
                                    
                                # Right Column: Question Palette (Sticky)
                                with ui.column().classes('w-1/4 flex-shrink-0 min-w-[280px] sticky top-4'):
                                    with ui.card().classes('w-full p-4 rounded-2xl shadow-lg border-t-4 border-blue-500 bg-white'):
                                        ui.label('Danh sách câu hỏi').classes('font-bold text-gray-800 mb-4 border-b pb-2')
                                        self.palette_container = ui.grid(columns=5).classes('gap-2 justify-center')
                                        self.render_palette()
                                        
                                        with ui.column().classes('mt-6 space-y-2 text-sm text-gray-600'):
                                            with ui.row().classes('items-center'):
                                                ui.element('div').classes('w-3 h-3 rounded-full bg-gray-200 mr-2')
                                                ui.label('Chưa làm')
                                            with ui.row().classes('items-center'):
                                                ui.element('div').classes('w-3 h-3 rounded-full bg-green-500 mr-2')
                                                ui.label('Đúng (có thể làm lại)')
                                            with ui.row().classes('items-center'):
                                                ui.element('div').classes('w-3 h-3 rounded-full bg-red-500 mr-2')
                                                ui.label('Sai (hãy thử lại)')
                                            with ui.row().classes('items-center'):
                                                ui.element('div').classes('w-3 h-3 rounded-full bg-blue-500 mr-2')
                                                ui.label('Đang chọn')

                        def render_palette(self):
                            self.palette_container.clear()
                            with self.palette_container:
                                for idx, _ in enumerate(self.questions):
                                    history = self.user_answers.get(idx, {})
                                    correct_count = history.get('correct', 0)
                                    wrong_count = history.get('wrong', 0)
                                    
                                    # Base Styles
                                    base_class = 'w-10 h-10 rounded-lg flex items-center justify-center font-bold text-sm transition-all duration-200'
                                    color_class = 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    
                                    # Status Color Priority
                                    status = None
                                    if correct_count > 0:
                                        status = 'correct'
                                        color_class = 'bg-green-500 text-white shadow-sm'
                                    elif wrong_count > 0:
                                        status = 'wrong'
                                        color_class = 'bg-red-500 text-white shadow-sm'
                                    
                                    # Override if currently selected (Blue selection)
                                    if idx == self.current_index and not status:
                                         color_class = 'bg-blue-600 text-white shadow-md'

                                    # Current Selection Indicator (Border/Ring)
                                    ring_class = ''
                                    if idx == self.current_index:
                                        if status: 
                                            ring_class = 'ring-4 ring-blue-300 transform scale-110 z-10'
                                        else:
                                            ring_class = 'ring-2 ring-blue-300 transform scale-105'

                                    msg = f"Câu {idx + 1}: Đúng {correct_count} | Sai {wrong_count}"
                                    if not status: msg = f"Câu {idx + 1}: Chưa làm"
                                        
                                    ui.button(str(idx + 1), on_click=lambda i=idx: self.jump_to(i)).classes(f'{base_class} {color_class} {ring_class}').tooltip(msg)

                        def render_current_question(self):
                            self.container.clear()
                            q = self.questions[self.current_index]
                            progress = ((self.current_index + 1) / len(self.questions)) * 100
                            self.progress_bar.style(f'width: {progress}%')
                            
                            history = self.user_answers.get(self.current_index, {})
                            correct_count = history.get('correct', 0)
                            wrong_count = history.get('wrong', 0)
                            
                            with self.container:
                                with ui.card().classes('w-full p-6 sm:p-8 rounded-2xl shadow-lg relative'):
                                    with ui.row().classes('justify-between items-center mb-6 w-full'):
                                        ui.label(f'Câu {self.current_index + 1}').classes('bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded')
                                        
                                        # Smart Status Badge
                                        if correct_count > 0:
                                            ui.label(f'Đã đúng {correct_count} lần').classes('bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded')
                                        elif wrong_count > 0:
                                            ui.label(f'Đã sai {wrong_count} lần - Hãy thử lại').classes('bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded')
                                        else:
                                            ui.label('Chưa hoàn thành').classes('text-sm font-medium text-gray-500')

                                    ui.label(q['content']).classes('text-xl sm:text-2xl font-semibold text-gray-800 mb-8 leading-relaxed')
                                    options_col = ui.column().classes('w-full space-y-4')
                                    
                                    audio_success = ui.audio('/audio/success.mp3').props('hidden')
                                    audio_fail = ui.audio('/audio/error.mp3').props('hidden')
                                    
                                    btn_map = {}
                                    explanation_ui = None
                                    # No longer locking "is_solved" based on correct answer. Always allow attempts.

                                    with options_col:
                                        for opt in q['options']:
                                            key = opt['key']
                                            text = opt['text']
                                            btn_props = 'outline text-left no-caps'
                                            btn_classes = 'w-full justify-start px-4 py-3 text-gray-700 hover:bg-gray-50 border-2 rounded-lg transition-all'
                                            
                                            # Highlight logic: 
                                            # User requested "reset to default" to allow redo.
                                            # So we DO NOT pre-highlight the answer, even if they solved it.
                                            # We only show the "Badge" at the top (implemented above).
                                            
                                            # if correct_count > 0 and key == q['correct_answer']:
                                            #    btn_classes += ' bg-green-50 border-green-500'
                                            #    btn_props = 'icon=check' 
                                            
                                            b = ui.button(f"{key}. {text}").props(btn_props).classes(btn_classes)
                                            # Always enabled for retry
                                            btn_map[key] = b
                                            
                                            if key == q['correct_answer']:
                                                explanation_ui = ui.column().classes('w-full bg-green-50 p-4 border-l-4 border-green-500 rounded-r mt-2 shadow-sm animate-fade')
                                                # Always hide initially for retry
                                                explanation_ui.classes('hidden')
                                                with explanation_ui:
                                                     ui.label('Giải thích:').classes('font-bold text-green-800 text-sm mb-1')
                                                     ui.markdown(q['explanation']).classes('text-sm text-gray-800')
                                    
                                    def make_handler(btn_map, correct_key, feedback_ui, audio_ok, audio_no, feedback_msg_label):
                                        def handler(e):
                                            sender = e.sender
                                            selected_key = sender.text.split('.')[0].strip()
                                            
                                            # Initialize history if empty
                                            cid = self.state_ref.current_concept_id
                                            if cid not in self.state_ref.quiz_history: self.state_ref.quiz_history[cid] = {}
                                            if str(self.current_index) not in self.state_ref.quiz_history[cid]:
                                                self.state_ref.quiz_history[cid][str(self.current_index)] = {'correct': 0, 'wrong': 0}
                                                
                                            # --- LOGIC UPDATE ---
                                            if selected_key == correct_key:
                                                audio_ok.play()
                                                feedback_msg_label.set_text('')
                                                feedback_msg_label.classes('hidden')
                                                
                                                # Update Stats
                                                self.state_ref.quiz_history[cid][str(self.current_index)]['correct'] += 1
                                                self.state_ref.update_elo(cid, True)
                                                
                                                if feedback_ui: feedback_ui.classes(remove='hidden')
                                                
                                                # Visuals for this attempt
                                                for key, btn in btn_map.items():
                                                    # Don't disable, just update styles
                                                    if key == correct_key:
                                                        btn.props('color=green-6 icon=check')
                                                        btn.classes(remove='text-gray-700 hover:bg-gray-50 border-gray-200', add='bg-green-100 border-green-500 text-green-800')
                                                    else:
                                                        # Reset others
                                                        btn.props(remove='color icon') # Properly remove props
                                                        btn.props('outline') # Restore outline
                                                        btn.classes(add='text-gray-700 hover:bg-gray-50 border-gray-200', remove='bg-red-100 border-red-500 text-red-800 bg-green-100 border-green-500 text-green-800')
                                            else:
                                                audio_no.play()
                                                # Update stats
                                                self.state_ref.quiz_history[cid][str(self.current_index)]['wrong'] += 1
                                                self.state_ref.update_elo(cid, False)
                                                
                                                # Visuals
                                                sender.props('color=red-6 icon=close')
                                                sender.classes(remove='text-gray-700 hover:bg-gray-50 border-gray-200', add='bg-red-100 border-red-500 text-red-800')
                                                feedback_msg_label.set_text('Sai rồi, hãy thử lại!')
                                                feedback_msg_label.classes(remove='hidden')

                                            # Save and Refresh
                                            save_state()
                                            # Sync local cache
                                            self.user_answers[self.current_index] = self.state_ref.quiz_history[cid][str(self.current_index)]
                                            
                                            # Re-render Palette to update counts/colors
                                            self.render_palette()
                                            # Don't re-render current question immediately to avoid flicker, just updated buttons
                                            # Unless we want to update the "Attempts" badge immediately? 
                                            # Let's re-render current question badge only? No, simplified: just re-render palette.
                                            # Actually, if we want to show "Correct: X+1", we need to re-render.
                                            # But full re-render resets the button states (animation).
                                            # Ideally, we just update the badge. But for now, re-rendering palette is enough feedback.
                                            
                                            # Re-render Palette to update counts/colors
                                            self.render_palette()
                                            
                                        return handler

                                    feedback_msg_label = ui.label('').classes('hidden text-red-600 font-bold mt-2 ml-1')
                                    
                                    # Always bind handlers to allow retries
                                    for k, b in btn_map.items():
                                        b.on_click(make_handler(btn_map, q['correct_answer'], explanation_ui, audio_success, audio_fail, feedback_msg_label))

                                    with ui.row().classes('w-full justify-between mt-8'):
                                        ui.button('Trước', on_click=self.prev_q).props('outline').classes('px-6').bind_visibility_from(self, 'current_index', lambda i: i > 0)
                                        if self.current_index == 0: ui.element('div') 
                                        ui.button('Tiếp', on_click=self.next_q).classes('bg-blue-600 text-white px-8 shadow-md hover:bg-blue-700').bind_visibility_from(self, 'current_index', lambda i: i < len(self.questions) - 1)

                        def jump_to(self, idx):
                            self.current_index = idx
                            self.render_current_question()
                            self.render_palette()
                        def next_q(self):
                            if self.current_index < len(self.questions) - 1: self.jump_to(self.current_index + 1)
                        def prev_q(self):
                            if self.current_index > 0: self.jump_to(self.current_index - 1)

                    quiz = QuizController(questions, state)
                    quiz.render()


    # --- LAYOUT GIAO DIỆN MỚI (Single Tab) ---
    # Tabs are defined in header now
    # with ui.tabs().classes('w-full') as tabs:
    #    tab_knowledge = ui.tab('Kiến Thức', icon='hub')
    #    tab_video = ui.tab('Video', icon='movie')
    #    tab_quiz = ui.tab('Quiz', icon='quiz')

    with ui.tab_panels(tabs, value=tab_knowledge).classes('w-full h-[calc(100vh-100px)]'):
        
        # TAB 1: KNOWLEDGE TREE + CHAT (PREMIUM DASHBOARD LAYOUT)
        with ui.tab_panel(tab_knowledge).classes('p-0 h-full overflow-hidden bg-slate-50'):
             with ui.row().classes('w-full h-full no-wrap gap-0'):
                 
                 # --- LEFT PANEL: CURRICULUM (Sidebar) ---
                 with ui.column().classes('w-[280px] h-full bg-white border-r border-gray-200 flex flex-col shadow-sm z-10'):
                     # Header
                     with ui.row().classes('w-full p-4 items-center border-b border-gray-100'):
                         ui.icon('school', color='blue-600').classes('text-2xl')
                         ui.label('Chương trình học').classes('font-bold text-gray-800 text-lg tracking-tight')
                     
                     # Search
                     with ui.row().classes('w-full px-4 py-2 bg-gray-50 border-b border-gray-100'):
                         ui.input(placeholder='Tìm kiếm bài học...').props('dense outlined rounded color=blue-6 text-color=grey-8').classes('w-full bg-white text-sm')

                     # Curriculum Tree/List
                     with ui.scroll_area().classes('flex-grow w-full p-2'):
                         # 1. Build Data
                         concepts = data_manager.get_all_concepts()
                         chapters = {}
                         import re
                         chapter_pattern = re.compile(r"(ch[uương]+[_ ]?(\d+))", re.IGNORECASE)
                         
                         for c in concepts:
                             c_name = c['name']
                             chap_match = chapter_pattern.search(c_name)
                             chap_num = int(chap_match.group(2)) if chap_match else 999
                             chap_key = f"CHAPTER_{chap_num}"
                             if chap_num == 999: chap_display = "Tài nguyên bổ trợ"
                             else: chap_display = f"Chương {chap_num}"

                             if chap_key not in chapters:
                                 chapters[chap_key] = {'id': chap_key, 'label': chap_display, 'children': [], 'num': chap_num}
                             
                             chapters[chap_key]['children'].append({'id': c['id'], 'label': c_name})

                         sorted_chapters = sorted(chapters.values(), key=lambda x: x['num'])
                         
                         # 2. Render Custom Tree
                         for chap in sorted_chapters:
                             with ui.expansion(chap['label'], icon='folder_open').classes('w-full mb-1 bg-white rounded-lg border border-transparent hover:border-blue-100 transition-all font-semibold text-gray-700').props('header-class="text-blue-900"'):
                                 for child in chap['children']:
                                     # Lesson Item
                                     with ui.row().classes('w-full cursor-pointer hover:bg-blue-50 p-2 pl-8 rounded-md transition-colors items-center group') \
                                         .on('click', lambda id=child['id']: load_lesson_ui(id)):
                                         ui.icon('article', color='gray-400').classes('text-sm mr-2 group-hover:text-blue-500')
                                         ui.label(child['label']).classes('text-sm text-gray-600 group-hover:text-blue-700 leading-tight w-full truncate')

                 # --- CENTER PANEL: KNOWLEDGE GRAPH ---
                 with ui.column().classes('flex-grow h-full relative bg-slate-50 overflow-hidden'):
                     # Toolbar (Floating)
                     with ui.row().classes('absolute top-4 left-4 z-20 gap-2'):
                         with ui.button(icon='zoom_in', on_click=lambda: ui.notify('Zoom In')).props('flat round dense color=grey-7').classes('bg-white shadow-md border border-gray-200 hover:bg-blue-50'):
                              ui.tooltip('Phóng to')
                         with ui.button(icon='zoom_out', on_click=lambda: ui.notify('Zoom Out')).props('flat round dense color=grey-7').classes('bg-white shadow-md border border-gray-200 hover:bg-blue-50'):
                              ui.tooltip('Thu nhỏ')
                         with ui.button(icon='refresh', on_click=lambda: ui.notify('Reset View')).props('flat round dense color=grey-7').classes('bg-white shadow-md border border-gray-200 hover:bg-blue-50'):
                              ui.tooltip('Đặt lại')

                     # Graph Container
                     # Use a subtle grid background
                     graph_container = ui.element('div').classes('w-full h-full bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:20px_20px]')
                     render_dynamic_tree(graph_container, state, on_click=load_lesson_ui)
                     
                     # Bottom Status Bar
                     with ui.row().classes('absolute bottom-0 w-full bg-white/80 backdrop-blur border-t border-gray-200 p-2 justify-between px-4 text-xs text-gray-500'):
                         ui.label('Graph Engine: NetworkX + VisJS')
                         ui.label(f'Nodes: {len(concepts)} | Edges: {len(concepts)*2}') # Dummy stats

                 # --- RIGHT PANEL: AI ASSISTANT (Chat) ---
                 with ui.column().classes('w-[350px] h-full bg-white border-l border-gray-200 flex flex-col shadow-lg z-20'):
                     # Header
                     with ui.row().classes('w-full p-4 items-center justify-between border-b border-gray-100 bg-gradient-to-r from-blue-50 to-white'):
                         with ui.row().classes('items-center gap-2'):
                             ui.avatar(icon='smart_toy', color='blue-600', text_color='white').props('size=sm')
                             with ui.column().classes('gap-0'):
                                 ui.label('AI Tutor').classes('font-bold text-blue-900 leading-none')
                                 ui.label('Powered by Gemini 1.5').classes('text-[10px] text-blue-400 font-medium')
                         
                         rag_switch = ui.switch('Pro', value=True).props('dense color=blue keep-color').tooltip('Chế độ Nâng cao (RAG)')

                     # Chat History
                     # Important: Assign to global variable defined at top or pass scope?
                     # In this file structure, chat_container is in main_page scope.
                     with ui.scroll_area().classes('flex-grow w-full p-4 bg-gray-50/50') as chat_scroll_area:
                         chat_container = ui.column().classes('w-full gap-4')
                         
                         # Welcome Message
                         with chat_container:
                             with ui.row().classes('gap-3 items-start animate-fade'):
                                 ui.avatar(icon='smart_toy', color='white', text_color='blue-600').classes('border border-blue-100 shadow-sm')
                                 with ui.column().classes('gap-1'):
                                     ui.label('AI Tutor').classes('text-xs font-bold text-gray-500 ml-1')
                                     ui.label('Chào bạn! Mình là trợ lý học tập AI. Mình đã học toàn bộ giáo trình môn này. Hãy hỏi mình bất cứ điều gì nhé!').classes('bg-white p-3 rounded-2xl rounded-tl-none text-sm text-gray-700 shadow-sm border border-gray-100')

                     # Input Area
                     with ui.column().classes('w-full p-4 border-t border-gray-100 bg-white gap-2'):
                         # Suggestion Chips
                         with ui.row().classes('gap-2 overflow-x-auto w-full no-wrap pb-2'):
                             for q in ["Tóm tắt chương 1?", "Khái niệm TMĐT?", "Mô hình B2B là gì?"]:
                                 ui.button(q, on_click=lambda txt=q: [input_box.set_value(txt), chat_response()]).props('dense outline rounded color=grey-5 size=sm').classes('whitespace-nowrap')

                         with ui.row().classes('w-full items-center gap-2 relative'):
                             input_box = ui.input(placeholder='Nhập câu hỏi...').props('rounded outlined dense borderless').classes('w-full bg-gray-100 pr-10').on('keydown.enter', chat_response)
                             ui.button(icon='send', on_click=chat_response).props('flat round dense color=blue').classes('absolute right-1 top-1/2 transform -translate-y-1/2')

        # TAB 2: VIDEO
        # TAB 2: VIDEO
        with ui.tab_panel(tab_video).classes('p-0 h-full'):
             with ui.column().classes('w-full h-full p-0 relative'):
                 # --- VIDEO PLAYER CONTAINER (Full Height) ---
                 video_container = ui.column().classes('w-full h-full bg-black relative justify-center items-center')

        # TAB 3: QUIZ
        with ui.tab_panel(tab_quiz).classes('p-0 h-full'):
             with ui.column().classes('w-full h-full p-6 bg-gray-50 overflow-y-auto'):
                 lesson_label_quiz = ui.label("Vui lòng chọn bài học từ tab 'Kiến Thức'").classes('text-2xl text-gray-400 font-bold mb-6')
                 quiz_container = ui.column().classes('w-full')

        # TAB 4: CREATE TREE
        with ui.tab_panel(tab_create_tree).classes('p-6 h-full bg-gray-50 overflow-y-auto w-full'):
             ui.label('Tạo & Hiển thị Cây Tri Thức').classes('text-2xl font-bold text-blue-800 mb-2')
             ui.label('Quá trình xây dựng và hiển thị cây được chia làm 2 bước độc lập.').classes('text-gray-600 mb-6')
             
             with ui.row().classes('w-full gap-6 items-start flex-nowrap'):
                 # --- CARD 1: XÂY DỰNG CÂY (.txt) ---
                 with ui.card().classes('w-full md:w-[48%] flex-1 p-4 shadow-sm bg-white border border-gray-100'):
                     ui.label('Bước 1: Khởi tạo Cây Tri Thức').classes('text-lg font-bold text-blue-700')
                     ui.label('1. Tải lên file văn bản (.txt) tài liệu môn học.').classes('text-sm text-gray-600 mb-1')
                     ui.label('2. Trí tuệ Nhân tạo sẽ tự động phân tích thành cấu trúc JSON.').classes('text-sm text-gray-600 mb-4')
                     
                     upload_status_txt = ui.label('').classes('italic text-gray-400 mb-2')
                     actions_txt = ui.row().classes('w-full mt-2')

                     async def handle_upload_txt(e):
                         filename = getattr(e, 'name', 'tài liệu')
                         upload_status_txt.text = f'⏳ Đang xử lý {filename}... (quá trình này mất khoảng 20s)'
                         actions_txt.clear()
                         
                         if hasattr(e, 'content'): content_bytes = e.content.read()
                         elif hasattr(e, 'file'): content_bytes = await e.file.read()
                         else: raise Exception("Lỗi đọc file upload")
                             
                         content = content_bytes.decode('utf-8') if hasattr(content_bytes, 'decode') else content_bytes
                         content = content[:15000] # Bảo vệ API giới hạn độ dài
                         
                         from step1_build_tree import build_tree_for_user
                         from step2_build_edges import build_edges_for_user
                         try:
                             ui.notify(f'AI đang đọc hiểu nội dung {filename}...', type='info')
                             path, data = await run.io_bound(build_tree_for_user, user.username, content)
                             if data:
                                 upload_status_txt.text = f'⏳ Đang suy luận các mối quan hệ logic (Edges)...'
                                 await run.io_bound(build_edges_for_user, user.username)
                                 
                                 upload_status_txt.text = f'✅ Hoàn tất Khởi tạo!'
                                 ui.notify('Đã sinh cấu trúc Cây Tri Thức', type='positive')
                                 
                                 # Tạo Nút Tải Xuống
                                 with actions_txt:
                                     ui.label(f'Thành quả phân tích đã được lưu trữ dưới dạng JSON.').classes('text-green-600 font-bold w-full mb-1')
                                     ui.button('Tải xuống File JSON vừa tạo', on_click=lambda: ui.download(path, f"{user.username}_knowledge_tree.json")).props('color=blue icon=download outline rounded')
                             else:
                                 upload_status_txt.text = '❌ Tạo cây thất bại (lỗi AI).'
                         except Exception as ex:
                             upload_status_txt.text = f'❌ Lỗi: {str(ex)}'

                     ui.upload(on_upload=handle_upload_txt, auto_upload=True, multiple=False, label='Chọn file Đầu Vào (.txt)').props('bordered accept=".txt"').classes('w-full bg-blue-50 hover:bg-blue-100 rounded border-dashed border-2 border-blue-300')

                 # --- CARD 2: HIỂN THỊ CÂY (.json) ---
                 with ui.card().classes('w-full md:w-[48%] flex-1 p-4 shadow-sm bg-white border border-gray-100'):
                     ui.label('Bước 2: Dựng Đồ Họa 3D').classes('text-lg font-bold text-green-700')
                     ui.label('Tải lên file dữ liệu (.json) đã lấy từ Bước 1 để phân giải ra mạng nơ-ron tương tác 3D.').classes('text-sm text-gray-600 mb-4')
                     upload_status_json = ui.label('').classes('italic text-gray-400 mb-2')

                     async def handle_upload_json(e):
                         filename = getattr(e, 'name', 'dữ liệu JSON')
                         upload_status_json.text = f'⏳ Đang tải file lên hệ thống...'
                         
                         if hasattr(e, 'content'): content_bytes = e.content.read()
                         elif hasattr(e, 'file'): content_bytes = await e.file.read()
                         else: raise Exception("Lỗi đọc file upload")
                             
                         import os, json
                         out_dir = f"user_data/{user.username}"
                         os.makedirs(out_dir, exist_ok=True)
                         out_path = f"{out_dir}/{user.username}_knowledge_tree.json"
                         
                         with open(out_path, "wb") as f:
                             f.write(content_bytes)

                         from step2_5_visualize_tree import visualize_knowledge_tree
                         try:
                             upload_status_json.text = f'⏳ Đang biên dịch Đồ họa (PyVis)...'
                             await run.io_bound(visualize_knowledge_tree, user.username)
                             
                             upload_status_json.text = f'✅ Đã dựng mô hình 3D thành công!'
                             ui.notify('Dựng biểu đồ Cây Tri Thức tương tác thành công!', type='positive')
                             
                             tree_preview_container.clear()
                             with tree_preview_container:
                                 ui.label('Mô hình Mạng lưới Giáo dục 3D (Tương tác):').classes('font-bold text-lg text-blue-800 mb-2 mt-4')
                                 import time
                                 v = int(time.time())
                                 ui.element('iframe').props(f'src="/user_data/{user.username}/{user.username}_visual_tree.html?v={v}" width="100%" height="100%"').classes('w-full h-[1200px] border-2 border-gray-200 rounded-xl shadow-md')
                                 
                                 with open(out_path, 'r', encoding='utf-8') as f:
                                     read_json = json.load(f)
                                 with ui.expansion('Xem chi tiết cấu trúc JSON thô (Dành cho Dev)', icon='code').classes('w-full mt-4 bg-gray-50 border rounded-lg text-gray-700'):
                                     ui.code(json.dumps(read_json, indent=2, ensure_ascii=False), language='json').classes('w-full overflow-y-auto max-h-[500px] border shadow-sm rounded')
                                     
                         except Exception as ex:
                             upload_status_json.text = f'❌ Lỗi dựng đồ họa: {str(ex)}'

                     ui.upload(on_upload=handle_upload_json, auto_upload=True, multiple=False, label='Chọn file Đầu Ra (.json)').props('bordered accept=".json"').classes('w-full bg-green-50 hover:bg-green-100 rounded border-dashed border-2 border-green-300')

             # Chuyển container đồ họa xuống bên dưới
             tree_preview_container = ui.column().classes('w-full mt-8')

ui.run(storage_secret='pkt_secret_key', title='PKT Bio-Tutor', port=8081)
