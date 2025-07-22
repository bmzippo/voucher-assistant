#!/usr/bin/env python3

"""
Quick test to check if content field is now populated correctly
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from data_processing.voucher_loader import VoucherDataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_content_field():
    """Test if content field is populated for temp voucher file"""
    
    data_dir = "/Users/1-tiennv-m/1MG/Projects/LLM/data"
    loader = VoucherDataLoader()
    
    # Test temp voucher file specifically
    temp_file = Path(data_dir) / "temp voucher.xlsx"
    if temp_file.exists():
        print(f"Testing temp voucher file: {temp_file}")
        
        vouchers = loader.load_temp_voucher_file(str(temp_file))
        
        if vouchers:
            # Check first 3 vouchers
            for i, voucher in enumerate(vouchers[:3]):
                print(f"\n--- Voucher {i+1} ---")
                print(f"ID: {voucher['voucher_id']}")
                print(f"Name: {voucher['voucher_name']}")
                print(f"Description: {voucher['description'][:100]}..." if len(voucher['description']) > 100 else f"Description: {voucher['description']}")
                print(f"Terms: {voucher['terms_conditions'][:100]}..." if len(voucher['terms_conditions']) > 100 else f"Terms: {voucher['terms_conditions']}")
                print(f"Usage: {voucher['usage'][:100]}..." if len(voucher['usage']) > 100 else f"Usage: {voucher['usage']}")
                print(f"Content: {voucher['content'][:200]}..." if len(voucher['content']) > 200 else f"Content: {voucher['content']}")
                print(f"Content length: {len(voucher['content'])}")
        else:
            print("No vouchers loaded!")
    else:
        print(f"Temp voucher file not found: {temp_file}")

if __name__ == "__main__":
    asyncio.run(test_content_field())
