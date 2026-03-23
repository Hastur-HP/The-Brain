import os
from pathlib import Path

# Engine selection
LLM_ENGINE = os.getenv("LLM_ENGINE", "ollama").lower()

# Base URLs
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LLAMA_CPP_BASE_URL = os.getenv("LLAMA_CPP_BASE_URL", "http://localhost:8080/v1")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
RERANKER_BASE_URL = os.getenv("RERANKER_BASE_URL", "")

# External API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-no-key-required")

# Model names
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3.5:9b")
VISION_MODEL = os.getenv("VISION_MODEL", "qwen2.5vl:latest")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "qwen3-embedding:8b")
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")

# Model settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP_SIZE", "100"))
LLM_NUM_CTX = int(os.getenv("LLM_NUM_CTX", "32768"))
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "7200"))
LLM_MAX_ASYNC = int(os.getenv("LLM_MAX_ASYNC", "1"))
EMBEDDING_TIMEOUT = int(os.getenv("EMBEDDING_TIMEOUT", "300"))
EMBEDDING_MAX_ASYNC = int(os.getenv("EMBEDDING_MAX_ASYNC", "1"))
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "4096"))
MAX_EMBED_TOKENS = int(os.getenv("MAX_EMBED_TOKENS", "8192"))
RERANKER_MAX_BATCH_SIZE = int(os.getenv("RERANKER_MAX_BATCH_SIZE", 4))

# Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Filestructure
WORKING_DIR = os.getenv("WORKING_DIR", "/app/rag_storage")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")
PARSER = os.getenv("PARSER", "mineru")

# Persistent files
HIDDEN_TYPES_FILE = Path(WORKING_DIR) / "hidden_types.json"
CONV_FILE = Path(WORKING_DIR) / "conversations.json"
COMPLETED_LOG = Path(WORKING_DIR) / "completed_docs.json"

# Document settings
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".pptx", ".xlsx"}
MAX_UPLOAD_BYTES = 500 * 1024 * 1024  # 500 MB
