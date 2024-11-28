from datasets import load_dataset
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig, TrainingArguments, Trainer
import torch
import time
#import evaluate
import pandas as pd
import numpy as np


from transformers import AutoModelForCausalLM, AutoTokenizer
model_name = "Qwen/Qwen2.5-1.5B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

few_shot_prompt_sentences = """
You will be given a word, and your task is to create a sentence that makes the meaning of the word clear from its context. The sentence should not define the word directly but should provide enough clues so that the reader understands what the word means.

### Examples

Word: "benevolent"
Sentence: The benevolent king gave half of his fortune to help the poor and build schools for the underprivileged.

Word: "perplexed"
Sentence: Sarah was perplexed by the confusing instructions, not knowing whether to turn left or right.

Word: "melancholy"
Sentence: After the loss of his friend, John felt a deep sense of melancholy, a sadness that he couldn’t shake off.

Word: "frugal"
Sentence: Even though he earned a decent salary, Jack was frugal, always buying the cheapest items and saving the rest of his money for a rainy day.

Word: "resilient"
Sentence: Despite all the challenges she faced, Maria remained resilient, bouncing back stronger after every setback.

Word: "garrulous"
Sentence: 
"""

few_shot_prompt_sentences_child_friendly = """
You will be given a word, and your task is to create a sentence that makes the meaning of the word clear from its context. The sentence should not define the word directly but should provide enough clues so that even a child can understand what the word means. Use simple language and examples.

### Examples

Word: "benevolent"
Sentence: The benevolent teacher gave her students extra time to finish their homework and even brought snacks for everyone.

Word: "perplexed"
Sentence: Emma was perplexed when she looked at the puzzle because she couldn’t figure out where the pieces should go.

Word: "melancholy"
Sentence: After her pet fish died, Sarah sat in her room feeling very melancholy, staring at the empty fishbowl.

Word: "frugal"
Sentence: Even though Tom had money to buy a new toy, he decided to be frugal and save it for something more important later.

Word: "resilient"
Sentence: Even though Jamie fell off his bike and scraped his knee, he was resilient and got right back on to try again.

Word: {word}
Sentence: 
"""

few_shot_prompt_meanings = """
You will be given a word, and your task is to explain its meaning in a way that a child can understand. Use simple language, examples, or comparisons to make the meaning clear. The explanation should be short and easy to grasp.

### Examples

Word: "benevolent"
Meaning: Being kind and helping others, like when someone gives their toys to a friend who doesn’t have any.

Word: "perplexed"
Meaning: Feeling confused, like when you don’t understand how to finish a puzzle.

Word: "melancholy"
Meaning: Feeling very sad for a long time, like missing your favorite pet when it’s gone.

Word: "frugal"
Meaning: Being careful with money, like saving your allowance instead of spending it all at once.

Word: "resilient"
Meaning: Being strong and able to keep going, like when you fall down but get back up to try again.

Word: {word}
Meaning: 
"""

few_shot_contextualized_meanings = """
You will be given a word and a paragraph in which the word is used. Your task is to explain the meaning of the word specifically in the context of the paragraph. Focus on how the word is being used and what it means in that particular situation, not its general or dictionary definition.

### Examples

Word: "perplexed"
Paragraph: Sarah was perplexed by the confusing instructions, not knowing whether to turn left or right. She stood there for several minutes, trying to figure out what the signs meant.
Contextualized Meaning: In this paragraph, "perplexed" means that Sarah was very confused and unsure of what to do because the instructions were hard to understand.

Word: "melancholy"
Paragraph: The rainy afternoon filled the room with a gloomy atmosphere, and John sat quietly by the window, lost in thoughts of his old friend. The melancholy feeling lingered as he watched the raindrops fall.
Contextualized Meaning: In this context, "melancholy" refers to a deep, quiet sadness that John feels as he thinks about his old friend, intensified by the rainy, gloomy weather.

Word: "frugal"
Paragraph: Although Henry could afford to buy expensive clothes, he chose to live frugally, always looking for sales and wearing his clothes until they were worn out.
Contextualized Meaning: Here, "frugal" means that Henry chooses to spend his money carefully and avoid buying things he doesn’t need, even though he has enough money.

Word: "garrulous"
Paragraph: As confided to a neighbor's servant by the garrulous midwife, who had then in turn told anyone who would listen, Sanaubar had taken one glance at the baby in Ali's arms, seen the cleft lip, and barked a bitter laughter.
Contextualized Meaning: 
"""

few_shot_child_friendly_contextualized_meanings = """
You will be given a word and a paragraph in which the word is used. Your task is to explain the meaning of the word specifically in the context of the paragraph, but in a way that would be easy for a child to understand. Focus on how the word is being used in that particular situation and use simple language, examples, or comparisons to make it clear.

### Examples

Word: "perplexed"
Paragraph: Sarah was perplexed by the confusing instructions, not knowing whether to turn left or right. She stood there for several minutes, trying to figure out what the signs meant.
Contextualized Meaning: In this paragraph, "perplexed" means Sarah was really confused because she didn’t understand which way to go. It’s like when you don’t know how to finish a game and you’re not sure what to do next.

Word: "melancholy"
Paragraph: The rainy afternoon filled the room with a gloomy atmosphere, and John sat quietly by the window, lost in thoughts of his old friend. The melancholy feeling lingered as he watched the raindrops fall.
Contextualized Meaning: Here, "melancholy" means John feels very sad and quiet, like when you miss someone you care about, and it’s even harder because the weather is dark and rainy.

Word: "frugal"
Paragraph: Although Henry could afford to buy expensive clothes, he chose to live frugally, always looking for sales and wearing his clothes until they were worn out.
Contextualized Meaning: In this paragraph, "frugal" means Henry is careful with his money and doesn’t spend it on new clothes unless he really needs to, even though he has enough money. It’s like saving your allowance instead of buying new toys right away.

Word: {word}
Paragraph: {paragraph}
Contextualized Meaning: 
"""




prompts=[few_shot_prompt_meanings,
         few_shot_prompt_sentences_child_friendly,
        few_shot_child_friendly_contextualized_meanings]

from langchain.prompts import ChatPromptTemplate

def prompt_templates(word, paragraph):
    final_prompts=[]
    
    for prompt in prompts:
        prompt_template = ChatPromptTemplate.from_template(prompt)
        try:
            messages = prompt_template.format_messages(word=word)
        except:
            messages = prompt_template.format_messages(word=word, paragraph = paragraph)

        prompt = messages[0].content
        final_prompts.append(prompt)
    
    return final_prompts


def generate_response(prompt):
    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return response




word="imbecile"
paragraph = '''My favorite part of reading to Hassan was when we came across a big word that he didn't know. I'd tease him, expose his ignorance. One time, I was reading him a Mullah Nasruddin story and he stopped me. "What does that word mean?"
"Which one?"
"Imbecile."
"You don't know what it means?" I said, grinning.
"Nay, Amir agha."'''

final_prompts = prompt_templates(word, paragraph)



l=[f'Meaning of the word ', f'Putting in another sentence the word ', f'Contextual meaning of the word ']

for i in range(len(final_prompts)):
    response = generate_response(final_prompts[i])
    print(f'{l[i]}{word}:\n{response}\n\n\n\n')
    
