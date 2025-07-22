#!/usr/bin/env python3

"""
Test Elasticsearch indexing with content field for few vouchers
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from data_processing.voucher_loader import VoucherDataLoader
from data_processing.data_cleaner import VoucherDataCleaner
from advanced_vector_store import AdvancedVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_es_content_indexing():
    """Test indexing only a few vouchers to ES and check content field"""
    
    print("🧪 Testing ES Content Indexing")
    print("="*50)
    
    data_dir = "/Users/1-tiennv-m/1MG/Projects/LLM/data"
    
    # 1. Load only a few vouchers
    loader = VoucherDataLoader()
    temp_file = Path(data_dir) / "temp voucher.xlsx"
    
    vouchers = loader.load_temp_voucher_file(str(temp_file))
    print(f"📊 Loaded {len(vouchers)} vouchers from temp file")
    
    # Take only first 2 vouchers for testing
    test_vouchers = vouchers[:2]
    print(f"🔍 Testing with {len(test_vouchers)} vouchers")
    
    # 2. Clean data
    cleaner = VoucherDataCleaner()
    cleaned_vouchers = []
    for voucher in test_vouchers:
        cleaned_voucher = cleaner.clean_voucher_data(voucher)
        cleaned_vouchers.append(cleaned_voucher)
    print(f"🧹 Cleaned {len(cleaned_vouchers)} vouchers")
    
    # 3. Initialize vector store
    vector_store = AdvancedVectorStore()
    print("🤖 Initialized AdvancedVectorStore")
    
    # 4. Index vouchers one by one and check content
    for i, voucher in enumerate(cleaned_vouchers):
        print(f"\n--- Indexing Voucher {i+1}: {voucher['voucher_id']} ---")
        print(f"Name: {voucher['voucher_name']}")
        print(f"Content preview: {voucher['content'][:150]}...")
        
        try:
            success = await vector_store.index_voucher_advanced(voucher)
            if success:
                print(f"✅ Successfully indexed {voucher['voucher_id']}")
                
                # Check if document was indexed with content
                doc = vector_store.es.get(
                    index="voucher_knowledge",
                    id=voucher['voucher_id'],
                    ignore=[404]
                )
                
                if doc['found']:
                    source = doc['_source']
                    content_in_es = source.get('content', '')
                    print(f"📄 Content in ES (length {len(content_in_es)}): {content_in_es[:100]}...")
                    
                    if not content_in_es.strip():
                        print("❌ WARNING: Content field is empty in ES!")
                    else:
                        print("✅ Content field populated in ES")
                else:
                    print("❌ Document not found in ES")
            else:
                print(f"❌ Failed to index {voucher['voucher_id']}")
                
        except Exception as e:
            print(f"❌ Error indexing {voucher['voucher_id']}: {e}")
    
    print(f"\n🎉 Content indexing test completed!")

if __name__ == "__main__":
    asyncio.run(test_es_content_indexing())
