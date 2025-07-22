#!/usr/bin/env python3
"""
Complete Test script for voucher data processing pipeline (Safe Version with Vector Store)
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from data_processing.processor_safe import VoucherDataProcessorSafe, process_voucher_data_safe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_vector_store_operations():
    """Test vector store operations"""
    logger.info("🧪 Testing Vector Store Operations")
    
    # Initialize processor
    processor = VoucherDataProcessorSafe()
    
    # Test adding a sample voucher
    sample_voucher = {
        "id": "test_001",
        "name": "Voucher test ăn uống Hà Nội",
        "desc": "Giảm 50% cho tất cả món ăn tại các nhà hàng ở Hà Nội",
        "usage": "Đặt bàn trước và xuất trình voucher khi thanh toán",
        "termofuse": "Áp dụng từ thứ 2 đến thứ 6, không áp dụng ngày lễ",
        "location": "Hà Nội",
        "price": 100000,
        "tags": "ăn uống, giảm giá, gia đình",
        "merchant": "TestMerchant"
    }
    
    # Test adding voucher
    success = processor.vector_store.add_voucher(sample_voucher)
    if success:
        logger.info("✅ Successfully added test voucher to vector store")
    else:
        logger.error("❌ Failed to add test voucher")
    
    # Test searching
    search_queries = [
        "ăn uống Hà Nội",
        "nhà hàng giảm giá",
        "voucher gia đình",
        "món ăn ngon"
    ]
    
    for query in search_queries:
        results = await processor.search_vouchers(query, size=3)
        logger.info(f"🔍 Search '{query}': Found {len(results)} results")
        for i, result in enumerate(results, 1):
            logger.info(f"   {i}. {result.get('voucher_name')} (score: {result.get('score', 0):.2f})")

async def main():
    """Main test function"""
    print("Starting Complete Voucher Data Processing Pipeline Test (Safe Version)")
    print("=" * 80)
    
    # Get data directory
    current_dir = Path(__file__).parent.parent.parent
    data_dir = current_dir / "data"
    
    print(f"Using data directory: {data_dir}")
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    # Check for Excel files
    excel_files = list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*.xls"))
    if excel_files:
        print(f"Found Excel files in {data_dir}:")
        for file in excel_files:
            print(f"  - {file.name}")
    else:
        print(f"⚠️  No Excel files found in {data_dir}")
        return
    
    print(f"\nProcessing {len(excel_files)} files...")
    print("-" * 50)
    
    try:
        # Test vector store operations first
        await test_vector_store_operations()
        print("-" * 50)
        
        # Process voucher data
        print("Calling process_voucher_data_safe...")
        results = await process_voucher_data_safe(data_dir)
        
        print("\n" + "=" * 80)
        print("✅ PROCESSING COMPLETED!")
        print("=" * 80)
        
        # Display results
        print(f"\n📊 Overall Summary:")
        print(f"  - Total files processed: {len(results['file_results'])}")
        print(f"  - Total vouchers processed: {results['total_processed']}")
        print(f"  - Successfully indexed: {results['successful_indexed']}")
        print(f"  - Total errors: {len(results['errors'])}")
        
        # File-by-file results
        print(f"\n📁 File-by-file Results:")
        for filename, file_result in results['file_results'].items():
            print(f"\n🗂️  {filename}:")
            if file_result['status'] == 'success':
                print(f"    ✅ Status: {file_result['status']}")
                print(f"    📊 Total vouchers: {file_result['total_vouchers']}")
                print(f"    ✅ Valid vouchers: {file_result['valid_vouchers']}")
                print(f"    💾 Successfully indexed: {file_result['successful_indexed']}")
                if file_result['errors']:
                    print(f"    ⚠️  Errors: {len(file_result['errors'])}")
                    for error in file_result['errors'][:3]:  # Show first 3 errors
                        print(f"       - {error}")
            else:
                print(f"    ❌ Status: {file_result['status']}")
                print(f"    ❌ Error: {file_result.get('error', 'Unknown error')}")
        
        # Overall errors
        if results['errors']:
            print(f"\n⚠️  Overall Errors ({len(results['errors'])}):")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
        
        # Test search functionality
        print(f"\n🔍 Testing Search Functionality:")
        processor = VoucherDataProcessorSafe()
        
        test_queries = [
            "ăn uống",
            "du lịch",
            "Hà Nội",
            "giảm giá",
            "massage spa"
        ]
        
        for query in test_queries:
            search_results = await processor.search_vouchers(query, size=2)
            print(f"\n   Query: '{query}' -> {len(search_results)} results")
            for i, result in enumerate(search_results, 1):
                print(f"     {i}. {result.get('voucher_name', 'Unknown')} (score: {result.get('score', 0):.2f})")
        
        print(f"\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
