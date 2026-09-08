import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
CHAT_MODEL = os.environ.get("CHAT_MODEL", "llama3.2")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CHROMA_DIR = os.environ.get("CHROMA_DIR", "./chroma_db")
CHROMA_COLLECTION = "documents"
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "./uploads")

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week
