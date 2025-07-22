"""
Voucher Content Generator
Module để tạo content cho voucher theo chuẩn format để index vào ES
Dựa trên logic từ C# function voucherChunk
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VoucherContentGenerator:
    """
    Class để tạo content cho voucher theo format chuẩn
    Tương tự như function voucherChunk trong C#
    """
    
    def __init__(self):
        pass
    
    def generate_voucher_content(self, voucher: Dict[str, Any]) -> str:
        """
        Tạo content cho voucher dựa trên các field available
        
        Args:
            voucher: Dictionary chứa thông tin voucher
            
        Returns:
            str: Content đã được format để index vào ES
        """
        content_parts = []
        
        # 1. Voucher Name 
        voucher_name = voucher.get('voucher_name', '').strip()
        if voucher_name and voucher_name != 'nan':
            content_parts.append(voucher_name)
        
        # 2. Merchant 
        merchant = voucher.get('merchant', '').strip()
        if merchant and merchant != 'nan':
            content_parts.append(f"- Merchant: {merchant}")
        
        # 3. Price và Currency 
        price = voucher.get('price', '').strip()
        unit = voucher.get('unit', '').strip()
        if price and price != 'nan':
            if unit and unit != 'nan':
                price_text = f"- Giá đổi voucher: {price} {unit}"
            else:
                price_text = f"- Giá đổi voucher: {price}"
            content_parts.append(price_text)
        
        # 4. Description 
        description = voucher.get('description', '').strip()
        if description and description != 'nan':
            content_parts.append(description)
        
        # 5. Terms and Conditions
        terms = voucher.get('terms_conditions', '').strip()
        if terms and terms != 'nan':
            content_parts.append(f"- Điều kiện sử dụng: {terms}")
        
        # 6. Usage
        usage = voucher.get('usage', '').strip()
        if usage and usage != 'nan':
            content_parts.append(f"- Cách sử dụng: {usage}")
        
        # 7. Tags (tương tự AggregatedTags trong C#)
        tags = voucher.get('tags', '').strip()
        if tags and tags != 'nan':
            content_parts.append(f"- Tags: {tags}")
        
        # 8. Category
        category = voucher.get('category', '').strip()
        if category and category != 'nan':
            content_parts.append(f"- Danh mục: {category}")
        
        # 9. Location (tương tự AggregatedLocations trong C#)
        location = voucher.get('location', '').strip()
        if location and location != 'nan':
            content_parts.append(f"- Địa chỉ nhà hàng cung cấp dịch vụ có thể áp dụng voucher: {location}")
        
        # Join tất cả parts với newline
        content = '\n'.join(content_parts)
        
        logger.debug(f"Generated content for voucher {voucher.get('voucher_id', 'unknown')}: {len(content)} characters")
        
        return content
    
    def update_voucher_with_generated_content(self, voucher: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cập nhật voucher với content được generate
        
        Args:
            voucher: Dictionary chứa thông tin voucher
            
        Returns:
            Dict: Voucher với field content đã được cập nhật
        """
        voucher_copy = voucher.copy()
        generated_content = self.generate_voucher_content(voucher)
        voucher_copy['content'] = generated_content
        
        return voucher_copy

def format_voucher_value(price: str, currency: str = "VND") -> str:
    """
    Helper function để format giá voucher (tương tự VoucherHelper.FormatVoucherValue trong C#)
    
    Args:
        price: Giá voucher
        currency: Đơn vị tiền tệ
        
    Returns:
        str: Giá đã được format
    """
    try:
        # Thử convert sang số để format
        if price.replace('.', '').replace(',', '').isdigit():
            price_num = float(price.replace(',', ''))
            if currency.upper() == "VND":
                return f"{price_num:,.0f} VND"
            else:
                return f"{price_num:,.2f} {currency}"
        else:
            return f"{price} {currency}"
    except:
        return f"{price} {currency}"
