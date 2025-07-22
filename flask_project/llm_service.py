from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from PIL import Image
import os
import requests
from PIL import Image
from io import BytesIO
import base64
import io
from datasets import load_dataset
#from IPython.display import Audio
import tempfile
import soundfile as sf
from huggingface_hub import InferenceClient
#from langchain_community.embeddings import HuggingFaceHubEmbeddings
from langchain_huggingface import HuggingFaceEndpointEmbeddings
#from langchain.embeddings import HuggingFaceHubEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
#from langchain_chroma import Chroma
import warnings
warnings.filterwarnings("ignore")
import requests
import fal_client

from langchain.prompts import ChatPromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings

# hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# persist_dir = 'static/chroma'
# vector_db = Chroma(
#     persist_directory=persist_dir,
#     embedding_function=hf_embeddings)

url = "https://gpt-4o-mini.p.rapidapi.com/chat/completions"

headers = {
	"x-rapidapi-key": "1bf02a2893mshdf19511f9f91ec7p1d360fjsn6c1314c7778b",
	"x-rapidapi-host": "gpt-4o-mini.p.rapidapi.com",
	"Content-Type": "application/json"
}
os.environ['FAL_KEY'] = 'abd8d5d0-818f-406e-b212-9f45f6396d41:d3935499c524eedd39be799062757a28'


class paraVisualization:
    def __init__(self, api_key='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'):
        url = "https://gpt-4o-mini.p.rapidapi.com/chat/completions"
        
    
    def generate_response(self):
        payload = {
        "model": "gpt-4o-mini",
        "messages": self.messages
                }
        response = requests.post(url, json=payload, headers=headers)
        
        return response.json()['choices'][0]['message']['content']
        
        
        # #dummy images
        # img1 = Image.open('static/images/imagesForParaVis/vis1.png') 
        # img2 = Image.open('static/images/imagesForParaVis/vis2.png') 
        # img3 = Image.open('static/images/imagesForParaVis/vis3.png') 
        
        # collage_width = 504 * 3
        # collage = Image.new('RGB', (collage_width, 504))

        # for idx, img in enumerate([img1, img2, img3]):
        #     collage.paste(img, (idx * 504, 0))
            
        # path = 'static/images/imagesForParaVis/paravis.png'
        # collage.save(path)

        # # collage
        
        # # img_io1 = io.BytesIO()
        # # img1.save(img_io1, format="PNG")
        # # img_io1.seek(0)
        
        # # # Convert to Base64
        # # img_base641 = base64.b64encode(img_io1.getvalue()).decode("utf-8")
        # return path
                   
        
    def get_images(self, paragraph):
        prompt = f"""
        You are given a paragraph from a novel. Your task is to create three separate visual prompts from this paragraph. Each prompt should describe a **different significant moment, action, or image**, suitable for generating illustrations.

        Instructions:
        1. Identify three key scenes or actions in the paragraph. These can be emotional, physical, reflective, or environmental moments.
        2. For each one:
        - Generalize the character (e.g., "a man," "a boy," "a person").
        - Describe the action or situation simply but visually.
        - Mention the setting briefly.
        3. Each prompt must be **under 30 words**, and must be **visually descriptive**, not abstract or internal.
        4. If fewer than 3 clear actions are present, reuse key elements to create alternate views or perspectives.

        Paragraph:
        {paragraph}

        Resulting Prompts:
        Prompt 1:
        <First visual prompt>

        Prompt 2:
        <Second visual prompt>

        Prompt 3:
        <Third visual prompt>
        """
        self.messages = [
                    {"role": "system", "content": "You are a helpful assistant helping in extracting info from long paragraphs."},
                    {"role": "user", "content":prompt}
                ]
        result = self.generate_response()
        prompts = []
        for i in result.split("Prompt")[1:]:
            res = "A dimly lit, close-up,  atmospheric scene, illustrated in a refined, cinematic style reminiscent of Ivan Kramskoy featuring "+ i.split(':')[-1].strip()
            prompts.append(res)
            
        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log in update.logs:
                    print(log["message"])
        all_images=[]
        for prompt_for_vis in prompts:
            result_fal = fal_client.subscribe(
                "fal-ai/flux/schnell",
                arguments={
                            "images": [
                                        {
                                        "url": "",
                                        "content_type": "image/jpeg"
                                        }
                                    ],
                            "prompt": prompt_for_vis,
                            "image_size": "landscape_4_3",
                            "num_inference_steps": 4,
                            "num_images": 1,
                            "enable_safety_checker": True
                            },
                with_logs=True,
                on_queue_update=on_queue_update,
            )
            
            image_url = result_fal['images'][0]['url']
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            all_images.append(image)
            
        collage_width = 1024 * 3  # 3 images wide
        collage_height = 768      # height of one image
        collage = Image.new('RGB', (collage_width, collage_height))
        for idx, img in enumerate(all_images):
            collage.paste(img, (idx * 1024, 0))  # place each image side by side
            
        path = 'static/images/imagesForParaVis/paravis.png'
        collage.save(path)
        return path
            
            

    
    
class characterUpdate:
    def __init__(self, api_key='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'):
        url = "https://gpt-4o-mini.p.rapidapi.com/chat/completions"
    
    def generate_response(self,current_desc, char, p1, p2, vector_db):
        docs_returned = vector_db.similarity_search(
            f"From the following text, extract all passages that describe the physical appearance of the character '{char}'. Focus on details such as his hair, eyes, facial features, build, clothing, and any other distinctive physical attributes. Provide both the direct excerpts from the text and a summarized list of these features.",
            k=5,
            filter={
                '$and': [
                    {'page': {'$gt': p1}},
                    {'page': {'$lt': p2}}
                ]
            }
        )
        
        content=''
        for i in docs_returned:
            content+=i.page_content+'\n'
                
        messages = [
            {"role": "system", "content": "You are a helpful assistant, helping extract character description from text."},
            {"role": "user", "content":f'''
            You are an assistant helping write detailed character descriptions.
            
            Current character description:
            {current_desc}
            
            New narrative content:
            {content}
            
            Task:
            - Read the new narrative content carefully.
            - Identify **new facts, traits, backstory, or relationships** relevant to the character.
            - Update the character description to **incorporate this new information**, while preserving the existing essence.
            - Write the updated character description in **third person**, with a natural narrative tone.
            - Make it clear, concise, and factual—avoid speculation.
            - Keep the updated description under 50 words.
            
            Output format:
            Updated character description:
            <your updated version here>
            '''},
                       ]
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages
                    }
        response = requests.post(url, json=payload, headers=headers)
        output = response.json()['choices'][0]['message']['content'].split('Updated character description:')[-1].strip()
        return output
    
    
class characterVis:
    def __init__(self, api_key='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'):
        self.client = InferenceClient(
        provider="nebius",
        api_key=api_key)
        
        
    def generate_image(self, promptVis):
        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log in update.logs:
                    print(log["message"])

        result = fal_client.subscribe(
            "fal-ai/flux/schnell",
            arguments={
                        "images": [
                                    {
                                    "url": "",
                                    "content_type": "image/jpeg"
                                    }
                                ],
                        "prompt": promptVis,
                        "image_size": "landscape_4_3",
                        "num_inference_steps": 4,
                        "num_images": 1,
                        "enable_safety_checker": True
                        },
            with_logs=True,
            on_queue_update=on_queue_update,
            )

        image_url = result['images'][0]['url']
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        return image 
    
    
    def generate_response(self, char, p1, p2, vector_db):
        docs_returned = vector_db.similarity_search(
            f"From the following text, extract all passages that describe the physical appearance of the character '{char}'. Focus on details such as his hair, eyes, facial features, build, clothing, and any other distinctive physical attributes. Provide both the direct excerpts from the text and a summarized list of these features.",
            k=5,
            filter={
                '$and': [
                    {'page': {'$gt': p1}},
                    {'page': {'$lt': p2}}
                ]
            }
        )
        
        content=''
        for i in docs_returned:
            content+=i.page_content+'\n'
                
        messages = [
            {"role": "system", "content": "You are a helpful assistant, helping extract character description from text."},
            {"role": "user", "content":f"""
                You are helping generate a physical description of the character "{char}" based on the text below.

                Instructions:
                - Focus only on the character named "{char}".
                - If physical traits of "{char}" are mentioned (like hair, eyes, face, body, clothes), summarize them clearly in under 30 words.
                - If there are no physical traits, try to infer if "{char}" is a man, woman, or child and describe their likely appearance for the setting.
                - Do **not** describe other characters, even if they have more detail.
                - Keep it simple and factual.


                Text:
                {content}

                Output format:
                Physical description:
                <your description here>
                """},
                       ]
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages
                    }
        response = requests.post(url, json=payload, headers=headers)
        output = response.json()['choices'][0]['message']['content'].split('Physical description:')[-1].strip()
        
        promptVis = "A dimly lit, close-up,  atmospheric scene, illustrated in a refined, cinematic style reminiscent of Ivan Kramskoy featuring "+ output
        image = self.generate_image(promptVis)
        path = f'static/images/imagesForCharacters/{char}_image.png'
        image.save(path)
        return path
    
    
    
    
    
class audio_to_text:
    def __init__(self, api_key='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'):
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny",
            chunk_length_s=30,
            device=device,
            generate_kwargs={"temperature": 0.1}
            )
        
    def process_recording(self, data):
        prediction = self.pipe(data, batch_size=8)["text"]
        return prediction
                    
        



class ChatWithBook:
    def __init__(self, api_key='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'):
        self.client = InferenceClient(api_key=api_key)
     
        
    def chat(self, question, page, vector_db):
        docs_returned = vector_db.similarity_search(question, k=5, filter={'page':{'$lt': page}})
        paragraph = '\n'.join([x.page_content for x in docs_returned])
        

        prompt = f'''You are a helpful assistant answering questions about a book. Your job is to respond based only on the paragraphs provided. 
        Do not add information that is not explicitly mentioned or implied.

        Rules:
        - Use complete sentences.
        - Keep answers concise and grounded in the paragraph.
        - Do not assume or speculate beyond the text.
        
        Here is your Question:
        {question}
        
        Relevant Paragraphs:
        {paragraph}

        Answer:
        <your answer>
        '''
    
    
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant, helping answer questions from a book (context)."},
            {"role": "user", "content":prompt},
                    ]
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages
                    }
        response = requests.post(url, json=payload, headers=headers)
        output = response.json()['choices'][0]['message']['content']#.split('**Updated character description:**')[-1].strip()
        return output



class LLMService:
    def __init__(self, api_key='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'):
        self.client = InferenceClient(api_key=api_key)
        

    def generate_response(self, word, ind, paragraph=None):
        all_messages = [
        [
        {"role": "system", "content": "You are Mistral. You are a helpful assistant.."},
        {"role": "user", "content":f"""You will be given a single English word. Your task is to explain its meaning in a clear, simple, and easy-to-understand way suitable for someone learning English or unfamiliar with advanced vocabulary. Avoid using technical or overly complex language. You may include a relatable example or analogy if it helps clarify the word. You only have to output the 'Meaning'. Nothing else. Have a look at the example below:

        Example:

        Word: “gregarious”
        Meaning: Someone who enjoys being around other people and likes to socialize, such as a person who loves going to parties and meeting new friends.
        
        
        Word: {word}
        Meaning: <your output here>
        """}], 
        [
        {"role": "system", "content": "You are Mistral. You are a helpful assistant."},
        {"role": "user", "content": f"""You will be given a word along with a paragraph where that word appears. Your task is to explain the meaning of the word specifically in the context of that paragraph. Focus on how the word is being used in that particular sentence or situation, not just its dictionary definition. Use clear and simple language. You only have to output the 'Contextualized Meaning'. Nothing else. Have a look at the example below:

        Example:
        
        Word: “resolute”
        Paragraph: Even when the team doubted their chances, Maya remained resolute, her eyes fixed on the goal as she encouraged everyone to keep going despite the challenges.
        Contextualized Meaning: In this paragraph, “resolute” means Maya was determined and unwavering, staying focused and strong even when others were unsure.
        
        
        Word: {word}
        Paragraph: {paragraph}
        Contextualized Meaning: <your output here>
        """
        }],
                             
        [
        {"role": "system", "content": "You are Mistral. You are a helpful assistant."},
        {"role": "user", "content": f"""You will be given an English word. Your task is to write a single, well-crafted sentence that clearly shows the meaning of the word through context. Do not define the word directly. Instead, use clues in the sentence—such as actions, consequences, or descriptions—that allow the reader to infer its meaning. You only have to output the 'Sentence'. Nothing else. Have a look at the example below:

        Example:

        Word: “meticulous”
        Sentence: Jenna was meticulous when organizing her books, carefully arranging them by color, size, and subject so that everything looked perfect.

        Word: {word}
        Sentence: <your output here>
        """},]
         ]
        
        messages = all_messages[ind]
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages
                    }
        response = requests.post(url, json=payload, headers=headers)
        output = response.json()['choices'][0]['message']['content']#.split(':')[-1].strip()
        return output
        




class Text2SpeechService:
    def __init__(self):
        #Initialize the text-to-speech pipeline and load speaker embeddings
        #device = "mps" if torch.backends.mps.is_available() else "cpu"
        #device =  "cpu"
        self.device = "cpu"
        self.device_index = -1
        
        self.synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts",device=self.device_index)
        self.embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        self.speaker_embedding = torch.tensor(self.embeddings_dataset[7306]["xvector"]).unsqueeze(0)
        f='p'
    def generate_response(self, text):
        # Generate text-to-speech output with the specified text and speaker embeddings
        speech = self.synthesiser(
            text,
            forward_params={"speaker_embeddings": self.speaker_embedding}
        )
        # Return the audio data for playback
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        sf.write(temp_file.name, speech["audio"], samplerate=speech["sampling_rate"])
        return temp_file.name
        #return 'd'
    
    
    
class Summarization:
    def __init__(self):
        url = "https://gpt-4o-mini.p.rapidapi.com/chat/completions"
    def summarize(self, chapter_content):
        messages = [
            {"role": "system", "content": "You are a helpful assistant, helping answer questions from a book (context)."},
            {"role": "user", "content":f"""Summarize the following chapter in nor more than 2 paragraphs:
            
            {chapter_content}
             """}]
        payload =   {
                "model": "gpt-4o-mini",
                "messages": messages
                    }
        response = requests.post(url, json=payload, headers=headers)
        output = response.json()['choices'][0]['message']['content']
        return output

            
    
    