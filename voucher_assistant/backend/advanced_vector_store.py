"""
Advanced Vector Store với Multi-field Embedding Strategy
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

logger = logging.getLogger(__name__)

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
        self.weights = EmbeddingWeights()
        
        # Initialize embedding model
        self.model = SentenceTransformer(embedding_model)        
        logger.info(f"🤖 Advanced Vector Store initialized with model: {embedding_model}")
        
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
        """
        # Adjust weights based on detected intent
        adaptive_weights = EmbeddingWeights()
        
        if components['location_intent'] == 'high':
            adaptive_weights.location = 0.5
            adaptive_weights.content = 0.3
            adaptive_weights.service_type = 0.1
            adaptive_weights.target_audience = 0.1
        elif components['service_intent'] == 'high':
            adaptive_weights.service_type = 0.4
            adaptive_weights.content = 0.3
            adaptive_weights.location = 0.2
            adaptive_weights.target_audience = 0.1
        elif components['target_intent'] == 'high':
            adaptive_weights.target_audience = 0.4
            adaptive_weights.content = 0.3
            adaptive_weights.service_type = 0.2
            adaptive_weights.location = 0.1
        
        # Create weighted query embedding
        base_embedding = self.model.encode(query)
        
        # For now, return base embedding (can be enhanced with multiple embeddings)
        return base_embedding
    
    def _build_advanced_search_query(self, query_embedding: np.ndarray, 
                                   query_components: Dict[str, Any],
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
                                "query": query_components.get('original_query', ''),
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
