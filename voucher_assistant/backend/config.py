import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Elasticsearch Configuration
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    ELASTICSEARCH_INDEX: str = "voucher_knowledge_base"
    
    # Google Cloud Configuration
    GOOGLE_PROJECT_ID: str = os.getenv("GOOGLE_PROJECT_ID", "")
    GOOGLE_REGION: str = os.getenv("GOOGLE_REGION", "asia-southeast1")
    VERTEX_AI_ENDPOINT: str = os.getenv("VERTEX_AI_ENDPOINT", "")
    
    # Embedding Configuration
    # EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_MODEL: str = "dangvantuan/vietnamese-embedding"
    EMBEDDING_DIMENSION: int = 768
    
    # RAG Configuration
    MAX_CONTEXT_LENGTH: int = 4000
    TOP_K_RESULTS: int = 5
    CONFIDENCE_THRESHOLD: float = 0.7
    
    #   Specific Configuration
    ONEU_KNOWLEDGE_BASE_PATH: str = "data/oneu_knowledge/"
    UPOINT_RULES_PATH: str = "data/upoint_rules.json"
    PAYMENT_METHODS_PATH: str = "data/payment_methods.json"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]

settings = Settings()
