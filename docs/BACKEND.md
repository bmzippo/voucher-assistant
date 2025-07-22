# ⚙️ Backend Guide

> **  AI Voucher Assistant - Backend Development Guide**

## 📋 Table of Contents
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Development Setup](#development-setup)
- [Architecture Patterns](#architecture-patterns)
- [Testing Guide](#testing-guide)
- [Performance Optimization](#performance-optimization)

## 📁 Project Structure

```
voucher_assistant/backend/
├── advanced_main.py              # FastAPI application entry point
├── advanced_vector_store.py      # Multi-field embedding & hybrid search
├── smart_query_parser.py         # Vietnamese NLP & intent detection
├── location_aware_indexer.py     # Geographic indexing & ranking
├── requirements.txt               # Python dependencies
│
├── data_processing/               # Data pipeline components
│   ├── main_indexer.py           # Main data indexing script
│   ├── data_loader.py            # Excel/CSV data loading
│   ├── data_cleaner.py           # Data validation & cleaning
│   └── modular_indexer.py        # Modular indexing system
│
├── models/                        # Data models & schemas
│   ├── search_models.py          # Search request/response models
│   ├── voucher_models.py         # Voucher data models
│   └── error_models.py           # Error response models
│
├── services/                      # Business logic services
│   ├── search_service.py         # Search orchestration
│   ├── embedding_service.py      # AI/ML embedding operations
│   └── indexing_service.py       # Data indexing operations
│
├── utils/                         # Utility functions
│   ├── validators.py             # Input validation
│   ├── formatters.py             # Response formatting
│   └── logger.py                 # Logging configuration
│
└── tests/                         # Test suites
    ├── test_search.py            # Search functionality tests
    ├── test_parser.py            # Query parsing tests
    ├── test_indexing.py          # Data indexing tests
    └── fixtures/                 # Test data fixtures
```

## 🔧 Core Components

### 1. FastAPI Application (advanced_main.py)
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI components
vector_store = None
query_parser = None
location_indexer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global vector_store, query_parser, location_indexer
    
    logger.info("🚀 Initializing   Advanced AI Voucher Assistant...")
    
    # Initialize components
    vector_store = AdvancedVectorStore()
    query_parser = SmartQueryParser()
    location_indexer = LocationAwareIndexer()
    
    logger.info("✅ All advanced components initialized successfully!")
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title="  AI Voucher Assistant",
    description="Advanced voucher search and recommendation system",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/advanced-search")
async def advanced_search(request: AdvancedSearchRequest):
    """
    Advanced hybrid search endpoint
    Combines exact text search with semantic similarity
    """
    try:
        start_time = time.time()
        logger.info(f"🔍 Advanced search: '{request.query}'")
        
        # Parse query components
        parsed_query = query_parser.parse_query(request.query)
        
        # Execute advanced search
        results = await vector_store.advanced_vector_search(
            query=request.query,
            top_k=request.top_k,
            location_filter=request.location_filter,
            service_filter=request.service_filter,
            price_filter=request.price_filter
        )
        
        # Apply geographic ranking if location detected
        if parsed_query.location:
            results = location_indexer.apply_geographic_ranking(
                results, parsed_query.location
            )
        
        processing_time = (time.time() - start_time) * 1000
        
        return AdvancedSearchResponse(
            query=request.query,
            parsed_components=parsed_query,
            results=results,
            metadata={
                "total_results": len(results),
                "processing_time_ms": round(processing_time, 2),
                "search_method": "advanced_multi_field_with_intelligence",
                "embedding_dimensions": vector_store.embedding_dimension
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Advanced Vector Store (advanced_vector_store.py)
```python
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from dataclasses import dataclass

@dataclass
class EmbeddingWeights:
    """Weights for multi-field embeddings"""
    content: float = 0.4
    location: float = 0.3
    service_type: float = 0.15
    target_audience: float = 0.1
    keywords: float = 0.05

class AdvancedVectorStore:
    """
    Advanced Vector Store with multi-field embedding strategy
    Optimized for   ecosystem
    """
    
    def __init__(self, es_url: str = "http://localhost:9200", 
                 embedding_model: str = "dangvantuan/vietnamese-embedding",
                 index_name: str = "oneu_vouchers_advanced"):
        self.es_url = es_url
        self.es = Elasticsearch([es_url])
        self.index_name = index_name
        self.embedding_model_name = embedding_model
        self.embedding_dimension = 768
        self.weights = EmbeddingWeights()
        
        # Initialize embedding model
        self.model = SentenceTransformer(embedding_model)
        logger.info(f"🤖 Advanced Vector Store initialized with model: {embedding_model}")
        
        # Create advanced index mapping
        self._create_advanced_index()
    
    async def advanced_vector_search(self, query: str, top_k: int = 10,
                                   location_filter: Optional[str] = None,
                                   service_filter: Optional[str] = None,
                                   price_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Advanced search with multi-field embedding and filtering
        Implements hybrid search: exact text + semantic similarity
        """
        try:
            # Extract query components
            query_components = self._analyze_query(query)
            
            # Create query embedding based on detected intent
            query_embedding = self._create_adaptive_query_embedding(query, query_components)
            
            # Build Elasticsearch query with hybrid search
            search_body = self._build_hybrid_search_query(
                query_embedding, query_components, query, top_k, 
                location_filter, service_filter, price_filter
            )
            
            # Log query for debugging
            logger.info(f"🔍 Elasticsearch Query for '{query}':")
            logger.info(f"📋 Query Body: {json.dumps(search_body, indent=2, ensure_ascii=False)}")
            
            # Execute search
            response = self.es.search(index=self.index_name, body=search_body)
            
            # Process and rank results
            results = self._process_advanced_results(response, query_components)
            
            logger.info(f"✅ Advanced search completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Advanced search error: {e}")
            return []
    
    def _build_hybrid_search_query(self, query_embedding: np.ndarray, 
                                   query_components: Dict[str, Any],
                                   original_query: str,
                                   top_k: int,
                                   location_filter: Optional[str] = None,
                                   service_filter: Optional[str] = None,
                                   price_filter: Optional[str] = None) -> Dict[str, Any]:
        """Build sophisticated Elasticsearch query with HYBRID SEARCH"""
        
        # Choose embedding field based on primary focus
        embedding_field = 'combined_embedding'
        if query_components['primary_focus'] == 'location':
            embedding_field = 'location_embedding'
        elif query_components['primary_focus'] == 'service':
            embedding_field = 'service_embedding'
        
        # 🚀 HYBRID SEARCH: Combine semantic + exact text search
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        # 🎯 Exact text search (high boost for brand names)
                        {
                            "multi_match": {
                                "query": original_query,
                                "fields": ["voucher_name^3", "content^1"],
                                "type": "best_fields",
                                "boost": 3.0  # High boost for exact matches
                            }
                        },
                        # 🤖 Semantic search 
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": f"cosineSimilarity(params.query_vector, '{embedding_field}') + 1.0",
                                    "params": {"query_vector": query_embedding.tolist()}
                                }
                            }
                        }
                    ],
                    "filter": []
                }
            },
            "size": top_k,
            "_source": ["voucher_id", "voucher_name", "content", "location", "service_info", "price_info", "target_audience"]
        }
        
        # Add filters
        if location_filter:
            search_body["query"]["bool"]["filter"].append({
                "term": {"location.name": location_filter}
            })
        
        if service_filter:
            search_body["query"]["bool"]["filter"].append({
                "term": {"service_info.category": service_filter}
            })
        
        if price_filter:
            search_body["query"]["bool"]["filter"].append({
                "term": {"price_info.price_range": price_filter}
            })
        
        return search_body
```

### 3. Smart Query Parser (smart_query_parser.py)
```python
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class QueryIntent(Enum):
    """Main query intents"""
    FIND_RESTAURANT = "find_restaurant"
    FIND_HOTEL = "find_hotel" 
    FIND_ENTERTAINMENT = "find_entertainment"
    FIND_SHOPPING = "find_shopping"
    FIND_BEAUTY = "find_beauty"
    FIND_TRAVEL = "find_travel"
    FIND_KIDS = "find_kids"
    GENERAL_SEARCH = "general_search"

@dataclass 
class QueryComponents:
    """Components extracted from query"""
    original_query: str
    intent: QueryIntent
    location: Optional[str] = None
    location_type: Optional[str] = None
    service_requirements: List[str] = None
    target_audience: Optional[str] = None
    price_preference: Optional[str] = None
    time_requirements: List[str] = None
    keywords: List[str] = None
    modifiers: List[str] = None
    confidence: float = 0.0

class SmartQueryParser:
    """
    Advanced Query Parser for Vietnamese natural language
    Understands user intent and extracts query components
    """
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.location_patterns = self._load_location_patterns()
        self.service_patterns = self._load_service_patterns()
        self.target_patterns = self._load_target_patterns()
        
        logger.info("🧠 Smart Query Parser initialized")
    
    def parse_query(self, query: str) -> QueryComponents:
        """
        Main parsing function - extracts all components from query
        """
        logger.info(f"🔍 Parsed query: {query}")
        
        # Normalize query
        normalized_query = self._normalize_query(query)
        
        # Detect intent
        intent, intent_confidence = self._detect_intent(normalized_query)
        
        # Extract components
        location = self._extract_location(normalized_query)
        service_requirements = self._extract_service_requirements(normalized_query)
        target_audience = self._extract_target_audience(normalized_query)
        keywords = self._extract_keywords(normalized_query)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(intent_confidence, location, keywords)
        
        logger.info(f"   Intent: {intent.value} (confidence: {confidence:.2f})")
        if location:
            logger.info(f"   Location: {location}")
        logger.info(f"   Requirements: {service_requirements}")
        
        return QueryComponents(
            original_query=query,
            intent=intent,
            location=location,
            service_requirements=service_requirements or [],
            target_audience=target_audience,
            keywords=keywords or [],
            confidence=confidence
        )
    
    def _load_intent_patterns(self) -> Dict[QueryIntent, List[str]]:
        """Load patterns for intent detection - support both with and without diacritics"""
        return {
            QueryIntent.FIND_RESTAURANT: [
                r'(quán ăn|quan an|nhà hàng|nha hang|ăn uống|an uong|buffet|thức ăn|thuc an)',
                r'(restaurant|food|eat|dining|meal|cafe)',
                r'(bellissimo|silk path|sheraton|renaissance|capella|mercure|daewoo)'  # Brand names
            ],
            QueryIntent.FIND_HOTEL: [
                r'(khách sạn|khach san|resort|homestay|villa|nơi ở|noi o)',
                r'(hotel|accommodation|stay|lodge)'
            ],
            QueryIntent.FIND_KIDS: [
                r'(trẻ em|tre em|trẻ con|tre con|bé yêu|be yeu|em bé|em be|children|kids)',
                r'(đồ chơi|do choi|playground|khu vui chơi|khu vui choi)',
                r'(family.*trẻ|family.*tre|gia đình.*trẻ|gia dinh.*tre)'
            ]
        }
    
    def _detect_intent(self, query: str) -> tuple[QueryIntent, float]:
        """Detect primary intent from query"""
        query_lower = query.lower()
        best_intent = QueryIntent.GENERAL_SEARCH
        best_confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            intent_score = 0.0
            
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    intent_score += 0.3  # Base score for pattern match
                    
                    # Boost for exact matches
                    if pattern in query_lower:
                        intent_score += 0.2
            
            if intent_score > best_confidence:
                best_confidence = intent_score
                best_intent = intent
        
        return best_intent, min(best_confidence, 1.0)
```

### 4. Location-Aware Indexer (location_aware_indexer.py)
```python
from typing import List, Dict, Any, Optional, Tuple
import math

class LocationAwareIndexer:
    """
    Advanced geographic indexing and ranking system
    Optimized for Vietnamese locations and   ecosystem
    """
    
    def __init__(self):
        self.location_coordinates = self._load_location_coordinates()
        self.location_metadata = self._load_location_metadata()
        logger.info("🗺️ Location-Aware Indexer initialized")
    
    def apply_geographic_ranking(self, results: List[Dict], query_location: str) -> List[Dict]:
        """
        Apply advanced geographic ranking to search results
        """
        if not query_location or not results:
            return results
        
        # Get query location info
        query_coords = self.location_coordinates.get(query_location)
        query_meta = self.location_metadata.get(query_location, {})
        
        if not query_coords:
            return results
        
        # Calculate geographic relevance for each result
        for result in results:
            result_location = result.get('location', {}).get('name', 'Unknown')
            
            if result_location == query_location:
                # Exact location match
                result['geographic_score'] = 1.0
                result['ranking_factor'] = 'exact_location_match'
            else:
                # Calculate distance-based score
                result_coords = self.location_coordinates.get(result_location)
                if result_coords:
                    distance = self._calculate_distance(query_coords, result_coords)
                    result['geographic_score'] = self._distance_to_score(distance)
                else:
                    result['geographic_score'] = 0.1
        
        # Re-rank results considering geographic relevance
        def combined_score(result):
            similarity = result.get('similarity_score', 0)
            geographic = result.get('geographic_score', 0)
            
            # Weighted combination
            return similarity * 0.7 + geographic * 0.3
        
        results.sort(key=combined_score, reverse=True)
        return results
    
    def _calculate_distance(self, coords1: Tuple[float, float], 
                          coords2: Tuple[float, float]) -> float:
        """Calculate Haversine distance between two coordinates"""
        lat1, lon1 = math.radians(coords1[0]), math.radians(coords1[1])
        lat2, lon2 = math.radians(coords2[0]), math.radians(coords2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in kilometers
        return 6371 * c
```

## 🚀 Development Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ELASTICSEARCH_URL=http://localhost:9200
export EMBEDDING_MODEL=dangvantuan/vietnamese-embedding
export LOG_LEVEL=INFO
```

### 2. Database Setup
```bash
# Start Elasticsearch with Docker
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  elasticsearch:8.0.0

# Verify Elasticsearch is running
curl http://localhost:9200/_cluster/health
```

### 3. Data Indexing
```bash
# Index voucher data from Excel files
python voucher_assistant/backend/data_processing/main_indexer.py

# Verify indexing
curl "http://localhost:9200/oneu_vouchers_advanced/_count"
```

### 4. Run Development Server
```bash
# Start FastAPI development server
uvicorn voucher_assistant.backend.advanced_main:app --reload --port 8001

# Or run directly
python voucher_assistant/backend/advanced_main.py
```

## 🏗️ Architecture Patterns

### 1. Dependency Injection
```python
from fastapi import Depends
from typing import Annotated

async def get_vector_store() -> AdvancedVectorStore:
    """Dependency provider for vector store"""
    return vector_store

async def get_query_parser() -> SmartQueryParser:
    """Dependency provider for query parser"""
    return query_parser

@app.post("/api/search")
async def search(
    request: SearchRequest,
    vs: Annotated[AdvancedVectorStore, Depends(get_vector_store)],
    parser: Annotated[SmartQueryParser, Depends(get_query_parser)]
):
    """Search endpoint with dependency injection"""
    parsed_query = parser.parse_query(request.query)
    results = await vs.advanced_vector_search(request.query)
    return results
```

### 2. Error Handling
```python
from fastapi import HTTPException
from typing import Any, Dict

class VoucherAssistantException(Exception):
    """Base exception for voucher assistant"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class SearchException(VoucherAssistantException):
    """Exception for search operations"""
    pass

class IndexingException(VoucherAssistantException):
    """Exception for indexing operations"""
    pass

@app.exception_handler(VoucherAssistantException)
async def voucher_exception_handler(request, exc: VoucherAssistantException):
    """Global exception handler"""
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.error_code or "VOUCHER_ERROR",
                "message": exc.message,
                "details": exc.details,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
```

### 3. Async Processing
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

class AsyncEmbeddingService:
    """Async embedding service for better performance"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.model = SentenceTransformer("dangvantuan/vietnamese-embedding")
    
    async def encode_async(self, texts: List[str]) -> List[np.ndarray]:
        """Async encoding for multiple texts"""
        loop = asyncio.get_event_loop()
        
        # Run embedding in thread pool
        embeddings = await loop.run_in_executor(
            self.executor, 
            self.model.encode, 
            texts
        )
        
        return embeddings
    
    async def batch_encode(self, text_batches: List[List[str]]) -> List[List[np.ndarray]]:
        """Batch encoding with async processing"""
        tasks = [self.encode_async(batch) for batch in text_batches]
        return await asyncio.gather(*tasks)
```

### 4. Caching Strategy
```python
from functools import lru_cache
import redis
import json
import hashlib

class SearchCache:
    """Redis-based search result caching"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.ttl = 3600  # 1 hour cache
    
    def _generate_cache_key(self, query: str, filters: Dict) -> str:
        """Generate cache key from query and filters"""
        cache_data = {"query": query, "filters": filters}
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"search:{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    async def get_cached_results(self, query: str, filters: Dict) -> Optional[List]:
        """Get cached search results"""
        cache_key = self._generate_cache_key(query, filters)
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        
        return None
    
    async def cache_results(self, query: str, filters: Dict, results: List):
        """Cache search results"""
        cache_key = self._generate_cache_key(query, filters)
        
        try:
            self.redis_client.setex(
                cache_key, 
                self.ttl, 
                json.dumps(results, ensure_ascii=False)
            )
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

# Usage in search endpoint
@app.post("/api/search")
async def cached_search(request: SearchRequest):
    cache = SearchCache()
    
    # Try cache first
    cached_results = await cache.get_cached_results(
        request.query, 
        request.filters
    )
    
    if cached_results:
        return cached_results
    
    # Perform search
    results = await vector_store.advanced_vector_search(request.query)
    
    # Cache results
    await cache.cache_results(request.query, request.filters, results)
    
    return results
```

## 🧪 Testing Guide

### 1. Unit Tests
```python
import pytest
from unittest.mock import Mock, patch
import numpy as np

class TestSmartQueryParser:
    def setup_method(self):
        self.parser = SmartQueryParser()
    
    def test_intent_detection_restaurant(self):
        """Test restaurant intent detection"""
        query = "tìm nhà hàng buffet"
        result = self.parser.parse_query(query)
        
        assert result.intent == QueryIntent.FIND_RESTAURANT
        assert result.confidence > 0.3
    
    def test_location_extraction(self):
        """Test location extraction"""
        query = "buffet ở Hà Nội"
        result = self.parser.parse_query(query)
        
        assert result.location == "Hà Nội"
        assert result.intent == QueryIntent.FIND_RESTAURANT
    
    def test_brand_name_recognition(self):
        """Test brand name recognition"""
        query = "Bellissimo Restaurant"
        result = self.parser.parse_query(query)
        
        assert result.intent == QueryIntent.FIND_RESTAURANT
        assert "bellissimo" in [k.lower() for k in result.keywords]

class TestAdvancedVectorStore:
    @pytest.fixture
    def mock_elasticsearch(self):
        with patch('elasticsearch.Elasticsearch') as mock_es:
            yield mock_es
    
    def test_hybrid_search_query_building(self, mock_elasticsearch):
        """Test hybrid search query construction"""
        vector_store = AdvancedVectorStore()
        
        query_embedding = np.random.rand(768)
        query_components = {'original_query': 'test', 'primary_focus': 'content'}
        
        search_body = vector_store._build_hybrid_search_query(
            query_embedding, query_components, "test query", 10
        )
        
        # Verify hybrid search structure
        assert "bool" in search_body["query"]
        assert "should" in search_body["query"]["bool"]
        assert len(search_body["query"]["bool"]["should"]) == 2
        
        # Check exact text search
        multi_match = search_body["query"]["bool"]["should"][0]
        assert "multi_match" in multi_match
        assert multi_match["multi_match"]["boost"] == 3.0
        
        # Check semantic search
        script_score = search_body["query"]["bool"]["should"][1]
        assert "script_score" in script_score
```

### 2. Integration Tests
```python
import asyncio
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestSearchAPI:
    async def test_advanced_search_endpoint(self):
        """Test the advanced search API endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/advanced-search", json={
                "query": "buffet hà nội",
                "top_k": 5
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "query" in data
        assert "results" in data
        assert "metadata" in data
        assert len(data["results"]) <= 5
    
    async def test_health_check(self):
        """Test health check endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
```

### 3. Performance Tests
```python
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_search_performance():
    """Test search performance under load"""
    def single_search():
        start_time = time.time()
        # Perform search
        response = requests.post("http://localhost:8001/api/advanced-search", 
                               json={"query": "buffet hà nội", "top_k": 10})
        end_time = time.time()
        
        assert response.status_code == 200
        return end_time - start_time
    
    # Run concurrent searches
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(single_search) for _ in range(100)]
        response_times = [future.result() for future in as_completed(futures)]
    
    # Verify performance metrics
    avg_time = statistics.mean(response_times)
    p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
    
    assert avg_time < 0.5  # Average < 500ms
    assert p95_time < 1.0  # 95th percentile < 1s
    
    print(f"Average response time: {avg_time:.3f}s")
    print(f"95th percentile: {p95_time:.3f}s")
```

## ⚡ Performance Optimization

### 1. Database Optimization
```python
# Elasticsearch index settings for performance
ELASTICSEARCH_SETTINGS = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 1,
        "refresh_interval": "30s",
        "index": {
            "max_result_window": 50000,
            "mapping": {
                "total_fields": {"limit": 2000}
            }
        }
    }
}

# Connection pooling
from elasticsearch import Elasticsearch
from urllib3 import Retry

es_client = Elasticsearch(
    [{"host": "localhost", "port": 9200}],
    retry_on_timeout=True,
    retry_on_status=[502, 503, 504],
    max_retries=Retry(total=3, backoff_factor=1)
)
```

### 2. Memory Optimization
```python
import gc
from memory_profiler import profile

class OptimizedEmbeddingService:
    """Memory-optimized embedding service"""
    
    def __init__(self):
        self.model = SentenceTransformer("dangvantuan/vietnamese-embedding")
        self._embedding_cache = {}
        self._cache_size_limit = 1000
    
    @profile
    def encode_with_cache(self, text: str) -> np.ndarray:
        """Encode with memory-efficient caching"""
        text_hash = hash(text)
        
        if text_hash in self._embedding_cache:
            return self._embedding_cache[text_hash]
        
        # Clean cache if too large
        if len(self._embedding_cache) >= self._cache_size_limit:
            # Remove oldest entries
            oldest_keys = list(self._embedding_cache.keys())[:100]
            for key in oldest_keys:
                del self._embedding_cache[key]
            gc.collect()
        
        # Generate embedding
        embedding = self.model.encode(text)
        self._embedding_cache[text_hash] = embedding
        
        return embedding
```

### 3. Async Optimization
```python
import asyncio
from asyncio import Semaphore

class AsyncSearchService:
    """Async search service with concurrency control"""
    
    def __init__(self, max_concurrent_searches: int = 10):
        self.semaphore = Semaphore(max_concurrent_searches)
        self.vector_store = AdvancedVectorStore()
    
    async def search_with_throttling(self, query: str) -> List[Dict]:
        """Search with concurrency throttling"""
        async with self.semaphore:
            return await self.vector_store.advanced_vector_search(query)
    
    async def batch_search(self, queries: List[str]) -> List[List[Dict]]:
        """Batch search with optimal concurrency"""
        tasks = [self.search_with_throttling(query) for query in queries]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

---

**Next**: [🎨 Frontend Guide](./FRONTEND.md)
