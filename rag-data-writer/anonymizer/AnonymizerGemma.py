from dataclasses import dataclass
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from .AnonymizerUtil import map_language_code_to_label, generate_anonymize_prompt
from .Anonymizer import Anonymizer

model_id = "google/gemma-7b-it"

class AnonymizerGemma(Anonymizer):
    def __init__(self, skip_anonymization: bool = False):
        self._gemma_model = None
        self.skip_anonymization = skip_anonymization

    @property
    def gemma_model(self):
        # quantization_config = BitsAndBytesConfig(load_in_4bit=True)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            "google/gemma-7b-it",
            # quantization_config=quantization_config,
            # device_map="auto",
            torch_dtype=torch.bfloat16
        )
        self._gemma_model = GemmaModel(model=model, tokenizer=tokenizer)
        return self._gemma_model


    def anonymize_personal_data(self, text: str, language_code: str):
        language = map_language_code_to_label(language_code)

        prompt = generate_anonymize_prompt(text, language)

        chat = [
            { "role": "user", "content": prompt },
        ]
        self._execute_prompt(chat)    

        # tokenizer = self.gemma_model.tokenizer
        # model = self.gemma_model.model
        # input_text = "Write me a poem about Machine Learning."
        # input_ids = tokenizer(input_text, return_tensors="pt")#.to("cuda")
        # outputs = model.generate(**input_ids)
        # print(tokenizer.decode(outputs[0]))

    def _execute_prompt(self, chat_template: list):
        tokenizer = self.gemma_model.tokenizer
        model = self.gemma_model.model

        prompt = tokenizer.apply_chat_template(chat_template, tokenize=False, add_generation_prompt=True)

        inputs = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
        outputs = model.generate(input_ids=inputs.to(model.device), max_new_tokens=4048)
        print(tokenizer.decode(outputs[0]))

@dataclass
class GemmaModel:
    model: AutoModelForCausalLM
    tokenizer: AutoTokenizer