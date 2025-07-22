"""
Location-Aware Indexing System cho   AI Voucher Assistant
Advanced geographic intelligence với coordinate mapping và region analysis
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import math
from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)

@dataclass
class LocationInfo:
    """Thông tin địa lý chi tiết"""
    name: str
    normalized_name: str
    coordinates: Tuple[float, float]  # (longitude, latitude)
    region: str
    province: str
    districts: List[str]
    landmarks: List[str]
    timezone: str
    population_category: str  # small, medium, large, megacity

@dataclass
class GeographicContext:
    """Geographic context cho search và ranking"""
    primary_location: LocationInfo
    nearby_locations: List[LocationInfo]
    distance_relevance: Dict[str, float]
    cultural_context: List[str]
    economic_level: str

class LocationAwareIndexer:
    """
    Advanced location-aware indexing system
    Hiểu về địa lý Việt Nam và context văn hóa
    """
    
    def __init__(self, es_url: str = "http://localhost:9200"):
        self.es = Elasticsearch([es_url])
        self.location_database = self._build_vietnam_location_database()
        self.distance_threshold = 50  # km
        
        logger.info("🗺️ Location-Aware Indexer initialized")
    
    def _build_vietnam_location_database(self) -> Dict[str, LocationInfo]:
        """Build comprehensive Vietnam location database"""
        return {
            'hải_phòng': LocationInfo(
                name='Hải Phòng',
                normalized_name='hai_phong',
                coordinates=(106.6881, 20.8449),
                region='Miền Bắc',
                province='Hải Phòng',
                districts=['Hồng Bàng', 'Lê Chân', 'Ngô Quyền', 'Kiến An', 'Hải An', 'Đồ Sơn'],
                landmarks=['Cảng Hải Phòng', 'Đồ Sơn', 'Cát Bà', 'Chợ Sắt'],
                timezone='UTC+7',
                population_category='large'
            ),
            'hà_nội': LocationInfo(
                name='Hà Nội',
                normalized_name='ha_noi',
                coordinates=(105.8342, 21.0285),
                region='Miền Bắc',
                province='Hà Nội',
                districts=['Hoàn Kiếm', 'Ba Đình', 'Đống Đa', 'Hai Bà Trưng', 'Cầu Giấy', 'Tây Hồ'],
                landmarks=['Hồ Gươm', 'Văn Miếu', 'Phố Cổ', 'Hồ Tây', 'Nhà hát Lớn'],
                timezone='UTC+7',
                population_category='megacity'
            ),
            'hồ_chí_minh': LocationInfo(
                name='Hồ Chí Minh',
                normalized_name='ho_chi_minh',
                coordinates=(106.6297, 10.8231),
                region='Miền Nam',
                province='Hồ Chí Minh',
                districts=['Quận 1', 'Quận 3', 'Quận 5', 'Quận 7', 'Bình Thạnh', 'Phú Nhuận'],
                landmarks=['Chợ Bến Thành', 'Nhà hát Thành phố', 'Dinh Độc Lập', 'Bitexco'],
                timezone='UTC+7',
                population_category='megacity'
            ),
            'đà_nẵng': LocationInfo(
                name='Đà Nẵng',
                normalized_name='da_nang',
                coordinates=(108.2208, 16.0471),
                region='Miền Trung',
                province='Đà Nẵng',
                districts=['Hải Châu', 'Thanh Khê', 'Sơn Trà', 'Ngũ Hành Sơn', 'Liên Chiểu'],
                landmarks=['Cầu Rồng', 'Bà Nà Hills', 'Ngũ Hành Sơn', 'Biển Mỹ Khê'],
                timezone='UTC+7',
                population_category='large'
            ),
            'cần_thơ': LocationInfo(
                name='Cần Thơ',
                normalized_name='can_tho',
                coordinates=(105.7851, 10.0452),
                region='Miền Nam',
                province='Cần Thơ',
                districts=['Ninh Kiều', 'Bình Thủy', 'Cái Răng', 'Ô Môn', 'Thốt Nốt'],
                landmarks=['Chợ nổi Cái Răng', 'Bến Ninh Kiều', 'Cầu Cần Thơ'],
                timezone='UTC+7',
                population_category='medium'
            ),
            'nha_trang': LocationInfo(
                name='Nha Trang',
                normalized_name='nha_trang',
                coordinates=(109.1967, 12.2585),
                region='Miền Trung',
                province='Khánh Hòa',
                districts=['Nha Trang', 'Vĩnh Nguyên', 'Vạn Thắng', 'Phước Long'],
                landmarks=['Vinpearl', 'Tháp Bà Ponagar', 'Biển Nha Trang', 'Hòn Chồng'],
                timezone='UTC+7',
                population_category='medium'
            )
        }
    
    def normalize_location_name(self, location: str) -> Optional[str]:
        """Normalize location name to standard format"""
        location_lower = location.lower().strip()
        
        # Direct mapping
        name_mappings = {
            'hải phòng': 'hải_phòng',
            'hai phong': 'hải_phòng',
            'haiphong': 'hải_phòng',
            'hà nội': 'hà_nội',
            'ha noi': 'hà_nội',
            'hanoi': 'hà_nội',
            'hồ chí minh': 'hồ_chí_minh',
            'ho chi minh': 'hồ_chí_minh',
            'hcm': 'hồ_chí_minh',
            'sài gòn': 'hồ_chí_minh',
            'saigon': 'hồ_chí_minh',
            'đà nẵng': 'đà_nẵng',
            'da nang': 'đà_nẵng',
            'danang': 'đà_nẵng'
        }
        
        return name_mappings.get(location_lower)
    
    def get_location_info(self, location: str) -> Optional[LocationInfo]:
        """Get detailed location information"""
        normalized = self.normalize_location_name(location)
        if normalized:
            return self.location_database.get(normalized)
        return None
    
    def calculate_distance(self, coord1: Tuple[float, float], 
                          coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates in km"""
        lon1, lat1 = coord1
        lon2, lat2 = coord2
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def find_nearby_locations(self, target_location: LocationInfo) -> List[LocationInfo]:
        """Find locations within distance threshold"""
        nearby = []
        
        for loc_key, location in self.location_database.items():
            if location.name != target_location.name:
                distance = self.calculate_distance(
                    target_location.coordinates, 
                    location.coordinates
                )
                
                if distance <= self.distance_threshold:
                    nearby.append(location)
        
        # Sort by distance
        nearby.sort(key=lambda x: self.calculate_distance(
            target_location.coordinates, x.coordinates
        ))
        
        return nearby
    
    def build_geographic_context(self, location: str) -> Optional[GeographicContext]:
        """Build comprehensive geographic context"""
        location_info = self.get_location_info(location)
        if not location_info:
            return None
        
        nearby_locations = self.find_nearby_locations(location_info)
        
        # Calculate distance relevance for ranking
        distance_relevance = {}
        for nearby in nearby_locations:
            distance = self.calculate_distance(
                location_info.coordinates, 
                nearby.coordinates
            )
            # Relevance decreases with distance
            relevance = max(0, 1 - (distance / self.distance_threshold))
            distance_relevance[nearby.name] = relevance
        
        # Cultural context
        cultural_context = self._get_cultural_context(location_info)
        
        # Economic level
        economic_level = self._get_economic_level(location_info)
        
        return GeographicContext(
            primary_location=location_info,
            nearby_locations=nearby_locations,
            distance_relevance=distance_relevance,
            cultural_context=cultural_context,
            economic_level=economic_level
        )
    
    def _get_cultural_context(self, location: LocationInfo) -> List[str]:
        """Get cultural context for location"""
        context = [location.region]
        
        # Add cultural characteristics
        cultural_mappings = {
            'Hà Nội': ['thủ đô', 'lịch sử', 'văn hóa', 'chính trị', 'giáo dục'],
            'Hồ Chí Minh': ['kinh tế', 'thương mại', 'hiện đại', 'năng động', 'đa văn hóa'],
            'Hải Phòng': ['cảng biển', 'công nghiệp', 'hải sản', 'giao thương'],
            'Đà Nẵng': ['du lịch', 'biển', 'resort', 'nghỉ dưỡng', 'sạch đẹp'],
            'Cần Thơ': ['miệt vườn', 'sông nước', 'đặc sản', 'miền tây'],
            'Nha Trang': ['biển đẹp', 'du lịch', 'nghỉ dưỡng', 'hải sản', 'vui chơi']
        }
        
        context.extend(cultural_mappings.get(location.name, []))
        return context
    
    def _get_economic_level(self, location: LocationInfo) -> str:
        """Determine economic level of location"""
        economic_mappings = {
            'Hà Nội': 'high',
            'Hồ Chí Minh': 'very_high',
            'Đà Nẵng': 'high', 
            'Hải Phòng': 'medium_high',
            'Cần Thơ': 'medium',
            'Nha Trang': 'medium_high'
        }
        
        return economic_mappings.get(location.name, 'medium')
    
    def create_location_aware_mapping(self) -> Dict[str, Any]:
        """Create Elasticsearch mapping optimized for location awareness"""
        return {
            "mappings": {
                "properties": {
                    "voucher_id": {"type": "keyword"},
                    "voucher_name": {"type": "text", "analyzer": "vietnamese"},
                    "content": {"type": "text", "analyzer": "vietnamese"},
                    
                    # Geographic information
                    "location": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "keyword"},
                            "normalized_name": {"type": "keyword"},
                            "coordinates": {"type": "geo_point"},
                            "region": {"type": "keyword"},
                            "province": {"type": "keyword"},
                            "district": {"type": "keyword"},
                            "cultural_context": {"type": "keyword"},
                            "economic_level": {"type": "keyword"},
                            "population_category": {"type": "keyword"}
                        }
                    },
                    
                    # Geographic embeddings
                    "geo_embedding": {
                        "type": "dense_vector",
                        "dims": 768
                    },
                    
                    # Nearby locations for proximity search
                    "nearby_locations": {
                        "type": "nested",
                        "properties": {
                            "name": {"type": "keyword"},
                            "distance": {"type": "float"},
                            "relevance": {"type": "float"}
                        }
                    },
                    
                    # Location-aware boosting factors
                    "location_boost": {
                        "type": "object",
                        "properties": {
                            "exact_match": {"type": "float"},
                            "regional_match": {"type": "float"},
                            "cultural_match": {"type": "float"},
                            "economic_match": {"type": "float"}
                        }
                    },
                    
                    # Standard fields
                    "embeddings": {
                        "type": "dense_vector",
                        "dims": 768
                    },
                    
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
                }
            }
        }
    
    def enhance_voucher_with_location_data(self, voucher_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance voucher data với comprehensive location information"""
        enhanced_data = voucher_data.copy()
        
        # Extract location from metadata or content
        location = voucher_data.get('metadata', {}).get('location', '')
        if not location:
            # Try to extract from content
            location = self._extract_location_from_content(voucher_data.get('content', ''))
        
        if location:
            geo_context = self.build_geographic_context(location)
            if geo_context:
                enhanced_data['location'] = {
                    'name': geo_context.primary_location.name,
                    'normalized_name': geo_context.primary_location.normalized_name,
                    'coordinates': {
                        'lat': geo_context.primary_location.coordinates[1],
                        'lon': geo_context.primary_location.coordinates[0]
                    },
                    'region': geo_context.primary_location.region,
                    'province': geo_context.primary_location.province,
                    'cultural_context': geo_context.cultural_context,
                    'economic_level': geo_context.economic_level,
                    'population_category': geo_context.primary_location.population_category
                }
                
                # Add nearby locations
                enhanced_data['nearby_locations'] = [
                    {
                        'name': nearby.name,
                        'distance': self.calculate_distance(
                            geo_context.primary_location.coordinates,
                            nearby.coordinates
                        ),
                        'relevance': geo_context.distance_relevance.get(nearby.name, 0)
                    }
                    for nearby in geo_context.nearby_locations
                ]
                
                # Calculate location boost factors
                enhanced_data['location_boost'] = self._calculate_location_boost_factors(geo_context)
        
        return enhanced_data
    
    def _extract_location_from_content(self, content: str) -> Optional[str]:
        """Extract location from voucher content"""
        content_lower = content.lower()
        
        for location_name in self.location_database.keys():
            location_info = self.location_database[location_name]
            if location_info.name.lower() in content_lower:
                return location_info.name
        
        return None
    
    def _calculate_location_boost_factors(self, geo_context: GeographicContext) -> Dict[str, float]:
        """Calculate boost factors for different location matching scenarios"""
        return {
            'exact_match': 2.0,  # Exact location match
            'regional_match': 1.5,  # Same region
            'cultural_match': 1.3,  # Similar cultural context
            'economic_match': 1.2,  # Similar economic level
            'proximity_match': 1.4  # Nearby location
        }
    
    def create_geo_aware_search_query(self, query: str, parsed_components: Dict[str, Any],
                                    top_k: int = 10) -> Dict[str, Any]:
        """Create geo-aware search query for Elasticsearch"""
        
        query_location = parsed_components.get('location')
        geo_context = None
        
        if query_location:
            geo_context = self.build_geographic_context(query_location)
        
        # Base vector search
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'embeddings') + 1.0",
                                    "params": {"query_vector": parsed_components.get('query_embedding', [])}
                                }
                            }
                        }
                    ],
                    "should": [],  # For location boosting
                    "filter": []
                }
            },
            "size": top_k,
            "_source": ["voucher_id", "voucher_name", "content", "location", "nearby_locations", "location_boost"]
        }
        
        # Add location-based boosting
        if geo_context:
            # Exact location match (highest boost)
            search_body["query"]["bool"]["should"].append({
                "term": {
                    "location.name": {
                        "value": geo_context.primary_location.name,
                        "boost": 3.0
                    }
                }
            })
            
            # Regional match
            search_body["query"]["bool"]["should"].append({
                "term": {
                    "location.region": {
                        "value": geo_context.primary_location.region,
                        "boost": 1.8
                    }
                }
            })
            
            # Cultural context match
            for cultural_element in geo_context.cultural_context:
                search_body["query"]["bool"]["should"].append({
                    "term": {
                        "location.cultural_context": {
                            "value": cultural_element,
                            "boost": 1.5
                        }
                    }
                })
            
            # Nearby locations match
            for nearby in geo_context.nearby_locations:
                boost_factor = 1.0 + geo_context.distance_relevance.get(nearby.name, 0)
                search_body["query"]["bool"]["should"].append({
                    "term": {
                        "location.name": {
                            "value": nearby.name,
                            "boost": boost_factor
                        }
                    }
                })
            
            # Geographic proximity filter (optional strict filtering)
            if parsed_components.get('strict_location', False):
                search_body["query"]["bool"]["filter"].append({
                    "geo_distance": {
                        "distance": f"{self.distance_threshold}km",
                        "location.coordinates": {
                            "lat": geo_context.primary_location.coordinates[1],
                            "lon": geo_context.primary_location.coordinates[0]
                        }
                    }
                })
        
        return search_body
    
    def explain_geographic_ranking(self, results: List[Dict[str, Any]], 
                                 query_location: str) -> str:
        """Explain how geographic factors influenced ranking"""
        explanation = f"Kết quả tìm kiếm cho địa điểm: {query_location}\n\n"
        
        geo_context = self.build_geographic_context(query_location)
        if not geo_context:
            return explanation + "Không tìm thấy thông tin địa lý cho location này."
        
        explanation += f"📍 Thông tin địa lý:\n"
        explanation += f"- Tọa độ: {geo_context.primary_location.coordinates}\n"
        explanation += f"- Vùng: {geo_context.primary_location.region}\n"
        explanation += f"- Bối cảnh văn hóa: {', '.join(geo_context.cultural_context)}\n"
        explanation += f"- Mức kinh tế: {geo_context.economic_level}\n\n"
        
        explanation += f"🎯 Ranking factors:\n"
        for i, result in enumerate(results[:5], 1):
            location_data = result.get('location', {})
            result_location = location_data.get('name', 'Unknown')
            
            if result_location == query_location:
                explanation += f"{i}. {result.get('voucher_name', '')[:50]}... (EXACT MATCH ✅)\n"
            elif location_data.get('region') == geo_context.primary_location.region:
                explanation += f"{i}. {result.get('voucher_name', '')[:50]}... (SAME REGION 🌍)\n"
            else:
                explanation += f"{i}. {result.get('voucher_name', '')[:50]}... (OTHER LOCATION 📍)\n"
        
        if geo_context.nearby_locations:
            explanation += f"\n🗺️ Địa điểm lân cận được xem xét:\n"
            for nearby in geo_context.nearby_locations[:3]:
                distance = self.calculate_distance(
                    geo_context.primary_location.coordinates,
                    nearby.coordinates
                )
                explanation += f"- {nearby.name} ({distance:.1f}km)\n"
        
        return explanation
