#!/usr/bin/env python3
"""
Test script for the new data_processing module
Loads and processes all voucher files including temp voucher.xlsx, importvoucher.xlsx, importvoucher2.xlsx
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from data_processing import process_voucher_data

async def main():
    """
    Main function to test data processing pipeline
    """
    print("Starting Voucher Data Processing Pipeline")
    print("="*50)
    
    try:
        # Set data directory
        data_dir = "/Users/1-tiennv-m/1MG/Projects/LLM/data"
        print(f"Using data directory: {data_dir}")
        
        # Check if data directory exists
        if not os.path.exists(data_dir):
            print(f"Error: Data directory {data_dir} does not exist")
            return
        
        # List available Excel files
        data_path = Path(data_dir)
        excel_files = list(data_path.glob("*.xlsx"))
        
        print(f"Found Excel files in {data_dir}:")
        for file in excel_files:
            print(f"  - {file.name}")
        
        if not excel_files:
            print("No Excel files found to process")
            return
        
        print(f"\nProcessing {len(excel_files)} files...")
        print("-" * 30)
        
        # Run the processing pipeline
        print("Calling process_voucher_data...")
        results = await process_voucher_data(data_dir)
        print("process_voucher_data completed!")
        
        # Display results
        print("\nPROCESSING RESULTS:")
        print("="*30)
        print(f"Total processed: {results['total_processed']}")
        print(f"Successfully indexed: {results['successful_indexed']}")
        print(f"Errors encountered: {len(results['errors'])}")
        
        # File-specific results
        print("\nFile Processing Results:")
        for filename, file_result in results.get('file_results', {}).items():
            status = file_result['status']
            count = file_result['loaded_count']
            print(f"  {filename}: {status} ({count} vouchers)")
            if status == 'error':
                print(f"    Error: {file_result.get('error', 'Unknown error')}")
        
        # Cleaning summary
        if 'cleaning_summary' in results:
            cleaning = results['cleaning_summary']
            print(f"\nData Cleaning Summary:")
            print(f"  Vouchers cleaned: {cleaning['cleaned_vouchers']}")
            print(f"  Locations extracted: {cleaning['enhancement_stats']['location_extracted']}")
            print(f"  Business types detected: {cleaning['enhancement_stats']['business_type_detected']}")
        
        # Verification results
        if 'verification' in results:
            verification = results['verification']
            print(f"\nIndexing Verification:")
            print(f"  Basic search results: {verification['basic_search_count']}")
            print(f"  Advanced search results: {verification['advanced_search_count']}")
            print(f"  Indexing verified: {verification['indexing_verified']}")
        
        # Show any errors
        if results['errors']:
            print(f"\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")
        
        print("\n" + "="*50)
        if results['successful_indexed'] > 0:
            print("✅ Processing completed successfully!")
            print(f"✅ {results['successful_indexed']} vouchers are now searchable")
        else:
            print("❌ Processing completed with issues")
            print("❌ No vouchers were successfully indexed")
            
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
