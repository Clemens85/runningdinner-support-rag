from dotenv import load_dotenv
from ChatOpenAI import ChatOpenAI
from FeatureDescriptionGenerator import FeatureDescriptionGenerator, FeatureWriteRequest
import os

PROJECT_ROOT = '/home/clemens/Projects/runningdinner/runningdinner-client'

DASHBOARD_ROOT = f"{PROJECT_ROOT}/webapp/src/admin/dashboard"
TEAMS_ROOT = f"{PROJECT_ROOT}/webapp/src/admin/teams"
HOST_LOCATIONS_ROOT = f"{PROJECT_ROOT}/webapp/src/admin/hostlocations"
MESSAGES_ROOT = f"{PROJECT_ROOT}/webapp/src/admin/messages"

ADMIN_I18N_FILE = f"{PROJECT_ROOT}/shared/src/i18n/translations/de/AdminMessages_lang_de.json"
COMMON_I18N_FILE = f"{PROJECT_ROOT}/shared/src/i18n/translations/de/CommonMessages_lang_de.json"

OPENAI_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.1

load_dotenv(override=True)

def main():

  model = ChatOpenAI(model=OPENAI_MODEL, temperature=TEMPERATURE)
  generator = FeatureDescriptionGenerator(model=model)

  # feature_name = "Dashboard"
  # request: FeatureWriteRequest = FeatureWriteRequest(
  #   feature_root_dir=DASHBOARD_ROOT,
  #   feature_name=feature_name,
  #   i18n_files=[ADMIN_I18N_FILE]
  # )
  # description = generator.generate_feature_description(request=request)
  # generator.write_feature_description_to_file(description, get_admin_output_path("Dashboard"))

  # feature_name = "Teams"
  # request: FeatureWriteRequest = FeatureWriteRequest(
  #   feature_root_dir=TEAMS_ROOT,
  #   feature_name=feature_name,
  #   i18n_files=[ADMIN_I18N_FILE, COMMON_I18N_FILE]
  # )
  # description = generator.generate_feature_description(request=request)
  # generator.write_feature_description_to_file(description, get_admin_output_path("Teams"))


  # feature_name = "Dinner Routen Übersicht"
  # request: FeatureWriteRequest = FeatureWriteRequest(
  #   feature_root_dir=HOST_LOCATIONS_ROOT,
  #   feature_name=feature_name,
  #   i18n_files=[ADMIN_I18N_FILE, COMMON_I18N_FILE]
  # )
  # description = generator.generate_feature_description(request=request)
  # generator.write_feature_description_to_file(description, get_admin_output_path("Hostlocations"))

  # feature_name = "Nachrichtenversand"
  # request: FeatureWriteRequest = FeatureWriteRequest(
  #   feature_root_dir=MESSAGES_ROOT,
  #   feature_name=feature_name,
  #   i18n_files=[ADMIN_I18N_FILE, COMMON_I18N_FILE]
  # )
  # description = generator.generate_feature_description(request=request)
  # generator.write_feature_description_to_file(description, get_admin_output_path("Messages"))

  concat_feature_files(feature_collection="admin")

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

def get_admin_output_path(feature_name: str) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, f"output/admin/{feature_name}.md")

if __name__ == '__main__':
    main()