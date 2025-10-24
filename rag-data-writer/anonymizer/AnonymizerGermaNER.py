from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from peft import PeftModel, PeftConfig
from .Anonymizer import Anonymizer

#model_id = "fau/GermaNER"
model_id = "Davlan/xlm-roberta-base-ner-hrl"

# Define label mappings
label_names = ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
label2id = {label: idx for idx, label in enumerate(label_names)}
id2label = {idx: label for idx, label in enumerate(label_names)}

class AnonymizerGermaNER(Anonymizer):
    def __init__(self):
      self._ner_pipeline = None
      pass

    @property
    def ner_pipeline(self):
      # Load tokenizer
      tokenizer = AutoTokenizer.from_pretrained(model_id)
      # Load PEFT adapter config
      peft_config = PeftConfig.from_pretrained(model_id)
      # Load base model with label mappings
      base_model = AutoModelForTokenClassification.from_pretrained(
          peft_config.base_model_name_or_path,
          num_labels=len(label_names),
          id2label=id2label,
          label2id=label2id
      )
      # Attach adapter
      model = PeftModel.from_pretrained(base_model, model_id)
      # Create pipeline
      self._ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
      return self._ner_pipeline
    

    def anonymize_personal_data(self, text: str, language_code: str) -> str:
        anonymized_text = text  # Placeholder for actual anonymization logic

        ents = self.ner_pipeline(anonymized_text)
        print(ents)

        for ent in ents:
          print(f"{ent['word']} → {ent['entity_group']} (score: {ent['score']:.2f})")

        return anonymized_text