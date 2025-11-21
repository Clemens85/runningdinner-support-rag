from dataclasses import dataclass


@dataclass
class FeatureWriteRequest:
  feature_root_dir: str
  feature_name: str
  i18n_files: list[str]
