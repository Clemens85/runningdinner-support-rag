import torch
from transformers import pipeline


class LanguageDetector:
    
    def __init__(self):
        self._language_detector = None
    
    @property
    def language_detector(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        """Lazy load the language detection model"""
        if self._language_detector is None:
            # Using papluca/xlm-roberta-base-language-detection
            # This is a state-of-the-art model for language identification
            # It's lightweight (560MB) and supports 20 languages including German and English
            self._language_detector = pipeline(
                "text-classification",
                model="papluca/xlm-roberta-base-language-detection",
                device=device
            )
        return self._language_detector

    def detect_language(self, text: str) -> str:
        """
        Detects the language of the given text using a Huggingface model.
        
        Returns 'en' for English, 'de' for German.
        The model supports 20 languages, but we simplify the output to just 'en' or 'de'
        since those are the only two languages in our dataset.
        
        Args:
            text: The text to detect the language for
            
        Returns:
            'en' for English, 'de' for German (or any other language)
        """
        if not text or not text.strip():
            return 'de'  # Default to German for empty text
        
        # Truncate text if too long (model has max token limit)
        max_chars = 512
        text_sample = text[:max_chars] if len(text) > max_chars else text
        
        # Get prediction from the model
        result = self.language_detector(text_sample, top_k=1)
        detected_lang = result[0]['label'] or ''
        
        # Return 'en' if English is detected, otherwise return 'de'
        language_code = 'en' if detected_lang.lower() == 'en' else 'de'
        
        return language_code
