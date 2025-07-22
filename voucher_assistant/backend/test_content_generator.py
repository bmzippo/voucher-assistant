#!/usr/bin/env python3
"""
Test script for VoucherContentGenerator
Kiểm tra xem content generator có hoạt động đúng như mong đợi không
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from voucher_content_generator import VoucherContentGenerator

def test_content_generator():
    """
    Test VoucherContentGenerator với sample data
    """
    print("Testing VoucherContentGenerator")
    print("=" * 50)
    
    generator = VoucherContentGenerator()
    
    # Sample voucher data tương tự như trong database
    sample_vouchers = [
        {
            'voucher_id': 'test_1',
            'voucher_name': 'Buffet Lẩu Nướng Hàn Quốc',
            'merchant': 'Seoul Garden Restaurant',
            'price': '299000',
            'unit': 'VND',
            'description': 'Buffet lẩu nướng Hàn Quốc cao cấp với hơn 100 món ăn đặc sắc',
            'terms_conditions': 'Áp dụng từ thứ 2 đến thứ 6, không áp dụng ngày lễ tết',
            'usage': 'Xuất trình voucher tại quầy thu ngân, không hoàn tiền',
            'tags': 'buffet, lẩu nướng, hàn quốc, gia đình',
            'category': 'Nhà hàng',
            'location': 'Hà Nội'
        },
        {
            'voucher_id': 'test_2',
            'voucher_name': 'Combo Pizza Ý cho 4 người',
            'merchant': 'Pizza Hut',
            'price': '450',
            'unit': 'K',
            'description': 'Combo pizza Ý thơm ngon với 2 pizza size M và nước uống',
            'terms_conditions': 'Sử dụng trong 30 ngày từ ngày mua',
            'usage': 'Đặt bàn trước và thông báo sử dụng voucher',
            'tags': 'pizza, ý, combo, gia đình',
            'location': 'Hồ Chí Minh'
        },
        {
            'voucher_id': 'test_3',
            'voucher_name': 'Massage body thư giãn 90 phút',
            'merchant': 'Zen Spa',
            'description': 'Massage body thư giãn toàn thân với tinh dầu thảo dược',
            'location': 'Đà Nẵng',
            'category': 'Spa & Làm đẹp'
        }
    ]
    
    print(f"Testing với {len(sample_vouchers)} voucher samples...\n")
    
    for i, voucher in enumerate(sample_vouchers, 1):
        print(f"VOUCHER {i}: {voucher['voucher_name']}")
        print("-" * 40)
        
        # Generate content
        content = generator.generate_voucher_content(voucher)
        
        print("Generated Content:")
        print(content)
        print()
        
        # Test update method
        updated_voucher = generator.update_voucher_with_generated_content(voucher)
        print(f"Content length: {len(updated_voucher['content'])} characters")
        print(f"Content field added: {'content' in updated_voucher}")
        print()
        print("=" * 50)
        print()

def test_format_price():
    """
    Test helper function format_voucher_value
    """
    from voucher_content_generator import format_voucher_value
    
    print("Testing format_voucher_value function")
    print("=" * 40)
    
    test_cases = [
        ("299000", "VND"),
        ("450", "K"),
        ("50.5", "USD"),
        ("100,000", "VND"),
        ("invalid", "VND")
    ]
    
    for price, currency in test_cases:
        formatted = format_voucher_value(price, currency)
        print(f"Input: {price} {currency} -> Output: {formatted}")
    
    print()

if __name__ == "__main__":
    test_content_generator()
    test_format_price()
