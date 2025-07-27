import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    EMBEDDING_MODEL = "models/embedding-001"
    LLM_MODEL = "gemini-2.5-flash"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    SEARCH_K = 5
    TEMPERATURE = 0.3
    MAX_TOKENS = 1000
    PERSIST_DIR = "db"
    MAX_PAGES = 300
    MAX_FILES = 3
