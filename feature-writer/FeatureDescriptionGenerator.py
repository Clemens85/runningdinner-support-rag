from dataclasses import dataclass
from dotenv import load_dotenv
from RecursiveFilepathCollector import RecursiveFilepathCollector
from CodeFileReader import CodeFileReader
from Prompts import USER_PROMPT_TEMPLATE, SYSTEM_PROMPT
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

@dataclass
class FeatureWriteRequest:
  feature_root_dir: str
  feature_name: str
  i18n_files: list[str]


class FeatureDescriptionGenerator:
  def __init__(self, model):
    self.model = model
    pass

  def generate_feature_description(self, request: FeatureWriteRequest) -> str:

    collector = RecursiveFilepathCollector(request.feature_root_dir)
    filepaths = collector.collect_filepaths()

    files_content_arr = []
    for filepath in filepaths:
      reader = CodeFileReader(filepath=filepath)
      files_content_arr.append(reader.to_prompt_format())

    files_content_str = "\n\n---\n\n".join(files_content_arr)

    all_i18n = ""
    for i18n_file in request.i18n_files:
      i18n_file_reader = CodeFileReader(filepath=i18n_file)
      i18n_content = i18n_file_reader.read_content()
      all_i18n += f"{i18n_content}\n\n"

    user_prompt = USER_PROMPT_TEMPLATE.invoke({
      "feature_name": request.feature_name,
      "code_files": files_content_str,
      "i18n_en": all_i18n
    })

    prompt_template = ChatPromptTemplate([
      SystemMessage(content=SYSTEM_PROMPT),
      HumanMessage(content=user_prompt.to_string())
    ])
    prompt_value = prompt_template.invoke({})
    print (f"Invoking model with {len(prompt_value.to_string())} characters for feature {request.feature_name}...")

    response = self.model.invoke(prompt_value)
    return response.content
  
  def write_feature_description_to_file(self, description: str, output_filepath: str):
    with open(output_filepath, "w") as f:
      f.write(description)
    print(f"Wrote feature description to {output_filepath}")