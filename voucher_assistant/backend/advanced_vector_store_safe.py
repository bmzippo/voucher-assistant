"""
Advanced Vector Store với Multi-field Embedding Strategy (Safe Version)
Phần của   AI Voucher Assistant - Phase 2
"""

import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
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

class MockEmbeddingModel:
    """Mock embedding model to avoid PyTorch issues"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        logger.info(f"🔧 Mock Embedding Model initialized (dimension: {dimension})")
    
    def encode(self, texts: List[str], **kwargs) -> np.ndarray:
        """Generate mock embeddings"""
        if isinstance(texts, str):
            texts = [texts]
        
        # Generate deterministic mock embeddings based on text hash
        embeddings = []
        for text in texts:
            # Create a deterministic embedding based on text hash
            hash_val = hash(text) % (2**31)
            np.random.seed(hash_val)
            embedding = np.random.normal(0, 1, self.dimension)
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)
        
        return np.array(embeddings)

class AdvancedVectorStoreSafe:
    """
    Safe Advanced Vector Store với multi-field embedding strategy
    Tối ưu hóa cho   ecosystem (without model loading issues)
    """
    
    def __init__(self, es_url: str = "http://localhost:9200", 
                 embedding_model: str = "mock-vietnamese-sbert",
                 index_name: str = "vouchers_advanced"):
        self.es_url = es_url
        # Mock Elasticsearch connection for now
        self.es = None  # Would be: Elasticsearch([es_url])
        self.index_name = index_name
        self.embedding_model_name = embedding_model
        self.embedding_dimension = 768
        self.weights = EmbeddingWeights()
        
        # Initialize mock embedding model
        self.model = MockEmbeddingModel(self.embedding_dimension)
        logger.info(f"🤖 Safe Advanced Vector Store initialized with mock model: {embedding_model}")
        
        # Create advanced index mapping
        self._create_advanced_index()
    
    def _create_advanced_index(self):
        """Tạo Elasticsearch index với advanced mapping (Mock)"""
        mapping = {
            "mappings": {
                "properties": {
                    "voucher_id": {"type": "keyword"},
                    "voucher_name": {"type": "text", "analyzer": "vietnamese"},
                    "content": {"type": "text", "analyzer": "vietnamese"},
                    
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
                    "keyword_embedding": {
                        "type": "dense_vector",
                        "dims": self.embedding_dimension
                    },
                    
                    # Composite embedding
                    "composite_embedding": {
                        "type": "dense_vector",
                        "dims": self.embedding_dimension
                    },
                    
                    # Structured fields
                    "location": {"type": "keyword"},
                    "service_type": {"type": "keyword"},
                    "target_audience": {"type": "keyword"},
                    "keywords": {"type": "keyword"},
                    "price_range": {"type": "keyword"},
                    "usage_instructions": {"type": "text", "analyzer": "vietnamese"},
                    "terms_conditions": {"type": "text", "analyzer": "vietnamese"},
                    
                    # Metadata
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "merchant": {"type": "keyword"},
                    "tags": {"type": "keyword"}
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
                }
            }
        }
        
        logger.info(f"📝 Advanced index mapping created for: {self.index_name} (Mock)")
        return mapping
    
    def extract_voucher_components(self, voucher_data: Dict[str, Any]) -> VoucherComponents:
        """Extract và phân loại components từ voucher data"""
        
        # Extract content
        content_fields = ["name", "desc", "description", "details"]
        content = ""
        for field in content_fields:
            if field in voucher_data and voucher_data[field]:
                content += f"{voucher_data[field]} "
        
        # Extract location
        location = voucher_data.get("location", "").strip()
        if not location:
            # Try to extract from content
            location_patterns = [
                r"(?i)(hà nội|hồ chí minh|đà nẵng|hải phòng|cần thơ|nha trang|vũng tàu|đà lạt)",
                r"(?i)(tp\.|thành phố|tỉnh|quận|huyện)\s*([^,\.\n]+)"
            ]
            for pattern in location_patterns:
                match = re.search(pattern, content)
                if match:
                    location = match.group().strip()
                    break
        
        # Extract service type
        service_type = ""
        service_patterns = [
            r"(?i)(ăn uống|thức ăn|đồ ăn|restaurant|food)",
            r"(?i)(du lịch|travel|tour|khách sạn|hotel)",
            r"(?i)(mua sắm|shopping|thời trang|fashion)",
            r"(?i)(giải trí|entertainment|massage|spa)",
            r"(?i)(giao thông|vé xe|taxi|grab)"
        ]
        
        service_mapping = {
            0: "food_beverage",
            1: "travel_hotel", 
            2: "shopping_fashion",
            3: "entertainment_spa",
            4: "transportation"
        }
        
        for i, pattern in enumerate(service_patterns):
            if re.search(pattern, content):
                service_type = service_mapping[i]
                break
        
        # Extract target audience
        target_audience = ""
        target_patterns = [
            r"(?i)(gia đình|family)",
            r"(?i)(sinh viên|student)",
            r"(?i)(doanh nhân|business)",
            r"(?i)(cặp đôi|couple)"
        ]
        
        target_mapping = {
            0: "family",
            1: "student",
            2: "business", 
            3: "couple"
        }
        
        for i, pattern in enumerate(target_patterns):
            if re.search(pattern, content):
                target_audience = target_mapping[i]
                break
        
        # Extract keywords
        keywords = []
        if "tags" in voucher_data and voucher_data["tags"]:
            keywords.extend(voucher_data["tags"].split(","))
        
        # Extract from content
        keyword_patterns = [
            r"(?i)(giảm giá|discount|sale)",
            r"(?i)(miễn phí|free|gratis)",
            r"(?i)(combo|package|gói)",
            r"(?i)(vip|premium|cao cấp)",
            r"(?i)(online|trực tuyến)",
            r"(?i)(offline|tại cửa hàng)"
        ]
        
        for pattern in keyword_patterns:
            if re.search(pattern, content):
                keywords.append(re.search(pattern, content).group().lower())
        
        # Price range extraction
        price_range = ""
        if "price" in voucher_data and voucher_data["price"]:
            price = float(voucher_data["price"])
            if price < 100000:
                price_range = "budget"
            elif price < 500000:
                price_range = "mid_range"
            else:
                price_range = "premium"
        
        return VoucherComponents(
            content=content.strip(),
            location=location,
            service_type=service_type,
            target_audience=target_audience,
            keywords=list(set(keywords)),
            price_range=price_range
        )
    
    def create_multi_field_embeddings(self, components: VoucherComponents) -> Dict[str, np.ndarray]:
        """Tạo embeddings cho từng field"""
        
        embeddings = {}
        
        # Content embedding
        if components.content:
            embeddings["content"] = self.model.encode([components.content])[0]
        
        # Location embedding  
        if components.location:
            embeddings["location"] = self.model.encode([f"địa điểm {components.location}"])[0]
        
        # Service type embedding
        if components.service_type:
            embeddings["service"] = self.model.encode([f"dịch vụ {components.service_type}"])[0]
        
        # Target audience embedding
        if components.target_audience:
            embeddings["target"] = self.model.encode([f"đối tượng {components.target_audience}"])[0]
        
        # Keywords embedding
        if components.keywords:
            keyword_text = " ".join(components.keywords)
            embeddings["keywords"] = self.model.encode([keyword_text])[0]
        
        return embeddings
    
    def create_composite_embedding(self, field_embeddings: Dict[str, np.ndarray]) -> np.ndarray:
        """Tạo composite embedding từ các field embeddings với trọng số"""
        
        composite = np.zeros(self.embedding_dimension)
        total_weight = 0
        
        weight_mapping = {
            "content": self.weights.content,
            "location": self.weights.location,
            "service": self.weights.service_type,
            "target": self.weights.target_audience,
            "keywords": self.weights.keywords
        }
        
        for field, embedding in field_embeddings.items():
            if field in weight_mapping:
                weight = weight_mapping[field]
                composite += embedding * weight
                total_weight += weight
        
        # Normalize
        if total_weight > 0:
            composite = composite / total_weight
            composite = composite / np.linalg.norm(composite)
        
        return composite
    
    def add_voucher(self, voucher_data: Dict[str, Any]) -> bool:
        """Thêm voucher vào vector store"""
        try:
            # Extract components
            components = self.extract_voucher_components(voucher_data)
            
            # Create multi-field embeddings
            field_embeddings = self.create_multi_field_embeddings(components)
            
            # Create composite embedding
            composite_embedding = self.create_composite_embedding(field_embeddings)
            
            # Prepare document
            doc = {
                "voucher_id": voucher_data.get("id", ""),
                "voucher_name": voucher_data.get("name", ""),
                "content": components.content,
                "location": components.location,
                "service_type": components.service_type,
                "target_audience": components.target_audience,
                "keywords": components.keywords,
                "price_range": components.price_range,
                "usage_instructions": voucher_data.get("usage", ""),
                "terms_conditions": voucher_data.get("termofuse", ""),
                "merchant": voucher_data.get("merchant", ""),
                "tags": voucher_data.get("tags", "").split(",") if voucher_data.get("tags") else [],
                
                # Embeddings
                "composite_embedding": composite_embedding.tolist(),
                **{f"{field}_embedding": emb.tolist() for field, emb in field_embeddings.items()}
            }
            
            logger.info(f"✅ Document prepared for voucher: {voucher_data.get('name', 'Unknown')}")
            
            # In a real implementation, would index to Elasticsearch:
            # result = self.es.index(index=self.index_name, document=doc)
            # logger.info(f"✅ Voucher indexed: {result['_id']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding voucher: {str(e)}")
            return False
    
    def search_vouchers(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """Tìm kiếm vouchers với advanced vector search"""
        try:
            # Create query embedding
            query_embedding = self.model.encode([query])[0]
            
            logger.info(f"🔍 Searching for: '{query}' (Mock search)")
            
            # Mock search results
            mock_results = [
                {
                    "voucher_id": "mock_001",
                    "voucher_name": "Voucher mẫu 1",
                    "content": f"Kết quả tìm kiếm cho: {query}",
                    "score": 0.95,
                    "location": "Hà Nội",
                    "service_type": "food_beverage"
                },
                {
                    "voucher_id": "mock_002", 
                    "voucher_name": "Voucher mẫu 2",
                    "content": f"Kết quả liên quan đến: {query}",
                    "score": 0.87,
                    "location": "TP.HCM",
                    "service_type": "travel_hotel"
                }
            ]
            
            return mock_results[:size]
            
        except Exception as e:
            logger.error(f"❌ Error searching vouchers: {str(e)}")
            return []
