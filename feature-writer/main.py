from dotenv import load_dotenv
from ChatOpenAI import ChatOpenAI
from FeatureDescriptionGenerator import FeatureDescriptionGenerator
from AdminFeaturesGenerator import AdminFeaturesGenerator
import os
from FeatureWriteRequest import FeatureWriteRequest

PROJECT_ROOT = '/home/clemens/Projects/runningdinner/runningdinner-client'

COMMON_I18N_FILE = f"{PROJECT_ROOT}/shared/src/i18n/translations/de/CommonMessages_lang_de.json"

SELF_I18N_FILE = f"{PROJECT_ROOT}/shared/src/i18n/translations/de/SelfAdminMessages_lang_de.ts"
SELF_SERVICE_ROOT = f"{PROJECT_ROOT}/webapp/src/self"

LANDING_I18N_FILE = f"{PROJECT_ROOT}/shared/src/i18n/translations/de/LandingMessages_lang_de.ts"
LANDING_ROOT = f"{PROJECT_ROOT}/webapp/src/landing"

#OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MODEL = "gpt-4.1-mini"
TEMPERATURE = 0.1

load_dotenv(override=True)

def main():

  model = ChatOpenAI(model=OPENAI_MODEL, temperature=TEMPERATURE)
  generator = FeatureDescriptionGenerator(model=model)

  admin_features_generator = AdminFeaturesGenerator(generator=generator)
  admin_features_generator.generate()
  concat_feature_files(feature_collection="admin")

  self_feature_request: FeatureWriteRequest = FeatureWriteRequest(
      feature_root_dir=SELF_SERVICE_ROOT,
      feature_name="Teilnehmer Self Service",
      i18n_files=[SELF_I18N_FILE, COMMON_I18N_FILE]
  )

  landing_feature_request: FeatureWriteRequest = FeatureWriteRequest(
      feature_root_dir=LANDING_ROOT,
      feature_name="Startseite",
      i18n_files=[COMMON_I18N_FILE, LANDING_I18N_FILE]
  )

  generate_feature_description_for_request(generator, self_feature_request, "self_service")
  generate_feature_description_for_request(generator, landing_feature_request, "landing")
  

def generate_feature_description_for_request(generator: FeatureDescriptionGenerator, request: FeatureWriteRequest, feature_collection_name: str):
  
  script_dir = os.path.dirname(os.path.abspath(__file__))
  output_file_path = os.path.join(script_dir, f"output/{feature_collection_name}/{feature_collection_name}.md")

  description = generator.generate_feature_description(request=request)
  generator.write_feature_description_to_file(description, output_file_path)
  concat_feature_files(feature_collection=feature_collection_name)


def concat_feature_files(feature_collection: str):
  script_dir = os.path.dirname(os.path.abspath(__file__))
  output_dir = os.path.join(script_dir, "output", feature_collection)
  all_files = [f for f in os.listdir(output_dir) if f.endswith(".md")]
  all_contents = []
  for filename in all_files:
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "r") as f:
      content = f.read()
      all_contents.append(f"{content}\n\n---\n\n")
  
  concatenated_content = "\n".join(all_contents)
  concatenated_filepath = os.path.join(script_dir, "output", f"{feature_collection}_all_features.md")
  with open(concatenated_filepath, "w") as f:
    f.write(concatenated_content)
  print(f"Wrote concatenated feature descriptions to {concatenated_filepath}")

# def get_admin_output_path(feature_name: str) -> str:
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(script_dir, f"output/admin/{feature_name}.md")

if __name__ == '__main__':
    main()