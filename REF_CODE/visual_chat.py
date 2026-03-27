from nicegui import ui
import asyncio
from gemini_helper import get_chat_model

# --- Global Chat Session ---
chat_session = None

async def initialize_chat():
    global chat_session
    # Run in executor to avoid blocking UI during model setup/check
    loop = asyncio.get_event_loop()
    try:
        model = await loop.run_in_executor(None, get_chat_model)
        if model:
            chat_session = model.start_chat(history=[])
            print("Chat session initialized.")
            return True
        return False
    except Exception as e:
        print(f"Failed to init chat: {e}")
        return False

async def get_response(msg_container, text):
    global chat_session
    
    if not chat_session:
        success = await initialize_chat()
        if not success:
            with msg_container:
                ui.chat_message("❌ Failed to initialize Gemini. Check console.", sent=False).classes('bg-red-200 text-red-900')
            return

    # Show loading indicator
    with msg_container:
        spinner = ui.spinner(size='lg')
        
    try:
        # Run generation in a separate thread so UI doesn't freeze
        loop = asyncio.get_event_loop()
        
        # Use the robust chat session which handles 429 retries internally
        response = await loop.run_in_executor(None, chat_session.send_message, text)
            
        spinner.delete()
        
        with msg_container:
            ui.markdown(response.text).classes('w-full')
            
    except Exception as e:
        spinner.delete()
        with msg_container:
             ui.chat_message(f"❌ Error: {str(e)}", sent=False).classes('bg-red-100')

@ui.page('/')
async def main():
    ui.dark_mode().enable()
    
    with ui.column().classes('w-full items-center gap-4'):
        ui.markdown('# 🤖 Gemini Visual Chat (Robust)').classes('text-2xl mt-4 text-primary')
        ui.label('Auto-retries on 429 errors enabled').classes('text-xs text-gray-400')
        
        # Chat Container
        with ui.scroll_area().classes('w-full max-w-2xl h-[60vh] p-4 border rounded-lg border-gray-700 bg-gray-900') as scroll_area:
            msg_container = ui.column().classes('w-full gap-4')

        async def send():
            text = text_input.value
            if not text: return
            
            text_input.value = ''
            
            # Add user message
            with msg_container:
                ui.chat_message(text, sent=True).classes('text-white')
            
            scroll_area.scroll_to(percent=1.0)
            
            # Get bot response
            await get_response(msg_container, text)
            scroll_area.scroll_to(percent=1.0)

        # Input Area
        with ui.row().classes('w-full max-w-2xl items-center gap-2'):
            text_input = ui.input(placeholder='Type a message...').classes('flex-grow').on('keydown.enter', send)
            ui.button(icon='send', on_click=send).props('round dense flat')

    # Init chat on load
    await initialize_chat()

ui.run(title='Gemini Visual Chat', port=8888, reload=False, dark=True)
