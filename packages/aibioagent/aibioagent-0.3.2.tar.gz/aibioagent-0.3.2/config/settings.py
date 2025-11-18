import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from current working directory
# This allows users to have .env in their project folder
load_dotenv(dotenv_path=Path.cwd() / ".env")

# Access the API key and store constants
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = "gpt-4o-mini"        # Default model
VISION_LLM_MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"    # vector embedding
CHROMA_DIR = "data/chroma_db"

# API key is optional - can be set later with aba.set_api_key()
