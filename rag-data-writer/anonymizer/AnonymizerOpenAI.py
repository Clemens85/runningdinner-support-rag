from openai import OpenAI
from .Anonymizer import Anonymizer
from .AnonymizerUtil import map_language_code_to_label, generate_anonymize_prompt

class AnonymizerOpenAI(Anonymizer):

    def __init__(self, skip_anonymization: bool = False, model = "gpt-4o", temperature: float = 0):
        self.skip_anonymization = skip_anonymization
        self.openai_client = OpenAI()
        self.model = model
        self.temperature = temperature


    def anonymize_personal_data(self, text: str, language_code: str) -> str:
        if self.skip_anonymization:
            return text

        language = map_language_code_to_label(language_code)

        prompt = generate_anonymize_prompt(text, language)
        anonymization_response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that anonymizes personal data in texts."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
        )
        anonymized_text = anonymization_response.choices[0].message.content.strip()
        return anonymized_text
