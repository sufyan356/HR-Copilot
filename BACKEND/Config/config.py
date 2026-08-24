import os
from dotenv import load_dotenv

# Load variables from root .env
load_dotenv()


# ============================================================
# GROQ / LLM
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")


# ============================================================
# POSTGRESQL
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL",)


# ============================================================
# QDRANT
# ============================================================

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

QDRANT_COLLECTION_NAME = os.getenv(
    "QDRANT_COLLECTION_NAME",
    "hr-copilot",
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ============================================================
# CROSS-ENCODER RERANKER
# ============================================================

RERANKER_MODEL = os.getenv(
    "RERANKER_MODEL",
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# ============================================================
# JWT AUTHENTICATION
# ============================================================

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")




DEBUG = os.getenv("DEBUG", "True").lower() == "true"