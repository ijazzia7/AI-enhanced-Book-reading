from flask import Flask, render_template, jsonify, request, send_file
import pdfplumber
from llm_service import LLMService, Text2SpeechService

app = Flask(__name__)
#model = LLMService()

# PDF Book Path and Chunk Size
BOOK_PATH = "static/books/The Kite Runner.pdf"
CHUNK_SIZE = 500  # Number of characters per chunk

# Helper function to load PDF chunks
def load_pdf_pages():
    pages = []
    with pdfplumber.open(BOOK_PATH) as pdf:
        for page in pdf.pages:
            text = page.extract_text_simple()
            text = text.replace('\t\r \xa0', ' ').replace('\n \n', '<br><br>').replace('\n', '').replace('_', '').replace('-­‐', '-')
            pages.append(text if text else "Page is empty")  # Handle empty pages
            
    return pages

# Global variable to store pages
book_pages = load_pdf_pages()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_page/<int:page_num>', methods=['GET'])
def get_page(page_num):
    if 0 <= page_num < len(book_pages):
        return jsonify({'page': book_pages[page_num], 'next_page': page_num + 1, 'prev_page': page_num - 1})
    return jsonify({'page': '', 'next_page': None, 'prev_page': None})  # End of book

# New route to handle highlighted text submission
#@app.route('/submit_text', methods=['POST'])  # <-- Added this route
def submit_text():
    data = request.get_json()
    selected_text = data.get('selected_text', '')
    if selected_text:
        # Process the highlighted text (for now, just log it)
        selected_text = 'Explain what happens in the following paragraph in one line:\n\n'+selected_text
        #print(f"Received highlighted text: {selected_text}")
        #output = model.generate_response(selected_text)
        #print(output)
        # You can add logic here to save it to a database or process it
        return jsonify({"message": "Text received successfully!"}), 200
    return jsonify({"error": "No text received."}), 400


tts_service = Text2SpeechService()

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    # Get text from the request
    text = request.json.get('text', '')
    if not text:
        return {"error": "No text provided"}, 400

    # Generate audio and return the file
    audio_file_path = tts_service.generate_response(text)
    print(f"Sending file: {audio_file_path}")
    return send_file(audio_file_path, mimetype="audio/wav", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

