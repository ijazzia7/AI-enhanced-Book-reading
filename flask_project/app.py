from flask import Flask, render_template, jsonify, request, send_file
import pdfplumber
from llm_service import LLMService, Text2SpeechService, ChatWithBook, Summarization, audio_to_text, paraVisualization, characterUpdate, characterVis, paraVisualization
from langchain.prompts import ChatPromptTemplate
from flair.data import Sentence
from flair.models import SequenceTagger
import numpy as np
import requests
import time
from flask import session, redirect, url_for
from auth import auth_bp
from DBmodel import db
import os
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import re


app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(auth_bp)

# Create DB only if it doesn't exist
@app.before_request
def initialize_database():
    db_path = os.path.join(os.getcwd(), 'users.db')
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()


word_comprehension = LLMService()
tts_service = Text2SpeechService()
chat_bot = ChatWithBook()
summary = Summarization()
audio = audio_to_text()
updateCharacter = characterUpdate()
charImageUpdate = characterVis()
para_visualization = paraVisualization()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


tagger = SequenceTagger.load("flair/ner-english-fast")
# PDF Book Path and Chunk Size
CHUNK_SIZE = 500  # Number of characters per chunk
characters_dict={}

# Helper function to load PDF chunks
# def load_pdf_pages():
#     pages = []
    
#     with pdfplumber.open(BOOK_PATH) as pdf:
#         for page in pdf.pages:
#             text = page.extract_text_simple()
#             text = text.replace(' \n ', '<br><br>').replace('\n \n', '<br><br>').replace('_', '').replace('-­‐', '-')

#             pages.append(text if text else "Page is empty")  # Handle empty pages
            
#     return pages
def load_pdf_pages():    
    with open(BOOK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)





# Global variable to store pages
#book_pages = load_pdf_pages()

@app.route('/') 
@login_required
def index():
    return render_template('homepage.html')

@app.route('/get_page/<int:page_num>', methods=['GET'])
def get_page(page_num):
    if 0 <= page_num < len(book_pages):
        
        sentence = Sentence(book_pages[page_num])
        tagger.predict(sentence)
        l=[]
        for entity in sentence.get_spans('ner'):
           if (entity.tag =='PER') & (entity.score > 0.95):
               l.append(entity.text)
        characters_dict[page_num] = list(set(l))
        characters = characters_to_display(characters_dict).tolist()
        if len(characters)==0:
            characters='none'
        
        
        page_1 = book_pages[page_num]
        page_2 = book_pages[page_num+1]
        
        
        if '#$#$' in page_1:
            new_chap = 'one'
            chap_name = page_1.split('#$#$')[1]
            if '<br><br>' in page_1:
                page_1 = '<br><br>'.join(page_1.split('#$#$')[2].split('<br><br>')[1:])
            else:
                page_1 = page_1.split('#$#$')[2].strip()
#            page_1 = '<br><br>'.join(page_1.split('#$#$')[2].split('<br><br>')[1:])
        elif '#$#$' in page_2:
            new_chap = 'two'
            chap_name = page_2.split('#$#$')[1]
            if '<br><br>' in page_2:
                page_2 = '<br><br>'.join(page_2.split('#$#$')[2].split('<br><br>')[1:])
            else:
                page_2 = page_2.split('#$#$')[2].strip()
            #page_2 = '<br><br>'.join(page_2.split('#$#$')[2].split('<br><br>')[1:])
        else:
            new_chap='none'
            chap_name='none'
        current_chapter = int(combined_book_text[:combined_book_text.index(page_1)].split('#$#$')[-2].split()[-1])-1
        
                
        return jsonify({'page1': page_1,'page2': page_2,'chap': new_chap,'chapterName':chap_name, 'next_page': page_num + 2, 'prev_page': page_num - 2, 'characters':characters, 'currentChap':current_chapter})
    return jsonify({'page': '', 'next_page': None, 'prev_page': None})  # End of book


# def create_characters(characters):
#     dictionary= {}
#     for name in characters:
#         dictionary[name]={'image':'s'}
    






@app.route('/book-link') 
def reading_page():
    global book_file, BOOK_PATH, book_pages, vector_db, combined_book_text, chapters
    
    book_file = request.args.get('book')
    BOOK_PATH = f"cache/{book_file}"
    book_pages = load_pdf_pages()
    combined_book_text = ' '.join(book_pages)
    chapters = re.split(r'#\$\#\$Chapter \d+\#\$\#\$', combined_book_text)[1:]
    hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    persist_dir = f'static/vectordb/{book_file.split(".")[0]}/chroma'
    vector_db = Chroma(
    persist_directory=persist_dir,
    embedding_function=hf_embeddings)
    pattern = r"#\$\#\$Chapter \d+\#\$\#\$"
    chapter_pages=[]
    for i in range(len(book_pages)):
        if re.search(pattern, book_pages[i]):
            chapter_pages.append(i+1)
    print(book_file, BOOK_PATH,persist_dir)
    
    #return render_template('reading.html')
    return render_template('reading.html', totalPages=len(book_pages), chapterStarts=chapter_pages)


def characters_to_display(characters_dict):
    l = list(characters_dict.values())
    l = [item.replace('  ', ' ') for sublist in l for item in sublist]
    unique = set(l)
    count_dict ={}
    for x in range(len(unique)):
        count_dict[list(unique)[x]] = l.count(list(unique)[x])
    final_dict = dict(sorted(count_dict.items(), key=lambda item: item[1], reverse=True))
    keys = np.array(list(final_dict.keys()))
    values = np.array(list(final_dict.values()))
    return keys[values>=2][:10]




#------------------------------------------------------------------------------------------------
@app.route('/simple_meaning', methods=['POST'])  
def simple_meaning():
    data = request.get_json()
    word = data.get('selected_text', '')
    if word:
        output = word_comprehension.generate_response(word, 0, paragraph='None')
        #output = 'Lorem ipsum this is a testing MEANING of the word. This should be replaced by the model output'
        return jsonify({"LLM_output": output}), 200
    return jsonify({"error": "No text received."}), 400


@app.route('/contextual_meaning', methods=['POST'])  
def contextual_meaning():
    data = request.get_json()
    word = data.get('selected_text')
    paragraph = data.get('selected_paragraph')
    if word:
        output = word_comprehension.generate_response(word, 1, paragraph=paragraph)
        #output = 'Lorem ipsum this is a testing CONTEXTUAL MEANING of the word. This should be replaced by the model output'
        return jsonify({"LLM_output": output}), 200
    return jsonify({"error": "No text received."}), 400



@app.route('/create_sentence', methods=['POST'])  
def create_sentence():
    data = request.get_json()
    word = data.get('selected_text', '')
    if word:
        output = word_comprehension.generate_response(word, 2, paragraph='None')
        #output = 'Lorem ipsum this is a testing SENTENCE of the word. This should be replaced by the model output'
        return jsonify({"LLM_output": output}), 200
    return jsonify({"error": "No text received."}), 400

#------------------------------------------------------------------------------------------------



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



#------------------------------------------------------------------------------------------------


@app.route('/chat_book', methods=['POST'])  
def chatting():
    data = request.get_json()
    question = data.get('question')
    page_num = data.get('page_number')
    if question:
        output = chat_bot.chat(question, page_num, vector_db)
        #output = 'Hello how can we help you? This is a dummy response. #A dummy response'
        return jsonify({"chat_reply": output}), 200
    return jsonify({"error": "No text received."}), 400


#------------------------------------------------------------------------------------------------

@app.route("/transcribe_audio", methods=["POST"])
def transcribe_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    audio_bytes = audio_file.read()
    # Process the audio bytes using your pipeline
    try:
        transcription = audio.process_recording(audio_bytes)
        return jsonify({"transcription": transcription})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


#------------------------------------------------------------------------------------------------

    
# @app.route('/get-image', methods=['POST'])
# def get_image():
#     img_base64 = vis.get_images()
#     return jsonify({"image": f"data:image/png;base64,{img_base64}"})



# Dictionary Request
#------------------------------------------------------------------------------------------------
@app.route('/dictionary', methods=['POST'])  
def get_word_definition():
    word = request.get_json()
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            phonetic = [i for i in data if 'phonetic' in i][0]['phonetic']
        except:
            phonetic = 'phonetic not available'
        meanings = [len(i['meanings']) for i in data]
        ind = np.argmax(meanings)
        meaning = [i['meanings'] for i in data][ind]
        pos = [i['partOfSpeech'] for i in meaning]
        t=f'<strong>{phonetic}</strong><br><br>'
        for x in range(len(meaning)):
            t += f'<strong>Meaning (as {pos[x]})</strong> :<br>{[i['definition'] for i in meaning[x]['definitions']][0]}<br><br>'
        t = t.rstrip()       
    else:
        print(f"Error: {response.status_code}")
        return jsonify({"error": "No text received."}), 400
    
    return jsonify({"def": t}), 200
#------------------------------------------------------------------------------------------------
    
# Character Update 
@app.route('/updateCharacter', methods=['POST'])  
def update_description():
    data = request.get_json() 
    current_desc = data.get("current_desc")
    char = data.get("char")
    p1 = data.get("p1")
    p2 = data.get("p2")
    index = data.get("index")
    

    output = updateCharacter.generate_response(current_desc, char, p1, p2, vector_db)
    #time.sleep(7) 
    #output = f'{char}{index} Dummy Output character description For character'
    
    return jsonify({"output": output})  



#------------------------------------------------------------------------------------------------


# Visualize Character 
@app.route('/visCharacter', methods=['POST'])  
def update_image():
    data = request.get_json() 
    char = data.get("char")
    p1 = data.get("p1")
    p2 = data.get("p2")
    index = data.get("index")
    
    
    #output = f'https://dummyimage.com/504x504/cccccc/000000&text={char}{index}'
    output = charImageUpdate.generate_response(char, p1, p2, vector_db)
    #time.sleep(7) 
    
    return jsonify({"output_path": output})  



#------------------------------------------------------------------------------------------------


# Paragraph Visualization 
@app.route('/visParagraph', methods=['POST'])  
def character_vis():
    data = request.get_json() 
    paragraph = data.get("paragraph")
    output_path = para_visualization.get_images(paragraph)
    #time.sleep(5) 
    #output = f'Dummy Output character description For character'
    
    return jsonify({"output_path": output_path})  
    #return jsonify({"output_path": output})  


#------------------------------------------------------------------------------------------------


# Chapter Summarization 
@app.route('/summarize', methods=['POST'])  
def summarizingChapter():
    chap_num = request.get_json() 
    chapter_content = chapters[chap_num]
    result = summary.summarize(chapter_content)
    #result = 'sfdsdfdsf fsddfsfds fsdfsddfs'
    #time.sleep(5)
    return jsonify({"summarized_chapter": result})  

#------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)

 