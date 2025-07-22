"""
Voucher Data Cleaner Module
Handles data cleaning, normalization, and enhancement
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class VoucherDataCleaner:
    """
    Advanced data cleaner for voucher data
    """
    
    def __init__(self):
        self.cleaned_count = 0
        self.enhancement_stats = {
            'location_extracted': 0,
            'business_type_detected': 0,
            'service_info_analyzed': 0,
            'invalid_data_cleaned': 0
        }
    
    def clean_voucher_data(self, voucher_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize a single voucher data entry
        """
        # Create a copy to avoid modifying original
        cleaned_data = voucher_data.copy()
        
        # Handle NaN and empty values
        cleaned_data = self._handle_nan_values(cleaned_data)
        
        # Extract location if missing
        if not cleaned_data.get('location') or cleaned_data['location'] in ['nan', 'Unknown', '']:
            extracted_location = self._extract_location_from_text(
                cleaned_data.get('description', '') + ' ' + cleaned_data.get('terms_conditions', '')
            )
            if extracted_location:
                cleaned_data['location'] = extracted_location
                self.enhancement_stats['location_extracted'] += 1
            else:
                cleaned_data['location'] = 'Hà Nội'  # Default fallback
        
        # Detect business type
        cleaned_data['business_type'] = self._detect_business_type(
            cleaned_data.get('voucher_name', ''),
            cleaned_data.get('description', ''),
            cleaned_data.get('category', '')
        )
        self.enhancement_stats['business_type_detected'] += 1
        
        # Analyze service information
        cleaned_data['service_info'] = self._analyze_service_info(
            cleaned_data.get('description', ''),
            cleaned_data.get('terms_conditions', ''),
            cleaned_data.get('voucher_name', '')
        )
        self.enhancement_stats['service_info_analyzed'] += 1
        
        # Extract and normalize price information
        cleaned_data['price_info'] = self._extract_price_info(
            cleaned_data.get('price', ''),
            cleaned_data.get('voucher_name', '')
        )
        
        # Clean and extract keywords
        cleaned_data['keywords'] = self._extract_keywords(
            cleaned_data.get('voucher_name', '') + ' ' + 
            cleaned_data.get('description', '') + ' ' +
            cleaned_data.get('tags', '')
        )
        
        self.cleaned_count += 1
        return cleaned_data
    
    def _handle_nan_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle NaN and empty values"""
        for key, value in data.items():
            if value is None or str(value).lower() in ['nan', 'none', 'null']:
                data[key] = ''
            elif isinstance(value, str):
                data[key] = value.strip()
        
        return data
    
    def _extract_location_from_text(self, text: str) -> Optional[str]:
        """Extract location from text description"""
        if not text or text == 'nan':
            return None
        
        # Vietnamese cities and areas
        locations = {
            'hà nội': 'Hà Nội',
            'hồ chí minh': 'Hồ Chí Minh', 
            'sài gòn': 'Hồ Chí Minh',
            'hcm': 'Hồ Chí Minh',
            'đà nẵng': 'Đà Nẵng',
            'hải phòng': 'Hải Phòng',
            'cần thơ': 'Cần Thơ',
            'nha trang': 'Nha Trang',
            'huế': 'Huế',
            'đà lạt': 'Đà Lạt',
            'vũng tàu': 'Vũng Tàu',
            'quy nhon': 'Quy Nhon',
            'vinh': 'Vinh',
            'hạ long': 'Hạ Long'
        }
        
        text_lower = text.lower()
        
        # Direct location matching
        for location_key, location_value in locations.items():
            if location_key in text_lower:
                return location_value
        
        # Pattern-based extraction
        location_patterns = [
            r'tại\s+([^,\s]+(?:\s+[^,\s]+)*)',
            r'ở\s+([^,\s]+(?:\s+[^,\s]+)*)',
            r'quận\s+(\d+)',
            r'quận\s+([^,\s]+)',
            r'phường\s+([^,\s]+)',
            r'địa chỉ[:\s]+([^,\n]+)',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                potential_location = matches[0].strip()
                # Try to normalize
                for loc_key, loc_val in locations.items():
                    if loc_key in potential_location or potential_location in loc_key:
                        return loc_val
        
        return None
    
    def _detect_business_type(self, name: str, description: str, category: str = '') -> str:
        """Detect business type from multiple sources"""
        text = f"{name} {description} {category}".lower()
        
        # Enhanced business type detection
        business_patterns = {
            'Restaurant': [
                'buffet', 'nhà hàng', 'quán ăn', 'restaurant', 'food', 'café', 'coffee', 
                'bistro', 'bar', 'pub', 'ăn uống', 'thức ăn', 'món ăn', 'bữa ăn',
                'dimsum', 'lẩu', 'nướng', 'phở', 'bún', 'cơm'
            ],
            'Hotel': [
                'khách sạn', 'hotel', 'resort', 'homestay', 'villa', 'nghỉ dưỡng',
                'accommodation', 'stay', 'lodge', 'motel', 'hostel'
            ],
            'Beauty': [
                'spa', 'massage', 'làm đẹp', 'beauty', 'salon', 'nail', 'tóc',
                'wellness', 'thư giãn', 'chăm sóc', 'skincare', 'facial'
            ],
            'Shopping': [
                'mua sắm', 'shopping', 'mall', 'siêu thị', 'cửa hàng', 'store',
                'shop', 'market', 'plaza', 'outlet', 'fashion', 'thời trang'
            ],
            'Entertainment': [
                'giải trí', 'vui chơi', 'entertainment', 'game', 'cinema', 'rạp phim',
                'karaoke', 'bowling', 'gym', 'thể thao', 'fitness'
            ],
            'Travel': [
                'du lịch', 'travel', 'tour', 'vé máy bay', 'flight', 'xe khách',
                'taxi', 'grab', 'transportation', 'vận chuyển'
            ],
            'Health': [
                'sức khỏe', 'health', 'y tế', 'medical', 'bệnh viện', 'phòng khám',
                'doctor', 'bác sĩ', 'thuốc', 'pharmacy'
            ]
        }
        
        for business_type, keywords in business_patterns.items():
            if any(keyword in text for keyword in keywords):
                return business_type
        
        return 'Other'
    
    def _analyze_service_info(self, description: str, terms: str, name: str) -> Dict[str, Any]:
        """Analyze service information from text"""
        text = f"{description} {terms} {name}".lower()
        
        service_info = {
            'has_kids_area': any(keyword in text for keyword in [
                'trẻ em', 'children', 'kids', 'khu vui chơi', 'playground', 
                'gia đình', 'family', 'trẻ nhỏ', 'bé', 'em bé'
            ]),
            'is_family_friendly': any(keyword in text for keyword in [
                'gia đình', 'family', 'trẻ nhỏ', 'suitable for family', 
                'phù hợp gia đình', 'cả nhà'
            ]),
            'has_parking': any(keyword in text for keyword in [
                'đỗ xe', 'parking', 'bãi xe', 'chỗ đậu xe', 'free parking'
            ]),
            'has_wifi': any(keyword in text for keyword in [
                'wifi', 'internet', 'mạng', 'free wifi', 'miễn phí wifi'
            ]),
            'outdoor_seating': any(keyword in text for keyword in [
                'ngoài trời', 'outdoor', 'sân vườn', 'terrace', 'ban công'
            ]),
            'air_conditioned': any(keyword in text for keyword in [
                'máy lạnh', 'điều hòa', 'air conditioning', 'ac'
            ]),
            'delivery_available': any(keyword in text for keyword in [
                'giao hàng', 'delivery', 'ship', 'đặt hàng', 'takeaway'
            ]),
            'reservation_required': any(keyword in text for keyword in [
                'đặt bàn', 'reservation', 'book', 'đặt trước', 'appointment'
            ])
        }
        
        return service_info
    
    def _extract_price_info(self, price_text: str, voucher_name: str) -> Dict[str, Any]:
        """Extract and normalize price information"""
        price_info = {
            'original_price': 0,
            'discount_amount': 0,
            'discount_percentage': 0,
            'final_price': 0,
            'price_range': 'Budget',
            'currency': 'VND'
        }
        
        # Combine price text and voucher name for better extraction
        text = f"{price_text} {voucher_name}".lower()
        
        # Extract numbers from text
        numbers = re.findall(r'[\d,]+', text.replace('.', ','))
        if numbers:
            # Convert to integers
            amounts = []
            for num in numbers:
                try:
                    amount = int(num.replace(',', ''))
                    amounts.append(amount)
                except:
                    continue
            
            if amounts:
                # Use the largest amount as reference
                max_amount = max(amounts)
                price_info['original_price'] = max_amount
                
                # Determine price range
                if max_amount <= 100000:
                    price_info['price_range'] = 'Budget'
                elif max_amount <= 500000:
                    price_info['price_range'] = 'Mid-range'
                elif max_amount <= 1000000:
                    price_info['price_range'] = 'Premium'
                else:
                    price_info['price_range'] = 'Luxury'
        
        # Extract percentage discount
        percentage_match = re.findall(r'(\d+)%', text)
        if percentage_match:
            price_info['discount_percentage'] = int(percentage_match[0])
        
        return price_info
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        if not text or text == 'nan':
            return []
        
        # Vietnamese stop words
        stop_words = {
            'tôi', 'tại', 'ở', 'trong', 'có', 'là', 'và', 'với', 'cho', 'của', 
            'một', 'các', 'này', 'đó', 'được', 'sẽ', 'đã', 'từ', 'về', 'như',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'giảm', 'voucher', 'vnd', 'đồng', 'khi', 'mua', 'sử', 'dụng'
        }
        
        # Extract words and clean
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = []
        
        for word in words:
            if (len(word) > 2 and 
                word not in stop_words and 
                not word.isdigit() and
                word not in keywords):
                keywords.append(word)
        
        return keywords[:15]  # Limit to top 15 keywords
    
    def get_cleaning_summary(self) -> Dict[str, Any]:
        """Get summary of cleaning process"""
        return {
            'cleaned_vouchers': self.cleaned_count,
            'enhancement_stats': self.enhancement_stats
        }
