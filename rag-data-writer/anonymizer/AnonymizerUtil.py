ANONYMIZED_NAMES = [
    "Max Mustermann",
    "Maria Musterfrau",
    "Erika Mustermann",
    "John Doe",
]

ANONYMIZED_CITIES = [
    "Musterstadt",
    "Beispielstadt",
    "Demostadt"
]

ANONYMIZED_STREETS = [
    "Musterstraße 1",
    "Beispielweg 2",
    "Demoweg 3"
]

ANONYMIZED_EMAILS = [
    "max@mustermann.de",
    "maria@musterfrau.de",
    "erkia@musterfrau.de"
]

ASSISTANT_NAME = "RunYourDinner Team"
SUPPORT_PERSON_NAMES_LOWERCASE = ["Clemens Stich", "Clemens"]


def generate_anonymize_prompt(src_text: str, language: str):
    return f"""
    Anonymize the following {language} text by replacing personal data such as names (can be fullname or firstnames and lastnames), addresses, phone numbers and email addresses.
    Ensure that the anonymized text maintains the original meaning and context while removing all personal identifiers. You shall not change the text, just anonymize personal data.
    The given texts are quite small, there will be only few personal data to anonymize. It is important to to not randomly invent new personal data, but use the following fixed anonymized data replacements:
    Names: {', '.join(ANONYMIZED_NAMES)}
    Cities: {', '.join(ANONYMIZED_CITIES)}
    Streets: {', '.join(ANONYMIZED_STREETS)}
    Emails: {', '.join(ANONYMIZED_EMAILS)}
    
    When you encounter one real name (like "Michael Becker"), replace it with the first of the anonymized names (like "Max Mustermann") and keep this replacement consistent throughout the text.
    If you encounter another next real name (like "Jona Schmidt") replace it with the next anonymized name in the list (like "Maria Musterfrau") and so on.
    This is very important to ensure that the same personal data is always replaced with the same anonymized data.
    
    The provided {language} text is passed in markdown format and reflects a conversation between a user (marked with headline '## User') and an assistant (marked with headline '## Assistant').
    The Assistant is a real person from support and is almost always named "Clemens' or 'Clemens Stich'.
    When you find these names in the text, replace them with {ASSISTANT_NAME} and do not apply any further anonymization to this name. Do this always first before applying other anonymizations.
    
    Return only the anonymized text without any additional explanations.
    
    Here is the text to anonymize:\n\n{src_text}\n\nAnonymized text:
    """

def map_language_code_to_label(language_code: str) -> str:
    language_map = {
        "de": "German",
        "en": "English",
    }
    return language_map.get(language_code, "German")  # Default to German if not found