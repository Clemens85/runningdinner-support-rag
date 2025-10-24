PIPELINE_ROOT_DIR = "/home/clemens/Projects/runningdinner-support-rag/pipeline-data"

RAW_STAGE_DIR = f"{PIPELINE_ROOT_DIR}/stage-00-raw"
CURATED_STAGE_DIR=f"{PIPELINE_ROOT_DIR}/stage-01-curated"
ANONYMIZED_STAGE_DIR=f"{PIPELINE_ROOT_DIR}/stage-02-anonymized"
TRANSLATED_STAGE_DIR=f"{PIPELINE_ROOT_DIR}/stage-03-translated"

EMBEDDING_CACHE_DIR = f"{PIPELINE_ROOT_DIR}/.embedding-cache"

IMPORT_LOCK_FILE = f"{PIPELINE_ROOT_DIR}/import.lock"