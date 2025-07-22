"""
Smart Query Parser cho   AI Voucher Assistant
Phân tích và hiểu ý định người dùng từ natural language queries
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QueryIntent(Enum):
    """Các loại intent chính"""
    FIND_RESTAURANT = "find_restaurant"
    FIND_HOTEL = "find_hotel" 
    FIND_ENTERTAINMENT = "find_entertainment"
    FIND_SHOPPING = "find_shopping"
    FIND_BEAUTY = "find_beauty"
    FIND_TRAVEL = "find_travel"
    FIND_KIDS = "find_kids"
    GENERAL_SEARCH = "general_search"

class LocationType(Enum):
    """Loại địa điểm"""
    CITY = "city"
    DISTRICT = "district"  
    LANDMARK = "landmark"
    REGION = "region"

@dataclass 
class QueryComponents:
    """Các thành phần được extract từ query"""
    original_query: str
    intent: QueryIntent
    location: Optional[str] = None
    location_type: Optional[LocationType] = None
    service_requirements: List[str] = None
    target_audience: Optional[str] = None
    price_preference: Optional[str] = None
    time_requirements: List[str] = None
    keywords: List[str] = None
    modifiers: List[str] = None
    confidence: float = 0.0

class SmartQueryParser:
    """
    Advanced Query Parser cho Vietnamese natural language
    Hiểu và phân tích ý định người dùng
    """
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.location_patterns = self._load_location_patterns()
        self.service_patterns = self._load_service_patterns()
        self.target_patterns = self._load_target_patterns()
        self.time_patterns = self._load_time_patterns()
        self.modifier_patterns = self._load_modifier_patterns()
        
        logger.info("🧠 Smart Query Parser initialized")
    
    def _load_intent_patterns(self) -> Dict[QueryIntent, List[str]]:
        """Load patterns for intent detection - support both with and without diacritics"""
        return {
            QueryIntent.FIND_RESTAURANT: [
                r'(quán ăn|quan an|nhà hàng|nha hang|ăn uống|an uong|buffet|thức ăn|thuc an|món ăn|mon an|bữa ăn|bua an)',
                r'(restaurant|food|eat|dining|meal|cafe|quan cafe)',
                r'(đói|doi|thèm|them|muốn ăn|muon an)',
                r'(bellissimo|silk path|sheraton|renaissance|capella|mercure|daewoo)'  # Brand names
            ],
            QueryIntent.FIND_HOTEL: [
                r'(khách sạn|khach san|resort|homestay|villa|nơi ở|noi o|nghỉ dưỡng|nghi duong)',
                r'(hotel|accommodation|stay|lodge)',
                r'(ngủ|ngu|nghỉ|nghi|ở lại|o lai)'
            ],
            QueryIntent.FIND_ENTERTAINMENT: [
                r'(giải trí|giai tri|vui chơi|vui choi|trò chơi|tro choi|game|sự kiện|su kien|show)',
                r'(entertainment|fun|play|event|activity)',
                r'(chơi|choi|vui|thư giãn|thu gian)'
            ],
            QueryIntent.FIND_SHOPPING: [
                r'(mua sắm|mua sam|cửa hàng|cua hang|siêu thị|sieu thi|mall|shopping)',
                r'(shop|store|buy|purchase)',
                r'(mua|sắm|sam|tìm mua|tim mua)'
            ],
            QueryIntent.FIND_BEAUTY: [
                r'(làm đẹp|lam dep|spa|massage|salon|nail|tóc|toc)',
                r'(beauty|wellness|relaxation)',
                r'(đẹp|dep|thư giãn|thu gian|chăm sóc|cham soc)'
            ],
            QueryIntent.FIND_KIDS: [
                r'(trẻ em|tre em|trẻ con|tre con|bé yêu|be yeu|em bé|em be|children|kids)',
                r'(đồ chơi|do choi|playground|khu vui chơi|khu vui choi)',
                r'(family|gia đình.*trẻ|gia dinh.*tre)'
            ]
        }
    
    def _load_location_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load location patterns with metadata - support both with and without diacritics"""
        return {
            'cities': {
                # With diacritics
                'hải phòng': {'normalized': 'Hải Phòng', 'region': 'Miền Bắc', 'type': LocationType.CITY},
                'hà nội': {'normalized': 'Hà Nội', 'region': 'Miền Bắc', 'type': LocationType.CITY},
                'hồ chí minh': {'normalized': 'Hồ Chí Minh', 'region': 'Miền Nam', 'type': LocationType.CITY},
                'hcm': {'normalized': 'Hồ Chí Minh', 'region': 'Miền Nam', 'type': LocationType.CITY},
                'sài gòn': {'normalized': 'Hồ Chí Minh', 'region': 'Miền Nam', 'type': LocationType.CITY},
                'đà nẵng': {'normalized': 'Đà Nẵng', 'region': 'Miền Trung', 'type': LocationType.CITY},
                'cần thơ': {'normalized': 'Cần Thơ', 'region': 'Miền Nam', 'type': LocationType.CITY},
                'nha trang': {'normalized': 'Nha Trang', 'region': 'Miền Trung', 'type': LocationType.CITY},
                'vũng tàu': {'normalized': 'Vũng Tàu', 'region': 'Miền Nam', 'type': LocationType.CITY},
                'huế': {'normalized': 'Huế', 'region': 'Miền Trung', 'type': LocationType.CITY},
                'đà lạt': {'normalized': 'Đà Lạt', 'region': 'Miền Nam', 'type': LocationType.CITY},
                # Without diacritics
                'hai phong': {'normalized': 'Hải Phòng', 'region': 'Miền Bắc', 'type': LocationType.CITY},
                'ha noi': {'normalized': 'Hà Nội', 'region': 'Miền Bắc', 'type': LocationType.CITY},
                'hanoi': {'normalized': 'Hà Nội', 'region': 'Miền Bắc', 'type': LocationType.CITY},
                'ho chi minh': {'normalized': 'Hồ Chí Minh', 'region': 'Miền Nam', 'type': LocationType.CITY},
                'saigon': {'normalized': 'Hồ Chí Minh', 'region': 'Miền Nam', 'type': LocationType.CITY},
                'sai gon': {'normalized': 'Hồ Chí Minh', 'region': 'Miền Nam', 'type': LocationType.CITY},
                'da nang': {'normalized': 'Đà Nẵng', 'region': 'Miền Trung', 'type': LocationType.CITY},
                'can tho': {'normalized': 'Cần Thơ', 'region': 'Miền Nam', 'type': LocationType.CITY},
                'vung tau': {'normalized': 'Vũng Tàu', 'region': 'Miền Nam', 'type': LocationType.CITY},
                'hue': {'normalized': 'Huế', 'region': 'Miền Trung', 'type': LocationType.CITY},
                'da lat': {'normalized': 'Đà Lạt', 'region': 'Miền Nam', 'type': LocationType.CITY}
            },
            'districts': {
                'quận 1': {'normalized': 'Quận 1', 'city': 'Hồ Chí Minh', 'type': LocationType.DISTRICT},
                'quận 3': {'normalized': 'Quận 3', 'city': 'Hồ Chí Minh', 'type': LocationType.DISTRICT},
                'ba đình': {'normalized': 'Ba Đình', 'city': 'Hà Nội', 'type': LocationType.DISTRICT},
                'hoàn kiếm': {'normalized': 'Hoàn Kiếm', 'city': 'Hà Nội', 'type': LocationType.DISTRICT},
                'hồng bàng': {'normalized': 'Hồng Bàng', 'city': 'Hải Phòng', 'type': LocationType.DISTRICT}
            },
            'regions': {
                'miền bắc': {'normalized': 'Miền Bắc', 'type': LocationType.REGION},
                'miền trung': {'normalized': 'Miền Trung', 'type': LocationType.REGION},
                'miền nam': {'normalized': 'Miền Nam', 'type': LocationType.REGION}
            }
        }
    
    def _load_service_patterns(self) -> Dict[str, List[str]]:
        """Load service requirement patterns"""
        return {
            'kids_friendly': [
                r'(trẻ em|trẻ con|bé|children|kids)',
                r'(khu vui chơi|playground|chỗ.*chơi)',
                r'(gia đình.*trẻ|family.*kids)'
            ],
            'romantic': [
                r'(lãng mạn|romantic|cặp đôi|couple)',
                r'(hẹn hò|date|tình yêu)',
                r'(không gian.*riêng tư|private)'
            ],
            'group_dining': [
                r'(nhóm|group|team|công ty)',
                r'(tập thể|đông người|many people)',
                r'(tiệc|party|celebration)'
            ],
            'luxury': [
                r'(sang trọng|luxury|cao cấp|premium)',
                r'(vip|exclusive|đẳng cấp)',
                r'(high.?end|upscale)'
            ],
            'budget': [
                r'(rẻ|cheap|budget|giá.*thấp)',
                r'(tiết kiệm|affordable|reasonab)',
                r'(sinh viên|student)'
            ],
            'outdoor': [
                r'(ngoài trời|outdoor|sân vườn)',
                r'(không gian.*mở|open.?space)',
                r'(view.*đẹp|scenic)'
            ],
            'indoor': [
                r'(trong nhà|indoor|có.*máy lạnh)',
                r'(điều hòa|air.?con)',
                r'(kín.*gió|enclosed)'
            ]
        }
    
    def _load_target_patterns(self) -> Dict[str, List[str]]:
        """Load target audience patterns"""
        return {
            'family': [
                r'(gia đình|family|cả nhà)',
                r'(bố mẹ.*con|parents.*children)',
                r'(nhiều thế hệ|multi.?generation)'
            ],
            'couple': [
                r'(cặp đôi|couple|hai người)',
                r'(bạn trai.*bạn gái|boyfriend.*girlfriend)',
                r'(chồng.*vợ|husband.*wife)'
            ],
            'friends': [
                r'(bạn bè|friends|hội bạn)',
                r'(nhóm.*bạn|group.*friends)',
                r'(gathering|get.?together)'
            ],
            'business': [
                r'(công việc|business|meeting)',
                r'(họp|conference|khách hàng)',
                r'(đối tác|partner|client)'
            ],
            'solo': [
                r'(một mình|solo|individual)',
                r'(cá nhân|personal|alone)',
                r'(tự.*một|by.*myself)'
            ]
        }
    
    def _load_time_patterns(self) -> Dict[str, List[str]]:
        """Load time-related patterns"""
        return {
            'weekend': [
                r'(cuối tuần|weekend|thứ.*7|chủ nhật)',
                r'(saturday|sunday|nghỉ.*tuần)'
            ],
            'weekday': [
                r'(trong tuần|weekday|thứ.*[2-6])',
                r'(monday|tuesday|wednesday|thursday|friday)',
                r'(ngày.*thường|working.*day)'
            ],
            'evening': [
                r'(tối|evening|night|buổi.*tối)',
                r'(dinner|bữa.*tối|ăn.*tối)'
            ],
            'lunch': [
                r'(trưa|lunch|buổi.*trưa)',
                r'(bữa.*trưa|ăn.*trưa|noon)'
            ],
            'morning': [
                r'(sáng|morning|buổi.*sáng)',
                r'(breakfast|bữa.*sáng|ăn.*sáng)'
            ],
            'holiday': [
                r'(lễ|holiday|nghỉ.*lễ|festival)',
                r'(tết|new.*year|christmas|celebration)'
            ]
        }
    
    def _load_modifier_patterns(self) -> Dict[str, List[str]]:
        """Load query modifiers (urgent, flexible, etc.)"""
        return {
            'urgent': [
                r'(gấp|urgent|ngay.*bây.*giờ|immediately)',
                r'(khẩn.*cấp|asap|rush)'
            ],
            'flexible': [
                r'(linh hoạt|flexible|tùy.*ý)',
                r'(không.*cố định|not.*fixed|open)'
            ],
            'specific': [
                r'(cụ thể|specific|chính xác|exact)',
                r'(đúng.*như|exactly.*like)'
            ],
            'recommendation': [
                r'(đề xuất|recommend|gợi ý|suggest)',
                r'(tư vấn|advice|nên.*chọn)'
            ]
        }
    
    def parse_query(self, query: str) -> QueryComponents:
        """
        Main method để parse user query
        """
        query_lower = query.lower().strip()
        
        # Initialize components
        components = QueryComponents(
            original_query=query,
            intent=QueryIntent.GENERAL_SEARCH,
            service_requirements=[],
            time_requirements=[],
            keywords=[],
            modifiers=[]
        )
        
        # Extract intent
        components.intent, intent_confidence = self._extract_intent(query_lower)
        
        # Extract location
        components.location, components.location_type, location_confidence = self._extract_location(query_lower)
        
        # Extract service requirements
        components.service_requirements, service_confidence = self._extract_service_requirements(query_lower)
        
        # Extract target audience
        components.target_audience, target_confidence = self._extract_target_audience(query_lower)
        
        # Extract time requirements
        components.time_requirements = self._extract_time_requirements(query_lower)
        
        # Extract modifiers
        components.modifiers = self._extract_modifiers(query_lower)
        
        # Extract keywords
        components.keywords = self._extract_keywords(query_lower)
        
        # Calculate overall confidence
        components.confidence = self._calculate_confidence(
            intent_confidence, location_confidence, service_confidence, target_confidence
        )
        
        logger.info(f"🔍 Parsed query: {query}")
        logger.info(f"   Intent: {components.intent.value} (confidence: {components.confidence:.2f})")
        logger.info(f"   Location: {components.location}")
        logger.info(f"   Requirements: {components.service_requirements}")
        
        return components
    
    def _extract_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """Extract main intent from query"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                score += len(matches)
            
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            confidence = min(best_intent[1] / len(query.split()), 1.0)
            return best_intent[0], confidence
        
        return QueryIntent.GENERAL_SEARCH, 0.5
    
    def _extract_location(self, query: str) -> Tuple[Optional[str], Optional[LocationType], float]:
        """Extract location with type detection"""
        # Check cities first
        for location_key, location_info in self.location_patterns['cities'].items():
            if location_key in query:
                return location_info['normalized'], location_info['type'], 0.9
        
        # Check districts
        for district_key, district_info in self.location_patterns['districts'].items():
            if district_key in query:
                return district_info['normalized'], district_info['type'], 0.8
        
        # Check regions
        for region_key, region_info in self.location_patterns['regions'].items():
            if region_key in query:
                return region_info['normalized'], region_info['type'], 0.7
        
        # Use location prepositions to find potential locations
        location_indicators = [r'tại\s+([^,\s]+)', r'ở\s+([^,\s]+)', r'trong\s+([^,\s]+)']
        for pattern in location_indicators:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                # Try to normalize the found location
                potential_location = matches[0].strip()
                normalized = self._normalize_location(potential_location)
                if normalized:
                    return normalized, LocationType.CITY, 0.6
        
        return None, None, 0.0
    
    def _normalize_location(self, location: str) -> Optional[str]:
        """Normalize detected location"""
        location_lower = location.lower()
        
        # Check if it matches any known location
        all_locations = {**self.location_patterns['cities'], 
                        **self.location_patterns['districts']}
        
        for key, info in all_locations.items():
            if key in location_lower or location_lower in key:
                return info['normalized']
        
        return None
    
    def _extract_service_requirements(self, query: str) -> Tuple[List[str], float]:
        """Extract service requirements"""
        requirements = []
        total_matches = 0
        
        for requirement, patterns in self.service_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    requirements.append(requirement)
                    total_matches += 1
                    break
        
        confidence = min(total_matches / 3, 1.0) if requirements else 0.0
        return requirements, confidence
    
    def _extract_target_audience(self, query: str) -> Tuple[Optional[str], float]:
        """Extract target audience"""
        audience_scores = {}
        
        for audience, patterns in self.target_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    score += 1
            
            if score > 0:
                audience_scores[audience] = score
        
        if audience_scores:
            best_audience = max(audience_scores.items(), key=lambda x: x[1])
            confidence = min(best_audience[1] / 2, 1.0)
            return best_audience[0], confidence
        
        return None, 0.0
    
    def _extract_time_requirements(self, query: str) -> List[str]:
        """Extract time-related requirements"""
        time_reqs = []
        
        for time_type, patterns in self.time_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    time_reqs.append(time_type)
                    break
        
        return time_reqs
    
    def _extract_modifiers(self, query: str) -> List[str]:
        """Extract query modifiers"""
        modifiers = []
        
        for modifier, patterns in self.modifier_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    modifiers.append(modifier)
                    break
        
        return modifiers
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords for search"""
        # Remove common Vietnamese stop words
        stop_words = {
            'tôi', 'tại', 'ở', 'trong', 'có', 'là', 'và', 'với', 'cho', 'của', 
            'một', 'các', 'này', 'đó', 'được', 'sẽ', 'đã', 'từ', 'về', 'như',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'
        }
        
        # Split and clean words
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def _calculate_confidence(self, intent_conf: float, location_conf: float, 
                            service_conf: float, target_conf: float) -> float:
        """Calculate overall parsing confidence"""
        # Weighted average of individual confidences
        weights = [0.3, 0.3, 0.2, 0.2]  # intent, location, service, target
        confidences = [intent_conf, location_conf, service_conf, target_conf]
        
        weighted_sum = sum(w * c for w, c in zip(weights, confidences))
        return min(weighted_sum, 1.0)
    
    def generate_search_strategy(self, components: QueryComponents) -> Dict[str, Any]:
        """
        Generate search strategy based on parsed components
        """
        strategy = {
            'primary_field': 'combined_embedding',
            'boost_factors': {},
            'filters': {},
            'ranking_weights': {
                'semantic_similarity': 0.4,
                'location_match': 0.3,
                'service_match': 0.2,
                'target_match': 0.1
            }
        }
        
        # Adjust strategy based on intent and components
        if components.location and components.location_type == LocationType.CITY:
            strategy['primary_field'] = 'location_embedding'
            strategy['boost_factors']['location_exact_match'] = 2.0
            strategy['filters']['location'] = components.location
            strategy['ranking_weights']['location_match'] = 0.5
            strategy['ranking_weights']['semantic_similarity'] = 0.3
        
        if 'kids_friendly' in components.service_requirements:
            strategy['boost_factors']['kids_area'] = 1.5
            strategy['filters']['has_kids_area'] = True
        
        if 'luxury' in components.service_requirements:
            strategy['filters']['price_range'] = ['Premium', 'Luxury']
        elif 'budget' in components.service_requirements:
            strategy['filters']['price_range'] = ['Budget', 'Mid-range']
        
        # Time-based adjustments
        if 'weekend' in components.time_requirements:
            strategy['boost_factors']['weekend_available'] = 1.2
        
        # Confidence-based adjustments
        if components.confidence < 0.5:
            strategy['ranking_weights']['semantic_similarity'] = 0.6  # Fall back to semantic
            strategy['primary_field'] = 'combined_embedding'
        
        return strategy
    
    def explain_parsing(self, components: QueryComponents) -> str:
        """
        Generate human-readable explanation of parsing results
        """
        explanation = f"Phân tích query: '{components.original_query}'\n"
        explanation += f"- Ý định: {components.intent.value}\n"
        
        if components.location:
            explanation += f"- Địa điểm: {components.location} ({components.location_type.value})\n"
        
        if components.service_requirements:
            explanation += f"- Yêu cầu dịch vụ: {', '.join(components.service_requirements)}\n"
        
        if components.target_audience:
            explanation += f"- Đối tượng: {components.target_audience}\n"
        
        if components.time_requirements:
            explanation += f"- Thời gian: {', '.join(components.time_requirements)}\n"
        
        explanation += f"- Độ tin cậy: {components.confidence:.2f}"
        
        return explanation
