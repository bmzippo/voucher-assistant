"""
  AI Voucher Assistant - Vector Store Implementation
Tối ưu cho xử lý tiếng Việt và RAG theo yêu cầu giai đoạn 1
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import json

# Import với error handling
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"SentenceTransformers not available: {e}")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Elasticsearch not available: {e}")
    ELASTICSEARCH_AVAILABLE = False

import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """
    Vector Store implementation cho   AI Voucher Assistant
    Sử dụng Elasticsearch để lưu trữ và tìm kiếm vector embeddings
    Tối ưu cho tiếng Việt theo instruction
    """
    
    def __init__(self):
        self.es_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
        self.index_name = os.getenv('ELASTICSEARCH_INDEX', 'voucher_knowledge')
        self.embedding_model_name = os.getenv('EMBEDDING_MODEL', 'dangvantuan/vietnamese-embedding')  # Use Vietnamese model first
        self.embedding_dimension = int(os.getenv('EMBEDDING_DIMENSION', '768'))
        self.max_context_length = int(os.getenv('MAX_CONTEXT_LENGTH', '4000'))
        self.top_k = int(os.getenv('TOP_K_RESULTS', '5'))
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', '0.7'))
        
        self.es = None
        self.model = None
        self.is_ready = False
        
        # Initialize components
        self._initialize_elasticsearch()
        self._initialize_embedding_model()
    
    def _initialize_elasticsearch(self):
        """Khởi tạo kết nối Elasticsearch"""
        if not ELASTICSEARCH_AVAILABLE:
            logger.error("❌ Elasticsearch không khả dụng. Vui lòng cài đặt: pip install elasticsearch")
            return False
            
        try:
            self.es = Elasticsearch(
                [self.es_url],
                verify_certs=False,
                request_timeout=30,
                retry_on_timeout=True,
                max_retries=3
            )
            
            # Test connection
            if self.es.ping():
                logger.info(f"✅ Kết nối Elasticsearch thành công: {self.es_url}")
                return True
            else:
                logger.error(f"❌ Không thể ping Elasticsearch: {self.es_url}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Lỗi kết nối Elasticsearch: {e}")
            return False
    
    def _initialize_embedding_model(self):
        """Khởi tạo model embedding cho tiếng Việt"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.error("❌ SentenceTransformers không khả dụng. Đang sử dụng fallback method...")
            return self._initialize_fallback_embeddings()
            
        try:
            logger.info(f"🤖 Đang tải Vietnamese embedding model: {self.embedding_model_name}")
            self.model = SentenceTransformer(self.embedding_model_name)
            
            # Ensure correct embedding dimension for dangvantuan/vietnamese-embedding
            if "dangvantuan/vietnamese-embedding" in self.embedding_model_name:
                self.embedding_dimension = 768
                
            if "keepitreal/vietnamese-sbert" in self.embedding_model_name:
                self.embedding_dimension = 768
                
            logger.info(f"✅ Vietnamese embedding model đã sẵn sàng! Dimension: {self.embedding_dimension}")
            self.is_ready = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi tải model {self.embedding_model_name}: {e}")
            logger.info("🔄 Thử sử dụng model backup...")
            
            # Fallback to multilingual model
            try:
                backup_model = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
                self.model = SentenceTransformer(backup_model)
                self.embedding_dimension = 384  # Update dimension for backup model
                self.embedding_model_name = backup_model  # Update model name
                logger.warning(f"⚠️ Sử dụng backup model: {backup_model} (dimension: {self.embedding_dimension})")
                self.is_ready = True
                return True
            except Exception as backup_error:
                logger.error(f"❌ Backup model cũng thất bại: {backup_error}")
                return self._initialize_fallback_embeddings()
    
    def _initialize_fallback_embeddings(self):
        """Fallback embedding method using TF-IDF for Python 3.13 compatibility"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=768,
                ngram_range=(1, 2),
                stop_words=None
            )
            self.embedding_dimension = 768
            self.use_tfidf = True
            logger.warning("⚠️ Sử dụng TF-IDF embedding method")
            self.is_ready = True
            return True
        except ImportError:
            logger.error("❌ Không thể khởi tạo TF-IDF vectorizer")
            self.embedding_dimension = 300
            self.use_tfidf = False
            self.is_ready = True
            return True
    
    def _create_fallback_embedding(self, text: str) -> List[float]:
        """Tạo embedding đơn giản khi không có SentenceTransformers"""
        import hashlib
        import struct
        
        # Simple hash-based embedding (for demonstration only)
        hash_obj = hashlib.md5(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # Convert to fixed-size vector
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                val = struct.unpack('f', chunk)[0]
                embedding.append(val)
        
        # Pad or truncate to desired dimension
        while len(embedding) < self.embedding_dimension:
            embedding.append(0.0)
        
        return embedding[:self.embedding_dimension]
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Tạo embedding vector cho text
        Tối ưu cho tiếng Việt theo yêu cầu  
        """
        if not text or not text.strip():
            return [0.0] * self.embedding_dimension
            
        try:
            # Use SentenceTransformers if available
            if self.model is not None:
                embedding = self.model.encode(text, convert_to_tensor=False)
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                
                # Handle dimension mismatch - pad or truncate to match index
                if len(embedding) != self.embedding_dimension:
                    logger.warning(f"⚠️ Embedding dimension mismatch: model={len(embedding)}, index={self.embedding_dimension}")
                    if len(embedding) < self.embedding_dimension:
                        # Pad with zeros
                        embedding.extend([0.0] * (self.embedding_dimension - len(embedding)))
                        logger.info(f"🔧 Padded embedding to {self.embedding_dimension} dimensions")
                    else:
                        # Truncate
                        embedding = embedding[:self.embedding_dimension]
                        logger.info(f"🔧 Truncated embedding to {self.embedding_dimension} dimensions")
                
                return embedding
            
            # Use TF-IDF if available
            elif hasattr(self, 'use_tfidf') and self.use_tfidf and hasattr(self, 'tfidf_vectorizer'):
                try:
                    # For TF-IDF, we need to fit on some data first
                    # This is a simplified approach for demo
                    tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
                    embedding = tfidf_matrix.toarray()[0].tolist()
                    # Pad or truncate to match expected dimension
                    while len(embedding) < self.embedding_dimension:
                        embedding.append(0.0)
                    return embedding[:self.embedding_dimension]
                except Exception as e:
                    logger.error(f"TF-IDF embedding error: {e}")
                    return self._create_fallback_embedding(text)
            
            # Fallback to simple hash embedding
            else:
                return self._create_fallback_embedding(text)
                
        except Exception as e:
            logger.error(f"❌ Lỗi tạo embedding: {e}")
            return self._create_fallback_embedding(text)
    
    def extract_location_from_query(self, query: str) -> Optional[str]:
        """
        Extract location from user query using pattern matching
        Tích hợp   location intelligence
        """
        import re
        
        # Common Vietnamese location patterns
        location_patterns = [
            r'tại\s+([A-Za-zÀ-ỹ\s]+?)(?:\s|$)',  # "tại Hải Phòng"
            r'ở\s+([A-Za-zÀ-ỹ\s]+?)(?:\s|$)',   # "ở Hà Nội"
            r'([A-Za-zÀ-ỹ\s]*(?:Hải Phòng|Hà Nội|Hồ Chí Minh|Đà Nẵng|HCM|Sài Gòn)[A-Za-zÀ-ỹ\s]*)',  # Direct mention
        ]
        
        # Known cities/locations in   ecosystem
        known_locations = [
            'Hải Phòng', 'Hà Nội', 'Hồ Chí Minh', 'Đà Nẵng', 'HCM', 'Sài Gòn',
            'Cần Thơ', 'Nha Trang', 'Vũng Tàu', 'Huế', 'Đà Lạt'
        ]
        
        query_lower = query.lower()
        
        # Check for exact location matches first
        for location in known_locations:
            if location.lower() in query_lower:
                # Normalize location names
                if location in ['HCM', 'Sài Gòn']:
                    return 'Hồ Chí Minh'
                return location
        
        # Try pattern matching
        for pattern in location_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                location = matches[0].strip()
                # Normalize location names
                if 'hải phòng' in location.lower():
                    return 'Hải Phòng'
                elif 'hà nội' in location.lower():
                    return 'Hà Nội'
                elif any(x in location.lower() for x in ['hồ chí minh', 'hcm', 'sài gòn']):
                    return 'Hồ Chí Minh'
                elif 'đà nẵng' in location.lower():
                    return 'Đà Nẵng'
        
        return None

    async def vector_search(self, query: str, top_k: Optional[int] = None, min_score: Optional[float] = None, location_boost: bool = True) -> List[Dict[str, Any]]:
        """
        Vector Search API - Tìm kiếm bằng vector similarity với location boosting
        Tối ưu cho   AI Voucher Assistant
        """
        if not self.is_ready or not self.es:
            logger.error("❌ Vector Store chưa sẵn sàng")
            return []
        
        top_k = top_k or self.top_k
        min_score = min_score or self.confidence_threshold
        
        # Extract location for intelligent boosting
        extracted_location = None
        if location_boost:
            extracted_location = self.extract_location_from_query(query)
            if extracted_location:
                logger.info(f"🎯 Detected location in query: {extracted_location}")
        
        try:
            # 1. Tạo embedding vector từ search text
            logger.info(f"🔍 Vector search cho query: '{query}'")
            query_embedding = self.create_embedding(query)
            
            if not query_embedding or len(query_embedding) != self.embedding_dimension:
                logger.error(f"❌ Lỗi tạo embedding, dimension: {len(query_embedding) if query_embedding else 0}")
                return []
            
            # 2. Elasticsearch vector similarity search with increased size for boosting
            search_body = {
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'content_embedding') + 1.0",
                            "params": {"query_vector": query_embedding}
                        }
                    }
                },
                "size": top_k * 2 if location_boost else top_k,  # Get more results for potential boosting
                "_source": ["voucher_id", "voucher_name", "content", "metadata", "created_at"]
            }
            
            # 3. Thực hiện search
            response = await self._execute_search(search_body)
            
            # 4. Xử lý và format kết quả với location boosting
            results = []
            for hit in response.get('hits', {}).get('hits', []):
                # ES cosine similarity score (đã được +1.0 trong query)
                raw_score = hit['_score']
                normalized_score = raw_score / 2.0  # Chuyển từ [0,2] về [0,1] cho cosine similarity
                
                # Apply location boosting if detected
                if extracted_location and location_boost:
                    metadata = hit['_source'].get('metadata', {})
                    voucher_location = metadata.get('location', '')
                    
                    # Location metadata boost (highest priority)
                    if voucher_location == extracted_location:
                        normalized_score *= 1.6  # 60% boost for exact location match
                        logger.info(f"🚀 Location boost: {hit['_source'].get('voucher_name', '')[:50]}... (metadata: {voucher_location})")
                    
                    # Content location boost (secondary)
                    voucher_text = f"{hit['_source'].get('voucher_name', '')} {hit['_source'].get('content', '')}".lower()
                    if extracted_location.lower() in voucher_text:
                        normalized_score *= 1.3  # 30% boost for location in content
                        logger.info(f"🎯 Content location boost: {hit['_source'].get('voucher_name', '')[:50]}...")
                
                # Ghi log để debug
                logger.debug(f"Vector search hit: {hit['_source'].get('voucher_name', '')[:50]}... | raw_score: {raw_score:.4f} | final: {normalized_score:.4f}")
                
                # Chỉ lấy kết quả có độ tương đồng cao - sử dụng min_score thấp hơn cho tiếng Việt
                effective_min_score = min(min_score, 0.4)  # Score range 0-1, min_score reasonable
                if normalized_score >= effective_min_score:
                    result_item = {
                        'voucher_id': hit['_source'].get('voucher_id'),
                        'voucher_name': hit['_source'].get('voucher_name'),
                        'content': hit['_source'].get('content'),
                        'similarity_score': round(normalized_score, 4),
                        'raw_score': round(raw_score, 4),
                        'metadata': hit['_source'].get('metadata', {}),
                        'created_at': hit['_source'].get('created_at'),
                        'search_query': query,
                        'location_boost_applied': extracted_location is not None and location_boost
                    }
                    results.append(result_item)
            
            # Sort by boosted similarity score and return top_k
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            final_results = results[:top_k]
            
            logger.info(f"✅ Vector search hoàn thành: {len(final_results)}/{response.get('hits', {}).get('total', {}).get('value', 0)} kết quả phù hợp")
            if extracted_location:
                location_count = sum(1 for r in final_results if r['metadata'].get('location') == extracted_location)
                logger.info(f"🎯 Kết quả tại {extracted_location}: {location_count}/{len(final_results)}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Lỗi vector search: {e}")
            return []
    
    async def hybrid_search(self, query: str, top_k: Optional[int] = None, min_score: Optional[float] = None, location_boost: bool = True) -> Dict[str, Any]:
        """
        Hybrid Search - Kết hợp text search và vector search với location intelligence
        Để có kết quả tốt nhất cho  
        """
        try:
            top_k = top_k or self.top_k
            min_score = min_score or 0.3  # Default min_score for hybrid search
            
            # Extract location for both searches
            extracted_location = None
            if location_boost:
                extracted_location = self.extract_location_from_query(query)
                if extracted_location:
                    logger.info(f"🎯 Hybrid search with location: {extracted_location}")
            
            # Text search with location awareness
            text_search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["voucher_name^2", "content"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                },
                "size": top_k,
                "_source": ["voucher_id", "voucher_name", "content", "metadata"]
            }
            
            # Vector search results with location boosting
            vector_results = await self.vector_search(query, top_k, min_score, location_boost)
            
            # Text search results
            text_response = await self._execute_search(text_search_body)
            text_results = []
            for hit in text_response.get('hits', {}).get('hits', []):
                text_results.append({
                    'voucher_id': hit['_source'].get('voucher_id'),
                    'voucher_name': hit['_source'].get('voucher_name'),
                    'content': hit['_source'].get('content'),
                    'text_score': round(hit['_score'], 4),
                    'metadata': hit['_source'].get('metadata', {})
                })
            
            return {
                'query': query,
                'vector_results': vector_results,
                'text_results': text_results,
                'total_vector_results': len(vector_results),
                'total_text_results': len(text_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi hybrid search: {e}")
            return {
                'query': query,
                'vector_results': [],
                'text_results': [],
                'total_vector_results': 0,
                'total_text_results': 0
            }

    async def search_similar(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Tìm kiếm ngữ nghĩa trong Knowledge Base
        Triển khai RAG logic theo yêu cầu giai đoạn 1.2
        """
        if not self.is_ready or not self.es:
            logger.error("❌ Vector Store chưa sẵn sàng")
            return []
        
        top_k = top_k or self.top_k
        
        try:
            # Tạo embedding cho query
            query_embedding = self.create_embedding(query)
            
            # Elasticsearch vector search query
            search_body = {
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'content_embedding') + 1.0",
                            "params": {"query_vector": query_embedding}
                        }
                    }
                },
                "size": top_k,
                "_source": ["voucher_id", "voucher_name", "content", "metadata"]
            }
            
            # Thực hiện search
            response = await self._execute_search(search_body)
            
            # Xử lý kết quả
            results = []
            for hit in response.get('hits', {}).get('hits', []):
                score = hit['_score'] - 1.0  # Normalize score
                
                # Chỉ lấy kết quả có confidence score đủ cao
                if score >= self.confidence_threshold:
                    results.append({
                        'voucher_id': hit['_source'].get('voucher_id'),
                        'voucher_name': hit['_source'].get('voucher_name'),
                        'content': hit['_source'].get('content'),
                        'score': score,
                        'metadata': hit['_source'].get('metadata', {})
                    })
            
            logger.info(f"🔍 Tìm thấy {len(results)} kết quả phù hợp cho query: '{query[:50]}...'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Lỗi search: {e}")
            return []
    
    async def _execute_search(self, search_body: Dict[str, Any]) -> Dict[str, Any]:
        """Thực hiện search query với error handling"""
        try:
            # Log chi tiết query gửi xuống ES
            logger.info(f"📤 ES Query Body:")
            logger.info(f"Index: {self.index_name}")
            logger.info(f"Query: {json.dumps(search_body, indent=2, ensure_ascii=False)}")
            
            if hasattr(self.es, 'search'):
                response = self.es.search(index=self.index_name, body=search_body)
                logger.info(f"✅ ES Response: {response.get('hits', {}).get('total', 'unknown')} hits found")
                return response
            else:
                logger.error("❌ Elasticsearch client không hỗ trợ search method")
                return {'hits': {'hits': []}}
                
        except Exception as e:
            logger.error(f"❌ Elasticsearch search error: {e}")
            logger.error(f"❌ Failed query body: {json.dumps(search_body, indent=2, ensure_ascii=False)}")
            return {'hits': {'hits': []}}
    
    def get_context_for_llm(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Tạo context từ search results để gửi cho LLM
        Theo yêu cầu RAG trong giai đoạn 1.2
        """
        if not search_results:
            return "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu voucher."
        
        context_parts = []
        current_length = 0
        
        for result in search_results:
            voucher_name = result.get('voucher_name', 'Unknown Voucher')
            content = result.get('content', '')
            score = result.get('score', 0)
            
            # Format context với thông tin voucher
            part = f"[Voucher: {voucher_name}] (Độ liên quan: {score:.2f})\n{content}\n---\n"
            
            # Kiểm tra độ dài context
            if current_length + len(part) > self.max_context_length:
                break
                
            context_parts.append(part)
            current_length += len(part)
        
        context = "\n".join(context_parts)
        
        # Thêm instruction cho LLM
        instruction = (
            "Dựa trên thông tin voucher được cung cấp bên dưới, hãy trả lời câu hỏi của người dùng "
            "một cách chính xác và hữu ích. Chỉ sử dụng thông tin có trong dữ liệu được cung cấp.\n\n"
            "THÔNG TIN VOUCHER:\n"
        )
        
        return instruction + context
    
    async def health_check(self) -> Dict[str, Any]:
        """Kiểm tra trạng thái của Vector Store"""
        health_status = {
            "vector_store_ready": self.is_ready,
            "elasticsearch_connected": False,
            "embedding_model_loaded": self.model is not None,
            "index_exists": False,
            "document_count": 0
        }
        
        try:
            if self.es and self.es.ping():
                health_status["elasticsearch_connected"] = True
                
                # Kiểm tra index tồn tại
                if self.es.indices.exists(index=self.index_name):
                    health_status["index_exists"] = True
                    
                    # Đếm documents
                    count_response = self.es.count(index=self.index_name)
                    health_status["document_count"] = count_response.get('count', 0)
                    
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
        
        return health_status
    
    async def create_index(self):
        """Tạo Elasticsearch index cho vector search"""
        if not self.es:
            logger.warning("❌ Elasticsearch không khả dụng - bỏ qua việc tạo index")
            return False
            
        try:
            # Check if index exists
            if self.es.indices.exists(index=self.index_name):
                logger.info(f"✅ Index {self.index_name} đã tồn tại")
                return True
                
            # Create index with mapping
            mapping = {
                "mappings": {
                    "properties": {
                        "voucher_id": {"type": "keyword"},
                        "voucher_name": {"type": "text", "analyzer": "standard"},
                        "content": {"type": "text", "analyzer": "standard"},
                        "content_embedding": {
                            "type": "dense_vector",
                            "dims": self.embedding_dimension
                        },
                        "metadata": {"type": "object"},
                        "created_at": {"type": "date"},
                        "search_query": {"type": "text"}
                    }
                }
            }
            
            self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"✅ Đã tạo index {self.index_name} thành công")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi tạo index: {e}")
            return False

# Global instance
vector_store = VectorStore()