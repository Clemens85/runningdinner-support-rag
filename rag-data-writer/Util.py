import os
from dotenv import load_dotenv

def setup_environment():
  load_dotenv(override=True)
  os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

  if (os.environ.get('OPENAI_API_KEY') is None) or (os.environ.get('OPENAI_API_KEY') == ''):
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")
