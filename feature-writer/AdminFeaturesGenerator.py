import os
from FeatureWriteRequest import FeatureWriteRequest
from FeatureDescriptionGenerator import FeatureDescriptionGenerator

PROJECT_ROOT = '/home/clemens/Projects/runningdinner/runningdinner-client'

ADMIN_I18N_FILE = f"{PROJECT_ROOT}/shared/src/i18n/translations/de/AdminMessages_lang_de.json"
COMMON_I18N_FILE = f"{PROJECT_ROOT}/shared/src/i18n/translations/de/CommonMessages_lang_de.json"

DASHBOARD_ROOT = f"{PROJECT_ROOT}/webapp/src/admin/dashboard"
TEAMS_ROOT = f"{PROJECT_ROOT}/webapp/src/admin/teams"
PARTICIPANTS_ROOT = f"{PROJECT_ROOT}/webapp/src/admin/participants"
HOST_LOCATIONS_ROOT = f"{PROJECT_ROOT}/webapp/src/admin/hostlocations"
MESSAGES_ROOT = f"{PROJECT_ROOT}/webapp/src/admin/messages"
SETTINGS_ROOT = f"{PROJECT_ROOT}/webapp/src/admin/settings"

class AdminFeaturesGenerator:
    def __init__(self, generator: FeatureDescriptionGenerator):
        self.generator = generator

    def generate(self):

        dashboard_feature: FeatureWriteRequest = FeatureWriteRequest(
            feature_root_dir=DASHBOARD_ROOT,
            feature_name="Dashboard",
            i18n_files=[ADMIN_I18N_FILE]
        )
        participants_feature: FeatureWriteRequest = FeatureWriteRequest(
            feature_root_dir=PARTICIPANTS_ROOT,
            feature_name="Teilnehmer",
            i18n_files=[ADMIN_I18N_FILE, COMMON_I18N_FILE]
        )
        teams_feature: FeatureWriteRequest = FeatureWriteRequest(
            feature_root_dir=TEAMS_ROOT,
            feature_name="Teams",
            i18n_files=[ADMIN_I18N_FILE, COMMON_I18N_FILE]
        )
        route_cockpit_feature: FeatureWriteRequest = FeatureWriteRequest(
            feature_root_dir=HOST_LOCATIONS_ROOT,
            feature_name="Dinner Routen Übersicht",
            i18n_files=[ADMIN_I18N_FILE, COMMON_I18N_FILE]
        ) 
        messages_feature: FeatureWriteRequest = FeatureWriteRequest(
            feature_root_dir=MESSAGES_ROOT,
            feature_name="Nachrichtenversand",
            i18n_files=[ADMIN_I18N_FILE, COMMON_I18N_FILE]
        )   
        settings_feature: FeatureWriteRequest = FeatureWriteRequest(
            feature_root_dir=SETTINGS_ROOT,
            feature_name="Einstellungen",
            i18n_files=[ADMIN_I18N_FILE, COMMON_I18N_FILE]
        )

        features_to_generate = [
            dashboard_feature,
            participants_feature,
            teams_feature,
            route_cockpit_feature,
            messages_feature,
            settings_feature 
        ]

        for feature_request in features_to_generate:
            description = self.generator.generate_feature_description(request=feature_request)
            self.generator.write_feature_description_to_file(description, get_admin_output_path(feature_request.feature_name))


def get_admin_output_path(feature_name: str) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, f"output/admin/{feature_name}.md")