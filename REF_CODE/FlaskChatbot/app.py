from flask import Flask, render_template, request, jsonify
import sys
import os

# Add parent directory to path to import gemini_helper
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gemini_helper import get_chat_model

app = Flask(__name__)

# Global chat session per worker (simple implementation)
chat_session = None

def get_session():
    global chat_session
    if chat_session is None:
        model = get_chat_model()
        if model:
            chat_session = model.start_chat(history=[])
    return chat_session

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            prompt = request.form['prompt']
            
            session = get_session()
            if not session:
                return "Error: Could not initialize Gemini model. Check API Key."

            response = session.send_message(prompt)
            return response.text
            
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
