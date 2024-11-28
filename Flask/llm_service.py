from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from datasets import load_dataset
from IPython.display import Audio
import tempfile
import soundfile as sf





class LLMService:
    def __init__(self, model_name="gpt2", device='cpu'):
        # Initialize the tokenizer and model
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device)
        self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_response(self, prompt):
        # Generate a response based on the input prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(inputs["input_ids"],
                                      attention_mask=inputs["attention_mask"],
                                      max_length=500, num_return_sequences=1, repetition_penalty = 3.0)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response



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
    
    
    
    