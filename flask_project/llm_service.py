from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from PIL import Image
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

from langchain.prompts import ChatPromptTemplate




class Visualization:
    def __init__(self, api_key='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'):
        pass
        
    def get_images(self):
        #dummy images
        img1 = Image.open('/Users/ijazulhaq/flask_book_reading/static/images/vis1.jpeg') 
        img2 = Image.open('/Users/ijazulhaq/flask_book_reading/static/images/vis2.jpeg') 
        img3 = Image.open('/Users/ijazulhaq/flask_book_reading/static/images/vis3.jpeg') 
        
        img_io1 = io.BytesIO()
        img1.save(img_io1, format="PNG")
        img_io1.seek(0)
        
        # Convert to Base64
        img_base641 = base64.b64encode(img_io1.getvalue()).decode("utf-8")
        return img_base641
                   




class Summarization:
    def __init__(self, api_key='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'):
        self.text = 'The narrator explains why he went to visit Hassan and Ali in 1986: he was lonely, as most of his other friends had either died or escaped to Iran or Afghanistan. He had promised your father to care for the house after they left forPakistan, but with his degenerative arthritis he found it difficult to maintain it. So he decided to go to find them in a nearby village. He found them easily enough - they live in a tiny house surrounded by mud houses.'
    
    def summarize(self, text):
        return self.text
    
    
    
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
        hf_embeddings = HuggingFaceEndpointEmbeddings(
        repo_id="sentence-transformers/all-MiniLM-L6-v2",  
        huggingfacehub_api_token=api_key
        )
        # loader = PyPDFLoader("static/books/The Kite Runner.pdf", )
        # book = loader.load()
        # chunk_size = 2000
        # chunk_overlap = 50  
        # r_splitter =  RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap, separators='\xad')
        # splits = r_splitter.split_documents(book)
        # for x in range(len(splits)):
        #     splits[x].page_content = splits[x].page_content.replace('\t\r \xa0', ' ')
        
        persist_dir = 'static/prompts/docs/chromaNewest/'
        # self.vector_db = Chroma.from_documents(
        # documents = splits,
        # embedding = hf_embeddings,
        # persist_directory=persist_dir
        #         )
        self.vector_db = Chroma(persist_directory=persist_dir, embedding_function=hf_embeddings) 

        
        
    def chat(self, question, page):
        print(question, page)
        docs_returned = self.vector_db.similarity_search(question, k=5, filter={'page':{'$lt': page}})
        paragraph = '\n'.join([x.page_content for x in docs_returned])

        f = '''Answer the question based on the information provided in the paragraph. Do not include information that is not explicitly stated in the paragraph. If the answer cannot be found in the paragraph, respond with "The answer is not available in the paragraph."'''

        q1 = '''Paragraph:
        The Amazon rainforest is the largest tropical rainforest in the world, covering over 5.5 million square kilometers. It is home to diverse species of plants, animals, and indigenous communities. The rainforest plays a critical role in regulating the Earth's climate by absorbing vast amounts of carbon dioxide.

        Question:
        What is the role of the Amazon rainforest in regulating the Earth's climate?'''

        a1 = '''Answer:
        The Amazon rainforest regulates the Earth's climate by absorbing vast amounts of carbon dioxide.
        '''

        q2 = '''Paragraph:
        Eleanor spent hours in the dimly lit library, poring over old maritime charts and journals. The more she read, the clearer it became that Captain Winslow’s final voyage was not an ordinary trading mission. The maps marked a route far north, past the usual shipping lanes, and the journal entries hinted at "treasures of the deep" that could reshape their understanding of the ocean’s depths. Yet, Eleanor found no mention of what became of the ship or its crew.

        Question:
        What clues suggested Captain Winslow’s final voyage was unusual?'''

        a2 = '''Answer:
        The maps marked a route far north, past the usual shipping lanes, and the journal entries hinted at "treasures of the deep" that could reshape their understanding of the ocean’s depths.
        '''

        q3 = '''Paragraph:
        Dr. Hargrove’s lectures were known for their peculiar structure. He often began with anecdotes about seemingly unrelated historical events before weaving them into the complex theories of molecular biology he aimed to explain. Students frequently found themselves perplexed at the start, only to experience a moment of clarity when the connections were finally revealed. Still, many struggled to keep up with the leaps in logic, describing his classes as both fascinating and frustrating.

        Question:
        Why were Dr. Hargrove’s lectures considered frustrating by some students?'''

        a3 = '''Answer:
        Dr. Hargrove’s lectures were considered frustrating because many students struggled to keep up with the leaps in logic and the delay in understanding how his anecdotes connected to the theories of molecular biology.
        '''

        q4 = '''Paragraph:
        The old clockmaker’s shop, tucked away in a narrow alley, was filled with an assortment of ticking contraptions. Each clock had a story, the clockmaker often said, and none more so than the great pendulum clock that stood in the corner. Its face bore the scars of a fire long extinguished, and its hands moved erratically, as though struggling against the passage of time. Yet, customers were drawn to it, claiming they felt a strange sense of calm whenever they heard its uneven chimes.

        Question:
        What was unusual about the great pendulum clock in the clockmaker’s shop?'''

        a4 = '''Answer:
        The great pendulum clock had a scarred face from a fire and its hands moved erratically, as though struggling against the passage of time.
        '''

        q5 = '''Paragraph:
        When the king’s caravan arrived at the gates of Lyonesse, the city’s famed golden spires were shrouded in twilight. The herald’s voice rang out, calling for an audience with the city’s rulers, but no response came. Inside the walls, the streets lay deserted, with only faint whispers carried on the wind. Those who ventured close to the gates later spoke of shadows moving along the parapets, though no one dared to claim they saw the inhabitants themselves.

        Question:
        What did people notice about Lyonesse when the king’s caravan arrived?'''

        a5 = '''Answer:
        People noticed that the streets of Lyonesse were deserted, and faint whispers were carried on the wind. Some who ventured close to the gates claimed to see shadows moving along the parapets.
        '''

        q6 = '''Paragraph:
        The ancient manuscript contained cryptic symbols that scholars believed to be a form of early celestial mapping. Unlike modern star charts, these maps depicted constellations alongside diagrams of mythical creatures and elaborate geometric patterns. Some researchers theorized that the manuscript was not meant for navigation but for ceremonial purposes, reflecting the belief that the stars held divine significance.

        Question:
        What was one theory about the purpose of the ancient manuscript?'''

        a6 = '''Answer:
        One theory was that the manuscript was intended for ceremonial purposes, reflecting the belief that the stars held divine significance.
        '''

        q7 = '''Paragraph:
        {paragraph}

        Question:
        {question}'''
    

        prompt_template = ChatPromptTemplate.from_template(q7)
        messages = prompt_template.format_messages(paragraph=paragraph, question=question)
        prompt = messages[0].content
        print('Starting here: ',paragraph, ": Ending here")
        print(question)
        print(page)
        completion = self.client.chat.completions.create(
        model="Qwen/Qwen2.5-1.5B-Instruct", 
        messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": f},
        {"role": "assistant", "content": "Sure! Please provide the first question."},
    
        {"role": "user", "content": q1},
        {"role": "assistant", "content": a1},

        {"role": "user", "content": q2},
        {"role": "assistant", "content": a2},

        {"role": "user", "content": q3},
        {"role": "assistant", "content": a3},

        {"role": "user", "content": q4},
        {"role": "assistant", "content": a4},

        {"role": "user", "content": q5},
        {"role": "assistant", "content": a5},

        {"role": "user", "content": q6},
        {"role": "assistant", "content": a6},

        {"role": "user", "content": prompt},
                    ])
        
        return completion.choices[0].message.content




class LLMService:
    def __init__(self, api_key='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'):
        self.client = InferenceClient(api_key=api_key)
        prompt = ''
        self.all_messages = [[
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": "You will be given a word, and your task is to explain its meaning in a simple, clear, and easy-to-understand way. Avoid overly technical language, and use relatable examples when needed."},
            {"role": "assistant", "content": "Sure! Please provide the first word."},
            
            {"role": "user", "content": 'Word: "benevolent"'},
            {"role": "assistant", "content": "Meaning: Kind and caring towards others, often shown by helping those in need or making an effort to improve others' lives."},
            
            {"role": "user", "content": 'Word: "perplexed"'},
            {"role": "assistant", "content": "Meaning: Confused or unsure about something, like when you don’t understand a complicated problem or situation."},
            
            {"role": "user", "content": 'Word: "melancholy"'},
            {"role": "assistant", "content": "Meaning: A deep feeling of sadness or sorrow, often without a clear reason. It's different from just being a little sad—it’s a more lasting feeling."},
            
            {"role": "user", "content": 'Word: "frugal"'},
            {"role": "assistant", "content": "Meaning: Careful with money or resources, often by avoiding unnecessary spending and focusing on saving or being resourceful."},
            
            {"role": "user", "content": 'Word: "resilient"'},
            {"role": "assistant", "content": "Meaning: The ability to recover quickly from difficulties or setbacks, showing strength in the face of challenges."},
            
            {"role": "user", "content": prompt},
        ], 
                             [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": "You will be given a word and a paragraph in which the word is used. Your task is to explain the meaning of the word specifically in the context of the paragraph. Focus on how the word is being used and what it means in that particular situation, not its general or dictionary definition."},
        {"role": "assistant", "content": "Sure! Please provide the first paragraph and word."},
        
        {"role": "user", "content": 'Word: "perplexed"\nParagraph: Sarah was perplexed by the confusing instructions, not knowing whether to turn left or right. She stood there for several minutes, trying to figure out what the signs meant.'},
        {"role": "assistant", "content": 'Contextualized Meaning: In this paragraph, "perplexed" means that Sarah was very confused and unsure of what to do because the instructions were hard to understand.'},
        
        {"role": "user", "content": 'Word: "melancholy"\nParagraph: The rainy afternoon filled the room with a gloomy atmosphere, and John sat quietly by the window, lost in thoughts of his old friend. The melancholy feeling lingered as he watched the raindrops fall.'},
        {"role": "assistant", "content": 'Contextualized Meaning: In this context, "melancholy" refers to a deep, quiet sadness that John feels as he thinks about his old friend, intensified by the rainy, gloomy weather.'},
        
        {"role": "user", "content": 'Word: "frugal"\nParagraph: Although Henry could afford to buy expensive clothes, he chose to live frugally, always looking for sales and wearing his clothes until they were worn out.'},
        {"role": "assistant", "content": 'Contextualized Meaning: Here, "frugal" means that Henry chooses to spend his money carefully and avoid buying things he doesn’t need, even though he has enough money.'},
        
        {"role": "user", "content": '''Word: "ominous"\nParagraph: The dark clouds gathered rapidly, casting an ominous shadow over the small village. The wind howled through the trees, and the distant sound of thunder echoed across the valley.'''},
        {"role": "assistant", "content": '''Contextualized Meaning: Here, "ominous" means that the shadow created by the dark clouds feels threatening or foreboding, suggesting that something bad, like a storm, is about to happen.'''},
        
        {"role": "user", "content": '''Word: "garrulous"\nParagraph: As confided to a neighbor's servant by the garrulous midwife, who had then in turn told anyone who would listen, Sanaubar had taken one glance at the baby in Ali's arms, seen the cleft lip, and barked a bitter laughter.'''},
        {"role": "assistant", "content": 'Contextualized Meaning: In this paragraph, "garrulous" means that the midwife was excessively talkative, freely sharing private or sensitive information with anyone willing to listen.'},
        
        {"role": "user", "content": prompt},
        ],
                             
        [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": "You will be given a word, and your task is to create a sentence that makes the meaning of the word clear from its context. The sentence should not define the word directly but should provide enough clues so that the reader understands what the word means."},
        {"role": "assistant", "content": "Sure! Please provide the first word."},
        
        {"role": "user", "content": 'Word: "benevolent"'},
        {"role": "assistant", "content": 'Sentence: The benevolent king gave half of his fortune to help the poor and build schools for the underprivileged.'},
        
        {"role": "user", "content": 'Word: "perplexed"'},
        {"role": "assistant", "content": 'Sentence: Sarah was perplexed by the confusing instructions, not knowing whether to turn left or right.'},
        
        {"role": "user", "content": 'Word: "melancholy"'},
        {"role": "assistant", "content": 'Sentence: After the loss of his friend, John felt a deep sense of melancholy, a sadness that he couldn’t shake off.'},
        
        {"role": "user", "content": 'Word: "frugal"'},
        {"role": "assistant", "content": 'Sentence: Even though he earned a decent salary, Jack was frugal, always buying the cheapest items and saving the rest of his money for a rainy day.'},
        
        {"role": "user", "content": 'Word: "resilient"'},
        {"role": "assistant", "content": 'Sentence: Despite all the challenges she faced, Maria remained resilient, bouncing back stronger after every setback.'},
        
        {"role": "user", "content": prompt},
        ]
                             
         ]
        

    def generate_response(self, prompt, ind):
        messages = self.all_messages[ind]
        messages[-1]['content'] = prompt
        completion = self.client.chat.completions.create(
            model="Qwen/Qwen2.5-1.5B-Instruct", 
            messages=messages, 
            max_tokens=500, temperature=0.1)
        
        return completion.choices[0].message.content




class Text2SpeechService:
    def __init__(self):
        #Initialize the text-to-speech pipeline and load speaker embeddings
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts")
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
    
    
    
    