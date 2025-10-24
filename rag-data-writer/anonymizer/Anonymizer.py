from abc import ABC, abstractmethod

class Anonymizer(ABC):
    @abstractmethod
    def anonymize_personal_data(self, text: str, language_code: str) -> str:
        pass