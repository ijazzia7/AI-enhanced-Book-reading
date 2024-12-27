from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from datasets import load_dataset
from IPython.display import Audio
import tempfile
import soundfile as sf
from huggingface_hub import InferenceClient






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
        # Initialize the text-to-speech pipeline and load speaker embeddings
        self.synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts")
        self.embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        self.speaker_embedding = torch.tensor(self.embeddings_dataset[7306]["xvector"]).unsqueeze(0)

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
    
    
    
    