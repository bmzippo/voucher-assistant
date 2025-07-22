#!/usr/bin/env python3
"""
Quick test script to verify fixed column mapping
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from data_processing.voucher_loader import VoucherDataLoader

def test_fixed_mapping():
    """
    Test the fixed mapping for importvoucher.xlsx
    """
    print("Testing Fixed Column Mapping")
    print("=" * 40)
    
    loader = VoucherDataLoader()
    
    # Test with importvoucher.xlsx
    import_file = "/Users/1-tiennv-m/1MG/Projects/LLM/data/importvoucher.xlsx"
    
    print(f"Loading {import_file}...")
    vouchers = loader.load_import_voucher_file(import_file, has_header=True)
    
    if vouchers:
        # Check the first voucher (index 33 corresponds to the one we checked)
        test_voucher = vouchers[33]
        print(f"\nVoucher {test_voucher['voucher_id']}:")
        print(f"Name: {test_voucher['voucher_name']}")
        print(f"Description: {test_voucher['description'][:100]}...")
        print(f"Terms: {test_voucher['terms_conditions'][:100]}...")
        print(f"Usage: {test_voucher['usage'][:100]}...")
        print(f"Merchant: {test_voucher['merchant']}")
        print(f"Price: {test_voucher['price']}")
        print()
        
        print("Generated Content:")
        print("-" * 30)
        print(test_voucher['content'])
        print("-" * 30)
        
        # Check if content contains description
        has_description = test_voucher['description'] in test_voucher['content']
        print(f"\n✅ Content contains description: {has_description}")
        
        if has_description:
            print("🎉 SUCCESS: Description is now included in content!")
        else:
            print("❌ ISSUE: Description still missing from content")
            
    else:
        print("❌ No vouchers loaded")

if __name__ == "__main__":
    test_fixed_mapping()
