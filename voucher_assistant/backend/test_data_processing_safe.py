#!/usr/bin/env python3
"""
Test script for voucher data processing pipeline (Safe Version - Without Model Loading)
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from data_processing.processor import VoucherDataProcessor
from advanced_vector_store import AdvancedVectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SafeVoucherDataProcessor:
    """Safe version of VoucherDataProcessor for testing without model loading"""
    
    def __init__(self, elasticsearch_url="http://localhost:9200"):
        self.elasticsearch_url = elasticsearch_url
        logger.info(f"🔧 Safe Voucher Data Processor initialized (Mock mode)")
    
    async def process_excel_file(self, file_path):
        """Mock process Excel file"""
        import pandas as pd
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            logger.info(f"📊 Successfully read Excel file: {file_path}")
            logger.info(f"   - Rows: {len(df)}")
            logger.info(f"   - Columns: {list(df.columns)}")
            
            # Mock processing results
            results = {
                'file_path': str(file_path),
                'total_rows': len(df),
                'columns': list(df.columns),
                'processed_vouchers': len(df),
                'status': 'success'
            }
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {str(e)}")
            return {
                'file_path': str(file_path),
                'status': 'error',
                'error': str(e)
            }

async def process_voucher_data_safe(data_dir):
    """Safe version of process_voucher_data without model loading"""
    
    # Initialize processor (safe mode)
    processor = SafeVoucherDataProcessor()
    
    # Find Excel files
    data_path = Path(data_dir)
    excel_files = list(data_path.glob("*.xlsx")) + list(data_path.glob("*.xls"))
    
    if not excel_files:
        logger.warning(f"⚠️  No Excel files found in {data_dir}")
        return []
    
    logger.info(f"📁 Found {len(excel_files)} Excel files:")
    for file in excel_files:
        logger.info(f"   - {file.name}")
    
    # Process each file
    results = []
    for file_path in excel_files:
        logger.info(f"\n🔄 Processing: {file_path.name}")
        result = await processor.process_excel_file(file_path)
        results.append(result)
    
    return results

async def main():
    """Main test function"""
    print("Starting Voucher Data Processing Pipeline (Safe Mode)")
    print("=" * 60)
    
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
    print("-" * 30)
    
    try:
        print("Calling process_voucher_data_safe...")
        results = await process_voucher_data_safe(data_dir)
        
        print("\n" + "=" * 60)
        print("✅ PROCESSING COMPLETED!")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"\nFile {i}: {Path(result['file_path']).name}")
            print(f"  Status: {result['status']}")
            if result['status'] == 'success':
                print(f"  Total rows: {result['total_rows']}")
                print(f"  Columns: {result['columns']}")
                print(f"  Processed vouchers: {result['processed_vouchers']}")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n📊 Summary:")
        print(f"  - Total files processed: {len(results)}")
        print(f"  - Successful: {sum(1 for r in results if r['status'] == 'success')}")
        print(f"  - Failed: {sum(1 for r in results if r['status'] == 'error')}")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
