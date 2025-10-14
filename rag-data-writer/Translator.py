from openai import OpenAI

class Translator:
    def __init__(self, model = "gpt-4o", temperature: float = 0.2, max_tokens: int = 4048):
        self.openai_client = OpenAI()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def translate_to_german(self, text: str) -> str:
        translation_prompt = f"""
        Translate the following text which is formatted in Markdown to German.
        Return only the German translation and preserve the markdown structure in your translation. 
        There are headlines in the markdown text which contain phrases like ## User or ## Assistant. Those healines should not be translated, but preserved as they are.
        Return no further explanations and no further informations. Here is the German text:\n\n{text}\n\nGerman translation:
        """
        translation_response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates texts to German."},
                {"role": "user", "content": translation_prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        german_translation = translation_response.choices[0].message.content.strip()
        return german_translation