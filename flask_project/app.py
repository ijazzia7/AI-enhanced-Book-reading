from flask import Flask, render_template, jsonify, request, send_file
import pdfplumber
from llm_service import LLMService, Text2SpeechService, ChatWithBook, Summarization, audio_to_text, Visualization
from langchain.prompts import ChatPromptTemplate
from flair.data import Sentence
from flair.models import SequenceTagger
import numpy as np
import requests

app = Flask(__name__)
#model = LLMService()
#tts_service = Text2SpeechService()
model=1
tts_service=2

chat_bot = ChatWithBook()

summary = Summarization()
audio = audio_to_text()
vis = Visualization()
summary = 1
audio = 1
vis = 1



tagger = SequenceTagger.load("flair/ner-english-fast")
# PDF Book Path and Chunk Size
BOOK_PATH = "static/books/my_book-10.pdf"
CHUNK_SIZE = 500  # Number of characters per chunk
characters_dict={}

# Helper function to load PDF chunks
def load_pdf_pages():
    pages = []
    
    with pdfplumber.open(BOOK_PATH) as pdf:
        for page in pdf.pages:
            text = page.extract_text_simple()
            text = text.replace(' \n ', '<br><br>').replace('\n \n', '<br><br>').replace('_', '').replace('-­‐', '-')

            pages.append(text if text else "Page is empty")  # Handle empty pages
            
    return pages

# Global variable to store pages
book_pages = load_pdf_pages()

@app.route('/') 
def index():
    return render_template('homepage.html')

@app.route('/get_page/<int:page_num>', methods=['GET'])
def get_page(page_num):
    if 0 <= page_num < len(book_pages):
        
        # print(book_pages[page_num])
        # sentence = Sentence(book_pages[page_num])
        # tagger.predict(sentence)
        # l=[]
        # for entity in sentence.get_spans('ner'):
        #    if (entity.tag =='PER') & (entity.score > 0.95):
        #        l.append(entity.text)
        # characters_dict[page_num] = list(set(l))
        # characters = characters_to_display(characters_dict).tolist()
        # if len(characters)==0:
        #     characters='none'
        
        # print(characters)
        
        page_1 = book_pages[page_num]
        page_2 = book_pages[page_num+1]
        
        if '#$#$' in page_1:
            new_chap = 'one'
            chap_name = page_1.split('#$#$')[1]
            page_1 = '<br><br>'.join(page_1.split('#$#$')[2].split('<br><br>')[1:])
        elif '#$#$' in page_2:
            new_chap = 'two'
            chap_name = page_2.split('#$#$')[1]
            page_2 = '<br><br>'.join(page_2.split('#$#$')[2].split('<br><br>')[1:])
        else:
            new_chap='none'
            chap_name='none'
        
        return jsonify({'page1': page_1,'page2': page_2,'chap': new_chap,'chapterName':chap_name, 'next_page': page_num + 2, 'prev_page': page_num - 2})#, 'characters':characters})
    return jsonify({'page': '', 'next_page': None, 'prev_page': None})  # End of book

@app.route('/book-link') 
def reading_page():
    return render_template('reading.html')

def characters_to_display(characters_dict):
    l = list(characters_dict.values())
    l = [item for sublist in l for item in sublist]
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
    selected_text = data.get('selected_text', '')
    if selected_text:
        prompt  = 'Word: "{word}"'
        prompt_template = ChatPromptTemplate.from_template(prompt)
        messages = prompt_template.format_messages(word=selected_text)
        final_prompt = messages[0].content
        #output = model.generate_response(final_prompt, 0)
        output = 'Lorem ipsum this'
        return jsonify({"LLM_output": output}), 200
    return jsonify({"error": "No text received."}), 400


@app.route('/contextual_meaning', methods=['POST'])  
def contextual_meaning():
    data = request.get_json()
    selected_text = data.get('selected_text')
    paragraph = data.get('selected_paragraph')
    if selected_text:
        prompt = '''Word: "{word}"\nParagraph: {paragraph}'''
        prompt_template = ChatPromptTemplate.from_template(prompt)
        messages = prompt_template.format_messages(word=selected_text, paragraph=paragraph)
        final_prompt = messages[0].content
        #output = model.generate_response(final_prompt, 1)
        output = 'Lorem ipsum this is a testing meaning of the word. This should be replaced by the model output'
        #print(output)
        return jsonify({"LLM_output": output}), 200
    return jsonify({"error": "No text received."}), 400



@app.route('/create_sentence', methods=['POST'])  
def create_sentence():
    data = request.get_json()
    selected_text = data.get('selected_text', '')
    if selected_text:
        prompt  = 'Word: "{word}"'
        prompt_template = ChatPromptTemplate.from_template(prompt)
        messages = prompt_template.format_messages(word=selected_text)
        final_prompt = messages[0].content
        #output = model.generate_response(final_prompt, 2)
        output = 'Lorem ipsum this is a testing meaning of the word. This should be replaced by the model output'
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
        #output = chat_bot.chat(question, page_num)
        output = 'Hello how can we help you? This is a dummy response. A dummy response'
        return jsonify({"chat_reply": output}), 200
    return jsonify({"error": "No text received."}), 400

#------------------------------------------------------------------------------------------------

@app.route('/summarize', methods=['POST'])  
def summary():
    data = request.get_json()
    question = data.get('question')
    if question:
        #output = chat_bot.chat(question, page_num)
        output = 'Hello how can we help you? This is a dummy response. A dummy response'
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

    
@app.route('/get-image', methods=['POST'])
def get_image():
    img_base64 = vis.get_images()
    return jsonify({"image": f"data:image/png;base64,{img_base64}"})



# Dictionary Request
#------------------------------------------------------------------------------------------------
@app.route('/dictionary', methods=['POST'])  
def get_word_definition():
    word = request.get_json()
    print(word)
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
        print(t)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return jsonify({"error": "No text received."}), 400
    
    return jsonify({"def": t}), 200
#------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)

