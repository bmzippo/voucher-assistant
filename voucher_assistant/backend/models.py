from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class VoucherData(BaseModel):
    """Model for voucher data"""
    name: str
    description: str
    usage_instructions: str
    terms_of_use: str
    tags: Optional[str] = None
    location: Optional[str] = None
    price: int
    unit: int
    merchant: str
    
class VoucherSummary(BaseModel):
    """Model for voucher summary response"""
    voucher_id: str
    name: str
    key_points: List[str]
    discount_amount: str
    validity_period: Optional[str] = None
    usage_restrictions: List[str]
    merchant: str

class ChatMessage(BaseModel):
    """Model for chat messages"""
    message: str
    timestamp: Optional[datetime] = None

class VectorSearchRequest(BaseModel):
    """Model for vector search requests"""
    query: str
    top_k: Optional[int] = 5
    min_score: Optional[float] = 0.7

class VectorSearchResult(BaseModel):
    """Model for vector search result items"""
    voucher_id: str
    voucher_name: str
    content: str
    similarity_score: float
    raw_score: float
    metadata: Dict[str, Any]
    created_at: Optional[str] = None
    search_query: str

class VectorSearchResponse(BaseModel):
    """Model for vector search response"""
    query: str
    results: List[VectorSearchResult]
    total_results: int
    search_time_ms: Optional[float] = None
    embedding_dimension: int

class HybridSearchResponse(BaseModel):
    """Model for hybrid search response"""
    query: str
    vector_results: List[VectorSearchResult]
    text_results: List[Dict[str, Any]]
    total_vector_results: int
    total_text_results: int
    search_time_ms: Optional[float] = None
    
class ChatResponse(BaseModel):
    """Model for chat response"""
    response: str
    confidence_score: float
    sources: List[str]
    timestamp: datetime

class EmbeddingRequest(BaseModel):
    """Model for embedding requests"""
    text: str
    
class EmbeddingResponse(BaseModel):
    """Model for embedding response"""
    embedding: List[float]
    
class SearchRequest(BaseModel):
    """Model for search requests"""
    query: str
    voucher_id: Optional[str] = None
    top_k: int = 5
    
class SearchResult(BaseModel):
    """Model for search results"""
    content: str
    score: float
    metadata: Dict[str, Any]
