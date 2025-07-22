"""
Advanced Vector Store với Multi-field Embedding Strategy + RAG Integration
Phần của   AI Voucher Assistant - Phase 2
"""

import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
import json
import re
import os
from dataclasses import dataclass
from voucher_content_generator import VoucherContentGenerator
# import openai  # Will be enabled when integrated with actual LLM service
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class RAGResponse:
    """Response từ RAG pipeline"""
    answer: str
    retrieved_vouchers: List[Dict[str, Any]]
    confidence_score: float
    search_method: str
    processing_time: float
    query_intent: Dict[str, Any]

@dataclass
class EmbeddingWeights:
    """Trọng số cho các field embeddings"""
    content: float = 0.4
    location: float = 0.3
    service_type: float = 0.15
    target_audience: float = 0.1
    keywords: float = 0.05

@dataclass
class VoucherComponents:
    """Các component được extract từ voucher"""
    content: str
    location: str
    service_type: str
    target_audience: str
    keywords: List[str]
    price_range: str

class AdvancedVectorStore:
    """
    Advanced Vector Store với multi-field embedding strategy
    Tối ưu hóa cho   ecosystem
    """
    
    def __init__(self, es_url: str = "http://localhost:9200", 
                 embedding_model: str = os.getenv("EMBEDDING_MODEL","dangvantuan/vietnamese-embedding"),
                 index_name: str = os.getenv('ELASTICSEARCH_INDEX', 'voucher_knowledge')):
        self.es_url = es_url
        self.es = Elasticsearch([es_url])
        self.index_name = index_name
        self.embedding_model_name = embedding_model
        self.embedding_dimension = 768
        self.content_generator = VoucherContentGenerator()
        self.weights = EmbeddingWeights()
        
        # LLM Configuration
        self.llm_model = os.getenv('LLM_MODEL', 'gpt-4o-mini')  # Fallback to OpenAI
        self.llm_api_key = os.getenv('OPENAI_API_KEY')
        self.max_context_tokens = int(os.getenv('MAX_CONTEXT_TOKENS', '4000'))
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.3'))
        
        # Initialize embedding model
        self.model = SentenceTransformer(embedding_model)        
        logger.info(f"🤖 Advanced Vector Store initialized with model: {embedding_model}")
        logger.info(f"🧠 LLM configured: {self.llm_model}")
        
        # Create advanced index mapping
        self._create_advanced_index()
    
    def _create_advanced_index(self):
        """Tạo Elasticsearch index với advanced mapping"""
        mapping = {
            "mappings": {
                "properties": {
                    "voucher_id": {"type": "keyword"},
                    "voucher_name": {
                        "type": "text", 
                        "analyzer": "vietnamese",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "content": {
                        "type": "text", 
                        "analyzer": "vietnamese"
                    },
                    
                    # Multi-field embeddings
                    "content_embedding": {
                        "type": "dense_vector",
                        "dims": self.embedding_dimension
                    },
                    "location_embedding": {
                        "type": "dense_vector", 
                        "dims": self.embedding_dimension
                    },
                    "service_embedding": {
                        "type": "dense_vector",
                        "dims": self.embedding_dimension
                    },
                    "target_embedding": {
                        "type": "dense_vector",
                        "dims": self.embedding_dimension
                    },
                    "combined_embedding": {
                        "type": "dense_vector",
                        "dims": self.embedding_dimension
                    },
                    
                    # Structured metadata
                    "location": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "keyword"},
                            "coordinates": {"type": "geo_point"},
                            "region": {"type": "keyword"},
                            "district": {"type": "keyword"}
                        }
                    },
                    
                    "service_info": {
                        "type": "object", 
                        "properties": {
                            "category": {"type": "keyword"},
                            "subcategory": {"type": "keyword"},
                            "tags": {"type": "keyword"},
                            "has_kids_area": {"type": "boolean"},
                            "restaurant_type": {"type": "keyword"}
                        }
                    },
                    
                    "price_info": {
                        "type": "object",
                        "properties": {
                            "original_price": {"type": "long"},
                            "discounted_price": {"type": "long"},
                            "price_range": {"type": "keyword"},
                            "currency": {"type": "keyword"}
                        }
                    },
                    
                    "target_audience": {"type": "keyword"},
                    "keywords": {"type": "keyword"},
                            
                    # Additional fields for voucher details
                    "usage_instructions": {
                        "type": "text",
                        "analyzer": "vietnamese"
                    },
                    "terms_conditions": {
                        "type": "text", 
                        "analyzer": "vietnamese"
                    },
                    "merchant": {"type": "keyword"},
                    "validity_period": {"type": "keyword"},
                    
                    # Metadata
                    "metadata": {"type": "object"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "vietnamese": {
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop"]
                        }
                    }
                },
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        
        # Create index if not exists
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"✅ Created advanced index: {self.index_name}")
    
    def extract_voucher_components(self, voucher_data: Dict[str, Any]) -> VoucherComponents:
        """
        Extract và classify các components từ voucher data
        Sử dụng rule-based + pattern matching cho tiếng Việt
        """
        # Generate content using VoucherContentGenerator if not present or needs update
        if 'content' not in voucher_data or not voucher_data['content'].strip():
            voucher_data = self.content_generator.update_voucher_with_generated_content(voucher_data)
        
        content = voucher_data.get('content', '')
        voucher_name = voucher_data.get('voucher_name', '')
        
        # Extract location
        location = self._extract_location_component(content, voucher_name)
        
        # Extract service type
        service_type = self._extract_service_type(content, voucher_name)
        
        # Extract target audience
        target_audience = self._extract_target_audience(content, voucher_name)
        
        # Extract keywords
        keywords = self._extract_keywords(content, voucher_name)
        
        # Extract price range
        price_range = self._extract_price_range(voucher_data)
        
        return VoucherComponents(
            content=content,
            location=location,
            service_type=service_type,
            target_audience=target_audience,
            keywords=keywords,
            price_range=price_range
        )
    
    def _extract_location_component(self, content: str, voucher_name: str) -> str:
        """Extract location information"""
        text = f"{voucher_name} {content}".lower()
        
        # Vietnamese location patterns
        location_patterns = [
            r'(hải phòng|hai phong)',
            r'(hà nội|ha noi|hanoi)',
            r'(hồ chí minh|ho chi minh|hcm|sài gòn|saigon)',
            r'(đà nẵng|da nang|danang)',
            r'(cần thơ|can tho)',
            r'(nha trang)',
            r'(vũng tàu|vung tau)',
            r'(huế|hue)',
            r'(đà lạt|da lat)'
        ]
        
        for pattern in location_patterns:
            if re.search(pattern, text):
                match = re.search(pattern, text).group(1)
                # Normalize location names
                if 'hải phòng' in match or 'hai phong' in match:
                    return 'Hải Phòng'
                elif 'hà nội' in match or 'ha noi' in match or 'hanoi' in match:
                    return 'Hà Nội'
                elif any(x in match for x in ['hồ chí minh', 'ho chi minh', 'hcm', 'sài gòn', 'saigon']):
                    return 'Hồ Chí Minh'
                elif 'đà nẵng' in match or 'da nang' in match or 'danang' in match:
                    return 'Đà Nẵng'
                # Add more normalizations as needed
        
        return 'Unknown'
    
    def _extract_service_type(self, content: str, voucher_name: str) -> str:
        """Extract service category"""
        text = f"{voucher_name} {content}".lower()
        
        service_patterns = {
            'Restaurant': [r'buffet', r'nhà hàng', r'ăn uống', r'quán ăn', r'thực đơn', r'menu'],
            'Hotel': [r'khách sạn', r'resort', r'homestay', r'villa'],
            'Entertainment': [r'giải trí', r'vui chơi', r'trò chơi', r'game'],
            'Shopping': [r'mua sắm', r'siêu thị', r'cửa hàng', r'shop'],
            'Beauty': [r'làm đẹp', r'spa', r'massage', r'salon'],
            'Travel': [r'du lịch', r'tour', r'vé máy bay', r'khách sạn'],
            'Kids': [r'trẻ em', r'đồ chơi', r'kingdom', r'playground']
        }
        
        for category, patterns in service_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return category
        
        return 'General'
    
    def _extract_target_audience(self, content: str, voucher_name: str) -> str:
        """Extract target audience"""
        text = f"{voucher_name} {content}".lower()
        
        audience_patterns = {
            'Family': [r'gia đình', r'trẻ em', r'family', r'kids', r'children'],
            'Couple': [r'cặp đôi', r'couple', r'romantic', r'lãng mạn'],
            'Business': [r'công ty', r'doanh nghiệp', r'business', r'meeting'],
            'Solo': [r'cá nhân', r'individual', r'solo'],
            'Group': [r'nhóm', r'group', r'team', r'tập thể']
        }
        
        for audience, patterns in audience_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return audience
        
        return 'General'
    
    def _extract_keywords(self, content: str, voucher_name: str) -> List[str]:
        """Extract important keywords"""
        text = f"{voucher_name} {content}".lower()
        
        # Key phrases that matter for search
        important_phrases = [
            'buffet', 'ăn uống', 'trẻ em', 'gia đình', 'cao cấp', 'sang trọng',
            'giảm giá', 'khuyến mãi', 'miễn phí', 'tặng kèm', 'combo',
            'cuối tuần', 'lễ tết', 'đặc biệt', 'premium', 'luxury'
        ]
        
        found_keywords = []
        for phrase in important_phrases:
            if phrase in text:
                found_keywords.append(phrase)
        
        return found_keywords
    
    def _extract_price_range(self, voucher_data: Dict[str, Any]) -> str:
        """Classify price range"""
        try:
            price = voucher_data.get('metadata', {}).get('price', 0)
            if isinstance(price, str):
                price = float(price.replace(',', ''))
            
            if price < 100000:
                return 'Budget'
            elif price < 500000:
                return 'Mid-range'
            elif price < 1000000:
                return 'Premium'
            else:
                return 'Luxury'
        except:
            return 'Unknown'
    
    def create_multi_field_embeddings(self, components: VoucherComponents) -> Dict[str, np.ndarray]:
        """
        Tạo embeddings riêng biệt cho từng field
        """
        embeddings = {}
        
        # Content embedding (full text)
        embeddings['content'] = self.model.encode(components.content)
        
        # Location embedding (focused on location)
        location_text = f"Địa điểm: {components.location}. Khu vực: {components.location}"
        embeddings['location'] = self.model.encode(location_text)
        
        # Service embedding (focused on service type and features)
        service_text = f"Dịch vụ: {components.service_type}. Keywords: {', '.join(components.keywords)}"
        embeddings['service'] = self.model.encode(service_text)
        
        # Target audience embedding
        target_text = f"Đối tượng: {components.target_audience}. Phù hợp cho: {components.target_audience}"
        embeddings['target'] = self.model.encode(target_text)
        
        return embeddings
    
    def combine_embeddings(self, embeddings: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Kết hợp các embeddings với trọng số
        """
        combined = (
            embeddings['content'] * self.weights.content +
            embeddings['location'] * self.weights.location +
            embeddings['service'] * self.weights.service_type +
            embeddings['target'] * self.weights.target_audience
        )
        
        # Normalize the combined embedding
        combined = combined / np.linalg.norm(combined)
        
        return combined
    
    async def index_voucher_advanced(self, voucher_data: Dict[str, Any]) -> bool:
        """
        Index voucher với advanced multi-field strategy
        """
        try:
            # Extract components
            components = self.extract_voucher_components(voucher_data)
            
            # Create multi-field embeddings
            embeddings = self.create_multi_field_embeddings(components)
            
            # Combine embeddings
            combined_embedding = self.combine_embeddings(embeddings)
            
            # Prepare document for indexing
            doc = {
                'voucher_id': voucher_data.get('voucher_id'),
                'voucher_name': voucher_data.get('voucher_name'),
                'content': components.content,
                
                # Multi-field embeddings
                'content_embedding': embeddings['content'].tolist(),
                'location_embedding': embeddings['location'].tolist(),
                'service_embedding': embeddings['service'].tolist(),
                'target_embedding': embeddings['target'].tolist(),
                'combined_embedding': combined_embedding.tolist(),
                
                # Structured metadata
                'location': {
                    'name': components.location,
                    'region': self._get_region(components.location),
                    'district': voucher_data.get('metadata', {}).get('district', '')
                },
                
                'service_info': {
                    'category': components.service_type,
                    'tags': components.keywords,
                    'has_kids_area': 'trẻ em' in components.keywords,
                    'restaurant_type': 'buffet' if 'buffet' in components.keywords else 'other'
                },
                
                'price_info': {
                    'original_price': voucher_data.get('metadata', {}).get('price', 0),
                    'price_range': components.price_range,
                    'currency': 'VND'
                },
                
                'target_audience': components.target_audience,
                'keywords': components.keywords,
                'created_at': voucher_data.get('created_at'),
                'updated_at': voucher_data.get('updated_at', voucher_data.get('created_at'))
            }
            
            # Index document
            response = self.es.index(
                index=self.index_name,
                id=voucher_data.get('voucher_id'),
                body=doc
            )
            
            logger.info(f"✅ Indexed voucher {voucher_data.get('voucher_id')} with advanced embeddings")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error indexing voucher: {e}")
            return False
    
    def _get_region(self, location: str) -> str:
        """Map location to region"""
        region_mapping = {
            'Hà Nội': 'Miền Bắc',
            'Hải Phòng': 'Miền Bắc', 
            'Đà Nẵng': 'Miền Trung',
            'Hồ Chí Minh': 'Miền Nam',
            'Cần Thơ': 'Miền Nam'
        }
        return region_mapping.get(location, 'Unknown')
    
    async def advanced_vector_search(self, query: str, top_k: int = 10,
                                   location_filter: Optional[str] = None,
                                   service_filter: Optional[str] = None,
                                   price_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Advanced search với multi-field embedding và filtering
        """
        try:
            # Extract query components
            query_components = self._analyze_query(query)
            
            # Create query embedding based on detected intent
            query_embedding = self._create_adaptive_query_embedding(query, query_components)
            
            # Build Elasticsearch query
            search_body = self._build_advanced_search_query(
                query_embedding, query_components, top_k, 
                location_filter, service_filter, price_filter
            )
            
            # 🔍 Log Elasticsearch query for debugging
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
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Phân tích query để hiểu intent và components"""
        query_lower = query.lower()
        
        components = {
            'original_query': query,  # 🔥 Add original query
            'location_intent': None,
            'service_intent': None,
            'target_intent': None,
            'primary_focus': 'content'  # default
        }
        
        # Detect location intent
        location_keywords = ['tại', 'ở', 'trong', 'gần']
        for keyword in location_keywords:
            if keyword in query_lower:
                components['location_intent'] = 'high'
                components['primary_focus'] = 'location'
                break
        
        # Detect service intent
        service_keywords = ['buffet', 'nhà hàng', 'ăn', 'uống', 'spa', 'massage']
        for keyword in service_keywords:
            if keyword in query_lower:
                components['service_intent'] = 'high'
                break
        
        # Detect target intent
        target_keywords = ['trẻ em', 'gia đình', 'family', 'kids']
        for keyword in target_keywords:
            if keyword in query_lower:
                components['target_intent'] = 'high'
                break
        
        return components
    
    def _create_adaptive_query_embedding(self, query: str, components: Dict[str, Any]) -> np.ndarray:
        """
        Tạo query embedding thích ứng dựa trên intent
        Trả về base embedding để dùng chung cho tất cả fields
        """
        # Create enhanced query text based on detected intent
        enhanced_query = query
        
        if components['location_intent'] == 'high':
            # Enhance with location context
            enhanced_query = f"Địa điểm địa lý khu vực: {query}"
        elif components['service_intent'] == 'high':
            # Enhance with service context
            enhanced_query = f"Dịch vụ loại hình: {query}"
        elif components['target_intent'] == 'high':
            # Enhance with target context
            enhanced_query = f"Đối tượng phù hợp: {query}"
        
        # Create base embedding for the enhanced query
        base_embedding = self.model.encode(enhanced_query)
        
        return base_embedding
    
    def _build_advanced_search_query(self, query_embedding: np.ndarray, 
                                   query_components: Dict[str, Any],
                                   top_k: int,
                                   location_filter: Optional[str] = None,
                                   service_filter: Optional[str] = None,
                                   price_filter: Optional[str] = None) -> Dict[str, Any]:
        """Build sophisticated Elasticsearch query with MULTI-FIELD VECTOR SEARCH"""
        
        # 🎯 Dynamic weights based on query intent
        weights = self._calculate_dynamic_weights(query_components)
        
        # 🚀 MULTI-FIELD VECTOR SEARCH: Search all embedding fields simultaneously
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        # 🎯 Exact text search (high boost for brand names)
                        {
                            "multi_match": {
                                "query": query_components.get('original_query', ''),
                                "fields": ["voucher_name^3", "content^1"],
                                "type": "best_fields",
                                "boost": 2.0  # Text search boost
                            }
                        },
                        # 🤖 Multi-field semantic search with adaptive weights
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": """
                                        double contentScore = cosineSimilarity(params.query_vector, 'content_embedding') * params.content_weight;
                                        double locationScore = cosineSimilarity(params.query_vector, 'location_embedding') * params.location_weight;
                                        double serviceScore = cosineSimilarity(params.query_vector, 'service_embedding') * params.service_weight;
                                        double targetScore = cosineSimilarity(params.query_vector, 'target_embedding') * params.target_weight;
                                        double combinedScore = cosineSimilarity(params.query_vector, 'combined_embedding') * params.combined_weight;
                                        
                                        return (contentScore + locationScore + serviceScore + targetScore + combinedScore) + 1.0;
                                    """,
                                    "params": {
                                        "query_vector": query_embedding.tolist(),
                                        "content_weight": weights['content'],
                                        "location_weight": weights['location'],
                                        "service_weight": weights['service'],
                                        "target_weight": weights['target'],
                                        "combined_weight": weights['combined']
                                    }
                                },
                                "boost": 3.0  # High boost for semantic similarity
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
    
    def _calculate_dynamic_weights(self, query_components: Dict[str, Any]) -> Dict[str, float]:
        """Calculate adaptive weights based on query intent"""
        # Base weights
        weights = {
            'content': 0.3,
            'location': 0.2,
            'service': 0.2,
            'target': 0.1,
            'combined': 0.2  # Always maintain some combined score
        }
        
        # Adjust weights based on detected intent
        if query_components.get('location_intent') == 'high':
            weights['location'] = 0.4
            weights['content'] = 0.2
            weights['combined'] = 0.3
            weights['service'] = 0.05
            weights['target'] = 0.05
            
        elif query_components.get('service_intent') == 'high':
            weights['service'] = 0.4
            weights['content'] = 0.2
            weights['combined'] = 0.3
            weights['location'] = 0.05
            weights['target'] = 0.05
            
        elif query_components.get('target_intent') == 'high':
            weights['target'] = 0.4
            weights['content'] = 0.2
            weights['combined'] = 0.3
            weights['location'] = 0.05
            weights['service'] = 0.05
        
        return weights
    
    def _process_advanced_results(self, response: Dict[str, Any], 
                                query_components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and enhance search results"""
        results = []
        
        for hit in response.get('hits', {}).get('hits', []):
            score = hit['_score'] - 1.0  # Normalize
            source = hit['_source']
            
            # Apply additional boosting based on query components
            if query_components.get('location_intent') == 'high':
                # Additional location relevance boost already handled by embedding choice
                pass
            
            result = {
                'voucher_id': source.get('voucher_id'),
                'voucher_name': source.get('voucher_name'),
                'content': source.get('content'),
                'similarity_score': round(score, 4),
                'location': source.get('location', {}),
                'service_info': source.get('service_info', {}),
                'price_info': source.get('price_info', {}),
                'target_audience': source.get('target_audience'),
                'search_method': 'advanced_multi_field'
            }
            
            results.append(result)
        
        return results
    
    # ================== RAG INTEGRATION METHODS ==================
    
    async def rag_search_with_llm(self, query: str, top_k: int = 5,
                                 location_filter: Optional[str] = None,
                                 service_filter: Optional[str] = None,
                                 price_filter: Optional[str] = None) -> RAGResponse:
        """
        Complete RAG pipeline: Retrieve + Generate
        """
        start_time = datetime.now()
        
        try:
            # 1. Retrieve relevant vouchers using advanced search
            logger.info(f"🔍 RAG Pipeline started for query: '{query}'")
            retrieved_vouchers = await self.advanced_vector_search(
                query, top_k=top_k,
                location_filter=location_filter,
                service_filter=service_filter, 
                price_filter=price_filter
            )
            
            # 2. Extract query components for context
            query_components = self._analyze_query(query)
            
            # 3. Prepare context for LLM
            context = self._prepare_llm_context(retrieved_vouchers, query_components)
            
            # 4. Generate answer using LLM
            if not retrieved_vouchers:
                answer = self._generate_no_results_response(query)
                confidence_score = 0.0
            else:
                answer = await self._call_llm_with_context(query, context, query_components)
                confidence_score = self._calculate_confidence_score(retrieved_vouchers)
            
            # 5. Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ RAG completed in {processing_time:.2f}s, confidence: {confidence_score:.2f}")
            
            return RAGResponse(
                answer=answer,
                retrieved_vouchers=retrieved_vouchers,
                confidence_score=confidence_score,
                search_method='advanced_rag',
                processing_time=processing_time,
                query_intent=query_components
            )
            
        except Exception as e:
            logger.error(f"❌ RAG pipeline error: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return RAGResponse(
                answer="Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại.",
                retrieved_vouchers=[],
                confidence_score=0.0,
                search_method='error',
                processing_time=processing_time,
                query_intent={}
            )
    
    def _prepare_llm_context(self, retrieved_vouchers: List[Dict[str, Any]], 
                           query_components: Dict[str, Any]) -> str:
        """
        Chuẩn bị context từ retrieved vouchers cho LLM
        """
        if not retrieved_vouchers:
            return "Không tìm thấy voucher phù hợp."
        
        context_parts = []
        context_parts.append("=== THÔNG TIN VOUCHER LIÊN QUAN ===\n")
        
        for i, voucher in enumerate(retrieved_vouchers, 1):
            context_parts.append(f"VOUCHER {i}:")
            context_parts.append(f"Tên: {voucher.get('voucher_name', 'N/A')}")
            context_parts.append(f"Nội dung: {voucher.get('content', 'N/A')}")
            
            # Add structured metadata
            location = voucher.get('location', {})
            if location.get('name') != 'Unknown':
                context_parts.append(f"Địa điểm: {location.get('name')} ({location.get('region', '')})")
            
            service_info = voucher.get('service_info', {})
            if service_info.get('category'):
                context_parts.append(f"Loại dịch vụ: {service_info.get('category')}")
            
            price_info = voucher.get('price_info', {})
            if price_info.get('price_range'):
                context_parts.append(f"Phân khúc giá: {price_info.get('price_range')}")
            
            target_audience = voucher.get('target_audience')
            if target_audience and target_audience != 'General':
                context_parts.append(f"Phù hợp cho: {target_audience}")
            
            similarity_score = voucher.get('similarity_score', 0)
            context_parts.append(f"Độ phù hợp: {similarity_score:.2f}")
            context_parts.append("---")
        
        # Limit context length
        full_context = "\n".join(context_parts)
        if len(full_context) > self.max_context_tokens * 3:  # Rough token estimation
            # Truncate to most relevant vouchers
            truncated_vouchers = retrieved_vouchers[:3]
            return self._prepare_llm_context(truncated_vouchers, query_components)
        
        return full_context
    
    async def _call_llm_with_context(self, query: str, context: str, 
                                   query_components: Dict[str, Any]) -> str:
        """
        Gọi LLM với context để generate answer
        """
        try:
            # Determine response style based on query intent
            response_style = self._get_response_style(query_components)
            
            system_prompt = f"""Bạn là AI Assistant chuyên về voucher   - hệ sinh thái FnB hàng đầu Việt Nam.

NHIỆM VỤ:
- Trả lời câu hỏi của người dùng dựa trên thông tin voucher được cung cấp
- Đưa ra lời khuyên phù hợp và chi tiết
- Giải thích các điều khoản & điều kiện một cách dễ hiểu
- Gợi ý voucher phù hợp nhất

PHONG CÁCH TRẢ LỜI: {response_style}

QUY TẮC:
1. CHỈ sử dụng thông tin từ voucher được cung cấp
2. KHÔNG tự tạo ra thông tin không có trong dữ liệu
3. Nếu không có voucher phù hợp, giải thích lý do và gợi ý tìm kiếm khác
4. Luôn kết thúc với câu hỏi để tương tác thêm
5. Sử dụng emoji phù hợp để làm cho câu trả lời sinh động

THÔNG TIN VOUCHER:
{context}"""

            user_prompt = f"Câu hỏi của khách hàng: {query}"
            
            # Call LLM (using simple HTTP request to avoid openai dependency for now)
            response = await self._make_llm_request(system_prompt, user_prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ LLM call failed: {e}")
            return self._generate_fallback_response(query, context)
    
    def _get_response_style(self, query_components: Dict[str, Any]) -> str:
        """Determine appropriate response style based on query intent"""
        if query_components.get('location_intent') == 'high':
            return "Tập trung vào thông tin địa điểm, khu vực và hướng dẫn đường đi"
        elif query_components.get('service_intent') == 'high':
            return "Chi tiết về dịch vụ, tiện ích và trải nghiệm"
        elif query_components.get('target_intent') == 'high':
            return "Tư vấn phù hợp với đối tượng và nhu cầu cụ thể"
        else:
            return "Tổng quan và gợi ý toàn diện"
    
    async def _make_llm_request(self, system_prompt: str, user_prompt: str) -> str:
        """
        Make LLM request (simplified version without openai dependency)
        In production, integrate with Vertex AI or OpenAI
        """
        # For now, return a structured response based on context
        return self._generate_structured_response(user_prompt, system_prompt)
    
    def _generate_structured_response(self, query: str, context: str) -> str:
        """
        Generate structured response when LLM is not available
        """
        # Extract voucher count from context
        voucher_count = context.count("VOUCHER ")
        
        if voucher_count == 0:
            return f"""🔍 Tôi đã tìm kiếm cho "{query}" nhưng không tìm thấy voucher phù hợp.

💡 **Gợi ý:**
- Thử tìm kiếm với từ khóa khác
- Kiểm tra lại địa điểm hoặc loại dịch vụ
- Liên hệ hotline   để được hỗ trợ thêm

❓ Bạn có muốn tôi tìm kiếm voucher theo tiêu chí khác không?"""
        
        response_parts = [
            f"🎯 Tôi tìm thấy **{voucher_count} voucher** phù hợp với yêu cầu \"{query}\" của bạn:\n"
        ]
        
        # Extract voucher names from context
        voucher_lines = [line for line in context.split('\n') if line.startswith('Tên:')]
        for i, line in enumerate(voucher_lines[:3], 1):
            voucher_name = line.replace('Tên: ', '')
            response_parts.append(f"**{i}.** {voucher_name}")
        
        response_parts.extend([
            "",
            "💡 **Lời khuyên:**",
            "- Kiểm tra điều khoản sử dụng trước khi đặt",
            "- Đặt bàn trước để đảm bảo có chỗ",
            "- Mang theo voucher khi đến sử dụng",
            "",
            "❓ Bạn có muốn tôi giải thích chi tiết về voucher nào không?"
        ])
        
        return "\n".join(response_parts)
    
    def _generate_fallback_response(self, query: str, context: str) -> str:
        """Generate fallback response when LLM fails"""
        return f"""⚡ Dựa trên tìm kiếm cho "{query}", tôi tìm thấy một số voucher có thể phù hợp:

{context[:500]}...

💼 Để được tư vấn chi tiết hơn, vui lòng liên hệ hotline   hoặc thử tìm kiếm với từ khóa cụ thể hơn.

❓ Bạn có câu hỏi gì khác về voucher không?"""
    
    def _generate_no_results_response(self, query: str) -> str:
        """Generate response when no vouchers found"""
        return f"""🔍 Không tìm thấy voucher phù hợp với "{query}".

💡 **Thử các cách sau:**
- Tìm kiếm với từ khóa đơn giản hơn (VD: "buffet", "massage", "spa")
- Chỉ định địa điểm cụ thể (VD: "Hà Nội", "TP.HCM")
- Tìm theo loại dịch vụ (VD: "nhà hàng", "khách sạn")

🌟 **Gợi ý phổ biến:**
- "buffet Hải Phòng" 
- "spa cho gia đình"
- "nhà hàng cao cấp"

❓ Bạn có muốn thử tìm kiếm với từ khóa khác không?"""
    
    def _calculate_confidence_score(self, retrieved_vouchers: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on retrieval results"""
        if not retrieved_vouchers:
            return 0.0
        
        # Calculate based on similarity scores and result count
        avg_similarity = sum(v.get('similarity_score', 0) for v in retrieved_vouchers) / len(retrieved_vouchers)
        
        # Normalize to 0-1 range
        confidence = min(avg_similarity / 50.0, 1.0)  # Assuming max similarity ~50
        
        # Boost confidence if we have multiple good results
        if len(retrieved_vouchers) >= 3 and avg_similarity > 30:
            confidence = min(confidence * 1.2, 1.0)
        
        return round(confidence, 3)
    
    # ================== UNIFIED SEARCH INTERFACE ==================
    
    async def search(self, query: str, 
                    search_type: str = "rag",  # "rag", "vector", "hybrid"
                    top_k: int = 5,
                    location_filter: Optional[str] = None,
                    service_filter: Optional[str] = None,
                    price_filter: Optional[str] = None,
                    return_raw_results: bool = False) -> Dict[str, Any]:
        """
        Unified search interface supporting multiple search types
        
        Args:
            query: Search query in Vietnamese
            search_type: "rag" (full RAG pipeline), "vector" (vector search only), "hybrid"
            top_k: Number of results to return
            location_filter: Filter by specific location
            service_filter: Filter by service category  
            price_filter: Filter by price range
            return_raw_results: If True, return raw search results instead of RAG response
            
        Returns:
            RAGResponse for "rag" search_type, or raw results for others
        """
        if search_type == "rag":
            # Use full RAG pipeline (Retrieval + Generation)
            return await self.rag_search_with_llm(
                query=query,
                top_k=top_k,
                location_filter=location_filter,
                service_filter=service_filter,
                price_filter=price_filter
            )
        
        elif search_type == "vector":
            # Use advanced vector search only
            results = await self.advanced_vector_search(
                query=query,
                top_k=top_k,
                location_filter=location_filter,
                service_filter=service_filter,
                price_filter=price_filter
            )
            
            if return_raw_results:
                return {"results": results, "search_type": "vector"}
            else:
                # Wrap in RAGResponse format for consistency
                return RAGResponse(
                    answer=f"Tìm thấy {len(results)} voucher phù hợp. Đây là kết quả vector search thuần túy.",
                    retrieved_vouchers=results,
                    confidence_score=self._calculate_confidence_score(results),
                    search_method='vector_only',
                    processing_time=0.0,
                    query_intent=self._analyze_query(query)
                )
        
        elif search_type == "hybrid":
            # Hybrid approach: Vector search + minimal context enhancement
            results = await self.advanced_vector_search(
                query=query,
                top_k=top_k,
                location_filter=location_filter,
                service_filter=service_filter,
                price_filter=price_filter
            )
            
            # Generate minimal response without full LLM call
            if results:
                answer = self._generate_hybrid_response(query, results)
            else:
                answer = self._generate_no_results_response(query)
            
            return RAGResponse(
                answer=answer,
                retrieved_vouchers=results,
                confidence_score=self._calculate_confidence_score(results),
                search_method='hybrid',
                processing_time=0.0,
                query_intent=self._analyze_query(query)
            )
        
        else:
            raise ValueError(f"Unsupported search_type: {search_type}. Use 'rag', 'vector', or 'hybrid'")
    
    def _generate_hybrid_response(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Generate a hybrid response with voucher list and basic guidance"""
        if not results:
            return self._generate_no_results_response(query)
        
        response_parts = [
            f"🎯 **Kết quả tìm kiếm cho**: \"{query}\"",
            f"📊 **Tìm thấy**: {len(results)} voucher phù hợp\n"
        ]
        
        # List top vouchers with key details
        for i, voucher in enumerate(results[:3], 1):
            name = voucher.get('voucher_name', 'N/A')
            location = voucher.get('location', {}).get('name', 'N/A')
            similarity = voucher.get('similarity_score', 0)
            
            response_parts.append(f"**{i}. {name}**")
            if location != 'N/A':
                response_parts.append(f"   📍 {location}")
            response_parts.append(f"   ⭐ Độ phù hợp: {similarity:.1f}%\n")
        
        if len(results) > 3:
            response_parts.append(f"... và {len(results) - 3} voucher khác")
        
        response_parts.extend([
            "\n💡 **Để được tư vấn chi tiết hơn, hãy sử dụng chế độ RAG search!**",
            "❓ Bạn có muốn biết thêm thông tin về voucher nào không?"
        ])
        
        return "\n".join(response_parts)
